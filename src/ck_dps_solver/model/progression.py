"""Biomes and boss progression: each boss is a milestone that opens a biome, and gear comes from biomes.

Choose how far you've progressed: items load from that biome and every one before it. Biomes are the wiki's item
`area` values, in progression order. Edit BIOMES to rename, reorder or regroup.

Items you can only get from a gate boss (its drops or its chest) count as the next biome's: you have them once you've
beaten the boss and moved on. E.g. the Scarab set (Ra-Akar's drops) is a Lava item, not a Desert one. Optional bosses'
drops count in their own tier (OPTIONAL_BOSSES). Random boss drops count from REFIGHT_TIER at the earliest (no
refights before the Cloaked Merchant).
"""
import functools

from ck_dps_solver.model.item_stats import find_internal_id, wiki_data

# (biome, wiki item areas, bosses of that tier), in progression order. Gate bosses open the next tier; optional bosses
# (OPTIONAL_BOSSES) sit in their own biome's tier.
BIOMES = [
    ('Dirt', ['StartArea', 'Slime'], ['Glurch the Abominous Mass']), # Includes the starting gear
    ('Clay Caves', ['Clay'], ['Ghorm the Devourer']),
    # Includes the Larva Hive: reachable from the Clay Caves, but its gear (levels 7-9) and bosses match this tier
    ('Forgotten Ruins', ['Stone', 'LarvaHive', 'Larva'], ['Malugaz the Corrupted', 'King Slime']),
    # The Hive Mother: optional since 1.0 (~330 tiles out, past Malugaz's ~300; her scanner needs Malugaz beaten)
    ("Azeos' Wilderness", ['Nature', 'Mold'], ['Azeos the Sky Titan', 'Ivy the Poisonous Mass', 'The Hive Mother']), # Includes the Mold Dungeon
    ('Sunken Sea', ['Sea', 'City'], ['Omoroth the Sea Titan', 'Morpha the Aquatic Mass']), # Includes the sunken City (Caveling Scholars, City Hall)
    ('Desert of Beginnings', ['Desert', 'Lava'], ['Ra-Akar the Sand Titan', 'Igneous the Molten Mass']), # Includes the lava areas
    ('Shimmering Frontier', ['Crystal'], ['Atlantean Worm', 'Druidra the Wild Titan', 'Crydra the Ice Titan', 'Pyrdra the Fire Titan']),
    ('Passage', ['Passage'], ['Nimruza, Queen of the Burrowed Sands', 'Urschleim', 'Core Commander']),
    ('Excavation', ['Excavation'], ['S.A.H.A.B.A.R.', 'Oblidra the Void Lord']),
]
BIOME_NAMES = [name for name, _, _ in BIOMES]
# Bosses that don't gate progression (checked with the user): their drops count in their tier.
# Only gate bosses' drops count from the next tier, since beating them is what opens it.
OPTIONAL_BOSSES = {'The Hive Mother', 'King Slime', 'Ivy the Poisonous Mass', 'Morpha the Aquatic Mass', 'Igneous the Molten Mass',
                   'Core Commander', 'Haunted Hive Mother'}
_BIOME_OF_AREA = {area: name for name, areas, _ in BIOMES for area in areas}
# Seasonal versions of bosses: same progression tier
BOSS_ALIASES = {'Haunted Hive Mother': 'The Hive Mother'}
# Obtaining kinds that come from killing or looting (anything else, e.g. crafting or merchants, isn't boss-exclusive)
_LOOT_KINDS = {'drop', 'loot', 'lootScene', 'dropScene'}
# Bosses can only be fought again with summoning idols, which the Cloaked Merchant sells; he moves in after Ghorm.
# Until then a boss's random drops are one roll on the first kill, so they count from this tier at the earliest.
REFIGHT_TIER = BIOME_NAMES.index('Forgotten Ruins')


@functools.lru_cache(maxsize=1)
def _boss_tiers():
    """Object id -> biome index, for bosses and their chests (e.g. 'Ghorm Chest')"""
    return {object_id: tier for object_id, (tier, _) in _boss_info().items()}


@functools.lru_cache(maxsize=1)
def _boss_info():
    """Object id -> (biome index, optional boss), for bosses and their chests"""
    tier_of_name = {boss: i for i, (_, _, bosses) in enumerate(BIOMES) for boss in bosses}
    tier_of_name.update({alias: tier_of_name[boss] for alias, boss in BOSS_ALIASES.items()})
    short = {name.split(',')[0].split(' the ')[0].replace('The ', ''): name for name in tier_of_name}
    info = {}
    for object_id, record in wiki_data()['objects'].items():
        name = record.get('name', '')
        # The boss, its chest ('Ghorm Chest'), or its statue ('Ghorm Statue': a crafting station you get by beating it)
        boss = name if name in tier_of_name else (short.get(name[:-len(' Chest')]) if name.endswith(' Chest') else
                                                  short.get(name[:-len(' Statue')]) if name.endswith(' Statue') else None)
        if boss is not None:
            info[object_id] = (tier_of_name[boss], boss in OPTIONAL_BOSSES)
    return info


def _unlock_tier(object_id):
    """Biome index from which a boss's (or its chest's) drops count: the next tier for gate bosses, its own for optional ones"""
    tier, optional = _boss_info()[object_id]
    return tier if optional else min(tier + 1, len(BIOME_NAMES) - 1)


def boss_exclusive_biome(internal_id):
    """The biome an item unlocks in, for items only bosses give (their drops, chests, or crafting at their statue); else None"""
    record = wiki_data()['equipment'].get(internal_id) or wiki_data().get('consumables', {}).get(internal_id, {}) # Gear, or food and potions
    obtaining = record.get('obtaining') or {}
    if not obtaining or set(obtaining) - _LOOT_KINDS - {'crafting'}:
        return None
    tiers = _boss_tiers()
    found = []
    for sources in obtaining.values():
        for source in sources:
            entity = (source.get('entity') or {}).get('id') or source.get('station') # Drops and chests, or a crafting station
            if entity not in tiers:
                return None # Also comes from a regular enemy, chest or structure
            tier = _unlock_tier(entity)
            if entity in _boss_info() and _chance(source) < 1:
                tier = max(tier, REFIGHT_TIER) # Random: you can't farm it before you can refight the boss
            found.append(tier)
    return BIOME_NAMES[min(found)] if found else None


# Soul settings and the boss whose soul each is. A soul is a gate boss's reward, so like its drops it counts from the
# next tier: with progression up to the boss's own biome, you haven't beaten it yet.
SOUL_BOSSES = {'Druidra soul': 'Druidra the Wild Titan', 'Pyrdra soul': 'Pyrdra the Fire Titan'}


def boss_unlock_biome(boss):
    """The biome from which a boss counts as beaten: the next one for gate bosses, its own for optional ones"""
    tier = next(i for i, (_, _, bosses) in enumerate(BIOMES) if boss in bosses)
    return BIOME_NAMES[tier if boss in OPTIONAL_BOSSES else min(tier + 1, len(BIOME_NAMES) - 1)]


def souls_reached(biomes):
    """{soul setting: whether progression has reached it} (biomes None = everything)"""
    return {setting: biomes is None or boss_unlock_biome(boss) in biomes for setting, boss in SOUL_BOSSES.items()}


def _chance(source):
    """Chance of getting at least one per kill or chest (crafting at a boss's statue is certain)"""
    if 'station' in source:
        return 1
    chance = source.get('chanceAtLeastOne', source.get('chance', 0)) or 0
    guaranteed = source.get('guaranteedChanceAtLeastOne', source.get('guaranteedChance', 0)) or 0
    return 1 - (1 - chance) * (1 - guaranteed)


def consumable_biome(internal_id):
    """Biome a food or potion becomes available in: from a boss only, the tier the boss unlocks; else its area (None if unknown)"""
    return boss_exclusive_biome(internal_id) or _BIOME_OF_AREA.get(wiki_data().get('consumables', {}).get(internal_id, {}).get('area'))


def biomes_up_to(biome):
    """Every biome from the start through `biome` (e.g. the biome of the last boss you've beaten)"""
    return BIOME_NAMES[:BIOME_NAMES.index(biome) + 1]


def item_biome(item):
    """Biome an item comes from (None if unknown)"""
    internal_id = find_internal_id(item.name.split(' (')[0]) # e.g. "Owlux (5x Triple Trouble)"
    if internal_id is None:
        return None
    return boss_exclusive_biome(internal_id) or _BIOME_OF_AREA.get(wiki_data()['equipment'][internal_id].get('area'))


def filter_items(items, biomes):
    """Items from the chosen biomes (biomes None = all). Items of unknown biome and empty slots are always kept."""
    if biomes is None:
        return list(items)
    allowed = set(biomes)
    return [item for item in items if item.name == 'None' or item_biome(item) in allowed or item_biome(item) is None]


# ---------------------------------------------------------------- progression from a character save

@functools.lru_cache(maxsize=1)
def progression_markers():
    """Object id -> biome index it proves you've reached (the boss's unlock tier), for items that prove a boss was beaten: guaranteed drops (100%) that only
    bosses give, e.g. Glurch Eye, Ghorm's Horn, the Echo-Maps. Boss chests don't count (you might not take them).
    Bosses without such a drop (The Hive Mother, Morpha, Core Commander) are covered by the next boss in progression."""
    tiers = _boss_tiers()
    objects = wiki_data()['objects']
    is_chest = lambda object_id: 'Chest' in objects.get(object_id, {}).get('categories', []) or objects.get(object_id, {}).get('name', '').endswith(' Chest')
    bosses = {object_id for object_id in tiers if not is_chest(object_id)}
    markers = {}
    for object_id, drops in wiki_data().get('drop_only', {}).items():
        if is_chest(object_id) or not drops or not all(entity in bosses for entity, _ in drops):
            continue
        guaranteed = [_unlock_tier(entity) for entity, chance in drops if chance >= 0.999]
        if guaranteed:
            markers[object_id] = min(guaranteed)
    return markers


# Titan souls in a save's collectedSouls (always collected after the fight), by id. The order follows the titans'
# progression; inferred from saves (soul 1 with Azeos' drops, souls 1-3 with Ra-Akar's) rather than game data.
SOUL_BIOMES = {1: "Azeos' Wilderness", 2: 'Sunken Sea', 3: 'Desert of Beginnings', 4: 'Shimmering Frontier', 5: 'Shimmering Frontier', 6: 'Shimmering Frontier'}
SOUL_NAMES = {1: 'Soul of Azeos', 2: 'Soul of Omoroth', 3: 'Soul of Ra-Akar', 4: 'a Hydra soul', 5: 'a Hydra soul', 6: 'a Hydra soul'}


def progression_from_save(player_path):
    """(biome to search up to, {biome unlocked: [marker item names]}) from a character's discovered items.
    The biome is the furthest one the beaten bosses unlock (a gate boss unlocks the next tier), or the first biome if none."""
    import json
    with open(player_path, encoding='utf-8-sig') as f:
        save = json.load(f)
    objects = wiki_data()['objects']
    by_number = {record['id']: object_id for object_id, record in objects.items()}
    markers = progression_markers()
    evidence = {}
    for entry in save.get('discoveredObjects2', []):
        object_id = by_number.get(entry.get('objectID'))
        if object_id in markers:
            evidence.setdefault(markers[object_id], set()).add(objects[object_id]['name'])
    for soul in save.get('collectedSouls', []):
        if soul in SOUL_BIOMES: # Titans are gate bosses: they unlock the next tier
            evidence.setdefault(min(BIOME_NAMES.index(SOUL_BIOMES[soul]) + 1, len(BIOME_NAMES) - 1), set()).add(f'{SOUL_NAMES[soul]} (collected)')
    if not evidence:
        return BIOME_NAMES[0], {} # Nothing beaten yet: the first biome
    return BIOME_NAMES[max(evidence)], {BIOME_NAMES[t]: sorted(names) for t, names in sorted(evidence.items())}
