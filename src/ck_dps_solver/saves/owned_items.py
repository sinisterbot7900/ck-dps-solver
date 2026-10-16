"""Turn the items a player owns (saves/save_reader.py) into search candidates at their actual levels."""
from collections import defaultdict
from dataclasses import replace

from ck_dps_solver.model import Item
from ck_dps_solver.model.character import item_groups

from ck_dps_solver.model.item_stats import considered_for, make_item, wiki_data
from ck_dps_solver.model.pets import pet_item
from ck_dps_solver.saves.save_reader import MAX_LEVEL

SEARCH_SLOTS = ['Helm', 'Breast armor', 'Pants armor', 'Necklace', 'Ring', 'Offhand']
EMPTY = 'None'


def empty_item(category):
    """An empty slot"""
    return Item(name=EMPTY, item_category=category, consider_for='Both')


def best_copies(copies, n):
    """The n best copies of one item: highest level first, then reinforced"""
    return sorted(copies, key=lambda c: (c.level, c.reinforced), reverse=True)[:n]


def build_pet(copy, catalogue):
    """Pet with the talents the save shows; pets without talent data (in chests) use their catalogue.py entry if there is one"""
    if copy.talents is None and copy.name in catalogue:
        return catalogue[copy.name]
    return pet_item(copy.internal_id, copy.talents or ())


def build_item(copy, catalogue, reinforcement):
    """Item for an owned copy. consider_for comes from the catalogue (catalogue.py) when the item is there"""
    if wiki_data()['equipment'][copy.internal_id].get('type') == 'Pet':
        return build_pet(copy, catalogue)
    known = catalogue.get(copy.name)
    item = make_item(copy.internal_id, copy.level, consider_for=known.consider_for if known is not None else None)
    if item is not None and reinforcement == 'detected' and not copy.reinforced:
        item.has_durability = False # Not reinforced, so it can't be reinforced in this search
    return item


def owned_search_items(owned, damage_type, catalogue, reinforcement='assume', level='actual'):
    """
    Search candidates from owned items.
    owned: list of OwnedItem. catalogue: {name: Item} from catalogue.py, used for consider_for.
    reinforcement: 'assume' (every reinforceable item counts as reinforced) or 'detected' (only items the save shows as reinforced).
    level: 'actual' (each item at its level in the save) or 'max' (every item as if upgraded to MAX_LEVEL).
    Returns (weapons, slots {slot: [Item]}, ring_copies, by_category {category: [Item]} for other categories such as bags and lanterns).
    """
    copies_by_item = defaultdict(list)
    for copy in owned:
        if level == 'max':
            copy = replace(copy, level=MAX_LEVEL)
        copies_by_item[copy.internal_id].append(copy)

    weapons, slots, ring_copies, other = [], {slot: [] for slot in SEARCH_SLOTS}, [], defaultdict(list)
    for internal_id, copies in copies_by_item.items():
        probe = build_item(copies[0], catalogue, reinforcement)
        if probe is None or (probe.item_category not in ('Weapon', 'Pet') and not considered_for(probe, damage_type)):
            continue
        category = probe.item_category
        if category == 'Ring':
            best = best_copies(copies, 2)
            if len(best) == 2 and (best[0].level, best[0].reinforced) == (best[1].level, best[1].reinforced):
                slots['Ring'].append(build_item(best[0], catalogue, reinforcement)); ring_copies.append(2)
            else:
                for copy in best:
                    slots['Ring'].append(build_item(copy, catalogue, reinforcement)); ring_copies.append(1)
            continue
        if category == 'Pet':
            # Every owned pet, once per distinct set of talents
            seen = set()
            for copy in copies:
                pet = build_item(copy, catalogue, reinforcement)
                key = tuple(sorted(pet.attributes.items()))
                if key not in seen:
                    seen.add(key)
                    other['Pet'].append(pet)
            continue
        item = build_item(best_copies(copies, 1)[0], catalogue, reinforcement)
        if category == 'Weapon':
            if item.damage_type == damage_type or (damage_type == 'Summoning' and item.curses): weapons.append(item) # Summoners: scepters too
        elif category in slots:
            slots[category].append(item)
        else:
            other[category].append(item)

    # Items with no stats the solver uses and no set/group score exactly like an empty slot, so only the empty slot is kept
    for slot in SEARCH_SLOTS:
        keep = [i for i, item in enumerate(slots[slot]) if any(item.attributes.values()) or item_groups(item)]
        slots[slot] = [slots[slot][i] for i in keep]
        if slot == 'Ring': ring_copies = [ring_copies[i] for i in keep]
        slots[slot].append(empty_item(slot))
        if slot == 'Ring': ring_copies.append(2)
    return weapons, slots, ring_copies, other
