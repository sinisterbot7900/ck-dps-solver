"""Drop items (and ring pairs) that can never be part of the best loadout.

An item is dominated when another item in the same slot is at least as good in every attribute (and, for weapons,
damage and attack speed). DPS never decreases when an attribute increases, so swapping the dominated item for the
other one never lowers DPS. Items in a set or group that matters for these settings (see relevant_groups) are never
dropped, since their value depends on the other equipped items. The best loadout is unchanged; the CSV loses
loadouts that only differ by a dominated item.

Attributes the formula never reads for the damage type (e.g. fishing for magic, magic damage for melee) are ignored.
Magic: more attack speed can lower DPS (mana runs out sooner, so mana-based bonuses drop), while every other stat
only helps. So for magic an item must have exactly the same attack speed stats to dominate another (EXACT_FOR_MAGIC),
and magic weapons (which differ in attack speed and mana cost) are all kept.
"""
import numpy as np

from ck_dps_solver.engine.dps_utils import ATTRIBUTES, FORMULA_SETS
from ck_dps_solver.model.character import SET_BONUSES, item_groups
from ck_dps_solver.model.item import FLAT_ATTRIBUTES

# Attributes that must be equal (not just at least as good) for one magic item to dominate another
EXACT_FOR_MAGIC = ['%_melee_attack_speed', '%_range_attack_speed', '%_melee_and_range_attack_speed', '%_melee_attack_speed_proc_chance']


# Attributes the DPS formula never reads for a damage type (so they can't make an item better or worse there)
_MAGIC_ONLY = ['%_magic_damage', '%_magic_damage_near_water', '%_magic_damage_from_mana', '%_magic_damage_on_crit', '+_max_mana', '+_mana_regen',
               '%_mana_regen_while_casting', '%_mana_regen_delay_reduction', '+_magic_barrier', '%_barrier_as_magic_damage', '%_barrier_as_mana_regen']
_MELEE_ONLY = ['%_physical_melee_damage', '%_melee_damage', '%_melee_attack_speed', '%_melee_attack_speed_proc_chance', '+_mining_damage', '%_mining_damage']
_RANGE_ONLY = ['%_physical_range_damage', '%_range_damage', '%_range_attack_speed', '+_fishing', '%_range_damage_while_standing_still']
_EXPLOSIVE_ONLY = ['%_explosives_damage', '%_napalm_chance', '%_burning_damage']
_SUMMON_ONLY = ['%_minion_damage', '%_minion_attack_speed', '%_minion_critical_hit_chance', '%_minion_critical_hit_damage', '%_minion_damage_against_bosses',
                '+_max_minions', '%_mana_reservation_reduction', '%_magic_to_minion_damage', '+_max_health', '%_max_health']
# Summoning's item pool (model/item_stats.considered_for): items for the minions only (minion stats, max mana for more
# minions, magic damage for Trickle down arcana and the Grim set, max health for Heartbound horde). The scepter's own
# damage is counted, but gear isn't picked for it (it's a small share of a summoner's DPS); this keeps searches small.
SUMMON_ITEM_ATTRIBUTES = set(_SUMMON_ONLY) | {'+_max_mana', '%_magic_damage'}
UNUSED_ATTRIBUTES = {
    'Range': _MELEE_ONLY + _MAGIC_ONLY + _SUMMON_ONLY,
    'Melee': _RANGE_ONLY + _MAGIC_ONLY + _SUMMON_ONLY + _EXPLOSIVE_ONLY,
    # Magic weapons hit at range or in melee (Zealot's Scimitar), so only physical-only attributes are unused
    'Magic': ['%_physical_melee_damage', '%_physical_range_damage', '+_fishing', '+_mining_damage', '%_mining_damage'] + _SUMMON_ONLY + _EXPLOSIVE_ONLY,
    # Summoners: items are judged for the minions only (SUMMON_ITEM_ATTRIBUTES), like the item pool. The scepter's own
    # damage still counts in the DPS, but an item that only helps the scepter can be dropped (a small share of the DPS).
    'Summoning': [a for a in ATTRIBUTES if a not in SUMMON_ITEM_ATTRIBUTES],
    # Explosions only get explosives bonuses
    'Explosives': [a for a in ATTRIBUTES if a not in _EXPLOSIVE_ONLY],
}


def worthless_attributes(damage_type, perks, items):
    """Attributes that can't change DPS with these talents and the items available (e.g. mining damage for melee without
    Miner's strength or Miner/Ancient Gem set pieces), so items are judged without them"""
    if perks is None:
        return []
    sets = {item.set for item in items}
    has = lambda attribute: any(item.attributes.get(attribute, 0) for item in items)
    worthless = []
    if damage_type == 'Melee' and not perks['Mining']["Miner's strength"] and not sets & {'MinerSet', 'AncientGemRingAndNecklace'}:
        worthless += ['+_mining_damage', '%_mining_damage'] # Mining damage only becomes hit damage through these
    if damage_type == 'Range' and not perks['Fishing']['Well-trained aim'] and 'DiverSet' not in sets:
        worthless += ['+_fishing'] # Likewise fishing
    if 'ScarabSet' not in sets:
        worthless += ['+_thorns_damage'] # Only the Scarab 3-piece adds thorns to hits
    if not perks['Gardening']['Potent poison'] and 'IvySet' not in sets and not has('%_damage_against_poisoned'):
        worthless += ['%_chance_to_apply_poison'] # Nothing that needs poisoned targets
    return worthless


def exact_attributes(damage_type):
    return EXACT_FOR_MAGIC if damage_type == 'Magic' else []


def unused_attributes(damage_type):
    return UNUSED_ATTRIBUTES.get(damage_type, [])


# Sets the formula uses only for one kind of physical weapon: Diver (fishing damage, physical range),
# Miner and Ancient Gem (mining damage, physical melee)
FORMULA_SETS_FOR = {'DiverSet': {'Range'}, 'MinerSet': {'Melee'}, 'AncientGemRingAndNecklace': {'Melee'}}


def relevant_groups(settings, damage_type=None, worthless=()):
    """Sets and groups that can change DPS with these settings (and damage type, if given): those needed by a set
    bonus whose setting is on and whose attribute the damage type uses, and those the DPS formula uses (the Welder
    set only matters for burning targets while you burn)."""
    unused = set(unused_attributes(damage_type)) | set(worthless) # worthless: see worthless_attributes
    groups = {s for attribute, _, _, required, setting in SET_BONUSES if (setting is None or settings[setting]) and attribute not in unused for s in required}
    groups |= {s for s in FORMULA_SETS if (s != 'PlateSet' or settings['Burning'])
               and (damage_type is None or damage_type in FORMULA_SETS_FOR.get(s, {damage_type}))}
    return groups


def set_only_requirements(items, settings, damage_type, worthless=()):
    """Items that only count through a set (none of their own stats matter for this damage type, but a set bonus or the
    formula uses their set): {id(item): {set: pieces needed}}. Such an item adds nothing unless its set is complete."""
    from ck_dps_solver.engine.dps_utils import FORMULA_SET_PIECES
    unused = list(unused_attributes(damage_type)) + list(worthless)
    groups = relevant_groups(settings, damage_type, worthless)
    needs = {} # Set -> fewest pieces that do something
    for attribute, _, _, required, setting in SET_BONUSES:
        if (setting is None or settings[setting]) and attribute not in unused:
            for group, pieces in required.items():
                needs[group] = min(needs.get(group, pieces), pieces)
    for group, pieces in FORMULA_SET_PIECES.items():
        if group in groups:
            needs[group] = min(needs.get(group, pieces), pieces)
    found = {}
    for item in items:
        sets = item_groups(item) & groups
        if item.name != 'None' and item.item_category != 'Weapon' and sets and not np.any(_vector(item, True, unused)):
            found[id(item)] = {group: needs[group] for group in sets if group in needs}
    return found


def completes_sets(items, requirements):
    """False when an item that only counts through its set is worn without enough pieces of that set"""
    if not requirements:
        return True
    counts = {}
    for item in {i.name: i for i in items if i is not None and i.name != 'None'}.values(): # Two copies of a ring count once
        for group in item_groups(item):
            counts[group] = counts.get(group, 0) + 1
    return all(any(counts.get(group, 0) >= pieces for group, pieces in requirements[id(item)].items())
               for item in items if item is not None and id(item) in requirements)


def _vector(item, reinforce, unused=()):
    attributes = {k: v for k, v in item.attributes.items() if k not in unused}
    if reinforce and item.has_durability and not item.reinforced:
        attributes = {k: round(v * 1.15, 0 if k in FLAT_ATTRIBUTES else 3) for k, v in attributes.items()}
    v = list(attributes.values())
    if item.item_category == 'Weapon':
        scale = 1.15 if reinforce and item.has_durability and not item.reinforced else 1
        v += [item.min_damage * scale, item.max_damage * scale, item.attacks_per_second, item.explosive_damage * scale]
    return np.array(v, dtype=float)


def _dominated_by(vectors, a, exact_columns=()):
    """Indices that are at least as good as `a` everywhere and equal in exact_columns (an exact duplicate only counts if listed earlier)"""
    exact = list(exact_columns)
    return [b for b in range(len(vectors)) if b != a and np.all(vectors[b] >= vectors[a]) and (np.any(vectors[b] > vectors[a]) or b < a)
            and np.all(vectors[b][exact] == vectors[a][exact])]


def undominated(items, groups, copies=None, reinforce=True, exact=(), unused=()):
    """Indices of items that aren't dominated by another item in the list.
    groups: relevant sets/groups; items in one are kept. Empty slots ('None') are always kept.
    copies: for rings, the copies owned of each item. Two ring slots can hold the dominators, so a ring is only
    dropped when its dominators add up to 2+ copies.
    exact: attributes that must be equal to dominate (see EXACT_FOR_MAGIC). unused: attributes to ignore (unused_attributes)."""
    vectors = [_vector(item, reinforce, unused) for item in items]
    names = [k for k in items[0].attributes if k not in unused] if items else []
    exact_columns = [names.index(k) for k in exact if k in names]
    copies = copies if copies is not None else [None] * len(items)
    keep = []
    for a, item in enumerate(items):
        if item_groups(item) & groups or item.name == 'None':
            keep.append(a)
            continue
        if item.item_category != 'Weapon' and not np.any(vectors[a]):
            continue # Nothing that counts: the same as an empty slot
        needed = 2 if copies[a] is not None else 1
        if sum(copies[b] if copies[b] is not None else 2 for b in _dominated_by(vectors, a, exact_columns)) < needed:
            keep.append(a)
    return keep


def drop_dominated(weapons, slots, settings, ring_copies=None, damage_type=None, perks=None):
    """(weapons, slots, ring_copies) without dominated items, and without items that can't add anything (perks: talents
    by name, for worthless_attributes)"""
    pool = list(weapons) + [item for items in slots.values() for item in items]
    worthless = worthless_attributes(damage_type, perks, pool)
    groups = relevant_groups(settings, damage_type, worthless)
    exact, unused = exact_attributes(damage_type), unused_attributes(damage_type) + worthless
    if damage_type not in ('Magic', 'Summoning', 'Explosives'): # Their weapons differ in ways dominance doesn't compare (mana costs, napalm)
        weapons = [weapons[i] for i in undominated(weapons, groups, unused=unused)]
    new_slots = {}
    for slot, items in slots.items():
        keep = undominated(items, groups, copies=ring_copies if slot == 'Ring' else None, exact=exact, unused=unused)
        new_slots[slot] = [items[i] for i in keep]
        if slot == 'Ring' and ring_copies is not None:
            ring_copies = [ring_copies[i] for i in keep]
    return weapons, new_slots, ring_copies


def undominated_pairs(pair_values, pair_has_groups, exact=(), unused=()):
    """Indices of ring pairs to keep: a pair without relevant groups is dropped when another pair's combined
    attributes are at least as good everywhere and equal in `exact` attributes (exact duplicates: the first is kept)."""
    v = np.asarray(pair_values, dtype=float)
    exact_columns = [ATTRIBUTES.index(k) for k in exact]
    if unused:
        v = v.copy()
        v[:, [ATTRIBUTES.index(k) for k in unused]] = 0
    n = len(v)
    keep = []
    for a in range(n):
        if pair_has_groups[a]:
            keep.append(a)
            continue
        at_least = np.all(v >= v[a], axis=1)
        if exact_columns: at_least &= np.all(v[:, exact_columns] == v[a, exact_columns], axis=1)
        better = np.any(v > v[a], axis=1)
        earlier = np.arange(n) < a
        at_least[a] = False
        if not np.any(at_least & (better | earlier)):
            keep.append(a)
    return keep
