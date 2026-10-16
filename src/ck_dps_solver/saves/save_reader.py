"""Read the equipment a player owns from Core Keeper save files.

Save files live in %USERPROFILE%/AppData/LocalLow/Pugstorm/Core Keeper/Steam/<steam id>/:
  saves/<n>.json        a character: equipped and inventory items
  worlds/<n>.world.gzip a world: chest contents (Brotli-compressed despite the extension; see saves/world_file.py)

Each item slot is (objectID, amount, variation). For equipment, `variation` is the item's upgrade level
(0 = never upgraded, i.e. its base level) and `amount` is its current durability.

Worlds also contain generated chests with loot (dungeons, biome chests), so world items are limited to
chests within a radius of the player (or of a chosen center).
"""
from dataclasses import dataclass
import json
import math

from ck_dps_solver.model.item_stats import has_durability, wiki_data
from ck_dps_solver.model.pets import learned_talents_from_aux, species_for_talents
from ck_dps_solver.saves import world_file

MAX_LEVEL = 20


@dataclass
class OwnedItem:
    internal_id: str
    name: str
    level: int       # Upgrade level from the save; 0 means the item's base level
    reinforced: bool # Guessed from durability above the item's normal maximum
    source: str      # 'player', or the chest it's in, e.g. 'Iron Chest at (12, -40)'
    talents: list = None # Pets: learned talent ids, when the save has them (characters' inventories do; chests don't)


def base_level(internal_id):
    """Lowest level the wiki lists stats for (an item's level before any upgrades)"""
    record = wiki_data()['equipment'][internal_id]
    levels = [int(k) for c in (record.get('equipped') or {}).get('conditions', []) if isinstance(c['value'], dict) for k in c['value']]
    for key in ('meleeDamage', 'rangeDamage'):
        if isinstance(record.get(key), dict): levels += [int(k) for k in record[key]]
    return min(levels) if levels else record.get('level', 1)


def owned_item(internal_id, amount, variation, source):
    record = wiki_data()['equipment'][internal_id]
    level = variation if variation > 0 else base_level(internal_id)
    durability = record.get('durability')
    reinforced = has_durability(record) and isinstance(durability, (int, float)) and amount > durability
    return OwnedItem(internal_id, record.get('name', internal_id), level, reinforced, source)


# The wiki's skill module (game 1.1.0.1) has the experience curves from before update 1.3.0.1 (21 Sep 2026), which
# "reduced the total experience required for maxing the Melee, Ranged, and Magic skill trees" and "adjusted the
# experience curves so skill points are earned faster at early levels" (official patch notes). The new curves,
# (multiplier, base), are fitted to levels read in game on five characters (Gardening 11 at 115 xp, 53 at 1138, 71 at
# 2220; Magic 8 at 271, 37 at 2037; Summoning 12 at 487, 40 at 3327; Melee 34 at 1804; Range 61 at 5093; the same
# readings are in tests/test_saves.py). Also no character may have more talent points than its
# level gives. Melee, Ranged and Magic share one curve, as before the update (one curve fits all their readings; its
# level-100 total is ~17,800, down from 20,001). Each value is the middle of the curves that fit.
SHARED_COMBAT_CURVE = (1.0296, 30.2)
CURVE_FIXES = {'Melee': SHARED_COMBAT_CURVE, 'Range': SHARED_COMBAT_CURVE, 'Magic': SHARED_COMBAT_CURVE,
               'Gardening': (1.0325, 8.1), 'Summoning': (1.0457, 29.8)}


def skill_level(experience, skill):
    """Skill level from total experience, using the skill's experience curve from the wiki data (with CURVE_FIXES)"""
    name = next((n for n, s in wiki_data()['skills'].items() if s is skill or s.get('id') == skill.get('id')), None)
    mul, base = CURVE_FIXES.get(name, (skill['mulFactor'], skill['baseFactor']))
    level = math.floor(math.log(1 - experience * (1 - mul) / base) / math.log(mul) + 1e-9)
    return max(0, min(int(level), skill['maxLevel']))


def read_character_stats(path, skill_names):
    """(skill levels, talent points) of a character, for the solver's skills (skill_names).
    Talent points are in talent tree order, 8 per skill."""
    save = load_player(path)
    by_id = {info['id']: name for name, info in wiki_data()['skills'].items()}
    skills = wiki_data()['skills']
    levels = {name: 0 for name in skill_names}
    for entry in save.get('skills', []):
        name = by_id.get(entry['skillID'])
        if name in levels:
            levels[name] = skill_level(entry['value'], skills[name])
    talents = {name: [0] * 8 for name in skill_names}
    for entry in save.get('skillTalentTreeDatas', []):
        name = by_id.get(entry['skillTreeID'])
        if name in talents:
            points = list(entry.get('points', []))[:8]
            talents[name] = points + [0] * (8 - len(points))
    return levels, talents


def load_player(path):
    with open(path, encoding='utf-8-sig') as f:
        return json.load(f)


def read_player(path):
    """Equipment in a character's inventory and equipment slots"""
    save = load_player(path)
    equipment = wiki_data()['equipment']
    items = []
    aux = save.get('inventoryAuxData', [{}] * len(save['inventory']))
    for slot, internal_id, aux_data in zip(save['inventory'], save['inventoryObjectNames'], aux):
        if slot['objectID'] and internal_id in equipment and 0 <= slot['variation'] <= MAX_LEVEL:
            item = owned_item(internal_id, slot['amount'], slot['variation'], 'player')
            if equipment[internal_id].get('type') == 'Pet':
                item.talents = learned_talents_from_aux((aux_data or {}).get('data'))
            items.append(item)
    return items


# Chests you craft and place: everything in them counts as yours (any of your characters may have stored it). Every
# other chest (Ancient, biome, dungeon, Cultist, Locked and boss chests) is world loot: its items only count once the
# character has discovered them (picked one up at some point), so unopened loot isn't taken for owned gear.
STORAGE_CHESTS = {'InventoryChest', 'CopperChest', 'IronChest', 'ScarletChest', 'OctarineChest', 'GalaxiteChest', 'SolariteChest', 'ReluciteChest'}


def discovered_object_ids(player_path):
    """Object ids a character has discovered (from the save's discovered objects)"""
    if player_path is None:
        return None
    return {entry.get('objectID') for entry in load_player(player_path).get('discoveredObjects2', [])}


def _counts(chest_internal_id, object_id, discovered):
    """Whether an item in a chest counts as owned (see STORAGE_CHESTS)"""
    return chest_internal_id in STORAGE_CHESTS or discovered is None or object_id in discovered


def container_object_ids():
    objects = wiki_data()['objects']
    return {o['id'] for internal_id, o in objects.items() if 'Chest' in o.get('categories', []) or internal_id.endswith('Chest')}


def read_world(path, player_path=None, center=None, radius=None):
    """
    Equipment stored in a world's chests.
    center: (x, z) to measure distance from. Default: the player's position (found through player_path's
            inventory), else the Core at (0, 0). radius: only chests within this many tiles (None = all).
    Returns (items, center used).
    """
    world = world_file.read_world(path)
    objects = wiki_data()['objects']
    id_to_internal = {o['id']: internal_id for internal_id, o in objects.items()}
    if center is None and player_path is not None:
        center = world_file.player_position(world, [slot['objectID'] for slot in load_player(player_path)['inventory']])
    center = center if center is not None else (0.0, 0.0)
    discovered = discovered_object_ids(player_path)

    equipment = wiki_data()['equipment']
    # Pets keep their talents on separate entities; match them to pets by species (talent pool)
    talent_ids = {t['id'] for t in wiki_data()['pets']['talents'].values()}
    talents_by_species = {}
    for pairs in world_file.pet_talent_lists(world, talent_ids):
        learned = tuple(sorted(t for t, points in pairs if points > 0))
        for species in species_for_talents([t for t, _ in pairs]):
            talents_by_species.setdefault(species, set()).add(learned)
    items = []
    for container in world_file.containers(world, container_object_ids(), set(id_to_internal)):
        if radius is not None and math.hypot(container.x - center[0], container.z - center[1]) > radius:
            continue
        chest = objects[id_to_internal[container.object_id]]['name']
        chest_id = id_to_internal[container.object_id]
        for object_id, amount, variation in container.slots:
            internal_id = id_to_internal.get(object_id)
            if internal_id in equipment and 0 <= variation <= MAX_LEVEL and _counts(chest_id, object_id, discovered):
                source = f'{chest} at ({container.x:g}, {container.z:g})'
                if equipment[internal_id].get('type') == 'Pet':
                    # One copy per distinct set of learned talents found for this species (usually one)
                    for learned in sorted(talents_by_species.get(internal_id, {()})):
                        item = owned_item(internal_id, amount, variation, source)
                        item.talents = list(learned)
                        items.append(item)
                else:
                    items.append(owned_item(internal_id, amount, variation, source))
    return items, center


def read_owned(player_paths=(), world_paths=(), center=None, radius=None):
    """Equipment from characters and worlds. World chests are measured from the first character's position."""
    items = []
    for path in player_paths: items += read_player(path)
    for path in world_paths:
        world_items, _ = read_world(path, player_path=player_paths[0] if player_paths else None, center=center, radius=radius)
        items += world_items
    return items


def owned_consumables(player_paths=(), world_paths=(), center=None, radius=None):
    """{source key: amount} of the food and potions in characters' inventories and in worlds' chests (same chest radius
    and center as equipment), as utils.consumables keys"""
    from ck_dps_solver.model.consumables import owned_keys
    found = {}
    def add(internal_id, amount, variation):
        for key in owned_keys(internal_id, variation):
            found[key] = found.get(key, 0) + max(amount, 1)
    for path in player_paths:
        save = load_player(path)
        for slot, internal_id in zip(save['inventory'], save['inventoryObjectNames']):
            if slot['objectID']:
                add(internal_id, slot['amount'], slot['variation'])
    objects = wiki_data()['objects']
    id_to_internal = {o['id']: internal_id for internal_id, o in objects.items()}
    discovered = discovered_object_ids(player_paths[0]) if player_paths else None
    for path in world_paths:
        world = world_file.read_world(path)
        here = center
        if here is None and player_paths:
            here = world_file.player_position(world, [slot['objectID'] for slot in load_player(player_paths[0])['inventory']])
        here = here if here is not None else (0.0, 0.0)
        for container in world_file.containers(world, container_object_ids(), set(id_to_internal)):
            if radius is not None and math.hypot(container.x - here[0], container.z - here[1]) > radius:
                continue
            for object_id, amount, variation in container.slots:
                if object_id in id_to_internal and _counts(id_to_internal[container.object_id], object_id, discovered):
                    add(id_to_internal[object_id], amount, variation)
    return found


# Souls in a save's collectedSouls / disabledSoulPowers, by id, in the wiki's order (Azeos, Omoroth, Ra-Akar, Druidra,
# Crydra, Pyrdra; ids 1-3 also checked against boss drops in saves). The two with a setting:
SOUL_SETTINGS = {4: 'Druidra soul', 6: 'Pyrdra soul'}


def soul_settings(path):
    """{setting: on} for the souls with a setting: on when collected and not disabled"""
    save = load_player(path)
    active = set(save.get('collectedSouls', [])) - set(save.get('disabledSoulPowers', []))
    return {setting: soul in active for soul, setting in SOUL_SETTINGS.items()}


def permanent_health_foods():
    """[(condition, food name, max health)] for every food that gives max health for good (current versions)"""
    foods = []
    for record in wiki_data().get('consumables', {}).values():
        if '(old)' in record['name']:
            continue
        for condition in record['conditions']:
            info = wiki_data()['conditions'].get(condition['id'], {})
            if info.get('effect') == 'MaxHealthPermanent' and condition['id'] not in [f[0] for f in foods]:
                foods.append((condition['id'], record['name'], int(condition['value'])))
    return sorted(foods, key=lambda f: (-f[2], f[1]))


def permanent_health_food_ids():
    """{condition (see permanent_health_foods): the food's object id}, e.g. for where to get it"""
    found = {}
    for internal_id, record in wiki_data().get('consumables', {}).items():
        if '(old)' not in record['name']:
            for condition in record['conditions']:
                if wiki_data()['conditions'].get(condition['id'], {}).get('effect') == 'MaxHealthPermanent':
                    found.setdefault(condition['id'], internal_id)
    return found


def permanent_health_eaten(path):
    """Conditions (see permanent_health_foods) of the permanent max health foods a character has eaten. Saves from
    before the foods had their own conditions use one shared one; it's matched to a food by its value."""
    conditions = wiki_data()['conditions']
    by_number = {c['id']: name for name, c in conditions.items() if 'id' in c}
    foods = permanent_health_foods()
    eaten = set()
    for entry in load_player(path).get('conditionsList', []):
        name = by_number.get(entry.get('Id'))
        if any(name == f[0] for f in foods):
            eaten.add(name)
        elif name == 'IncreasedMaxHealthPermanent': # Old shared condition: Giant Mushroom (25) or Amber Larva (50)
            eaten |= {f[0] for f in foods if f[2] == entry.get('Value') and f[1] in ('Giant Mushroom', 'Amber Larva')}
    return eaten


def permanent_max_health(path):
    """Max health a character has from permanent foods (Giant Mushroom, Atlantean Worm Heart...), from its conditions"""
    conditions = wiki_data()['conditions']
    by_number = {c['id']: name for name, c in conditions.items() if 'id' in c}
    total = 0
    for entry in load_player(path).get('conditionsList', []):
        condition = conditions.get(by_number.get(entry.get('Id')), {})
        if condition.get('effect') in ('MaxHealthPermanent', 'IncreasedMaxHealthPermanent') or (condition.get('isPermanent') and condition.get('description') == '%s max health'):
            total += entry.get('Value', 0)
    return total
