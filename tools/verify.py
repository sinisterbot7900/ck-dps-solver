"""Consistency checks to run after changing items, set bonuses, or the DPS math.

Usage: python -m tools.verify [--level 20] [--samples 3000]
  1. catalogue.py matches the wiki data at the given level (stats, weapon damage, sets)
  2. Every set referenced by SET_BONUSES exists in the wiki data (or is a solver group like 'Poison source')
  3. The batch search engine gives exactly the same DPS as Character + calculate_dps on random loadouts (melee, range
     and magic), and its skip-ahead upper bound is never below a real DPS
Exits non-zero if any check fails.
"""
import copy
import os
import random
import sys

import tools  # noqa: F401 (puts src/ on the path)
from ck_dps_solver import catalogue as I
from ck_dps_solver.engine.batch_search import SearchSpace
from ck_dps_solver.engine.dps_utils import calculate_dps
from ck_dps_solver.model import Character
from ck_dps_solver.model.character import BURN_SOURCE, SET_BONUSES
from ck_dps_solver.model.item_stats import find_internal_id, make_item, wiki_data
from ck_dps_solver.model.summoning import summoner_kits
from ck_dps_solver.saves.owned_items import empty_item

CATALOGUE = {'WEAPONS': I.WEAPONS, 'HELMS': I.HELMS, 'BREAST_ARMORS': I.BREAST_ARMORS, 'PANTS_ARMORS': I.PANTS_ARMORS, 'NECKLACES': I.NECKLACES,
             'RINGS': I.RINGS, 'OFFHANDS': I.OFFHANDS, 'BAGS': I.BAGS, 'LANTERNS': I.LANTERNS}
SOLVER_GROUPS = {BURN_SOURCE}


def check_items(level):
    problems = []
    for dict_name, items in CATALOGUE.items():
        for name, item in items.items():
            internal_id = find_internal_id(name)
            if internal_id is None:
                problems.append(f'{dict_name}: {name!r} is not in the wiki data')
                continue
            expected = make_item(internal_id, level)
            if expected is None:
                problems.append(f'{dict_name}: {name!r} is not usable by the solver')
                continue
            ours = {k: v for k, v in item.attributes.items() if v}
            theirs = {k: v for k, v in expected.attributes.items() if v}
            if ours != theirs:
                problems.append(f'{dict_name}: {name!r} attributes {ours} != wiki {theirs}')
            if item.has_durability != expected.has_durability:
                problems.append(f'{dict_name}: {name!r} can be reinforced {item.has_durability} != wiki {expected.has_durability}')
            if item.set != expected.set:
                problems.append(f'{dict_name}: {name!r} set {item.set!r} != wiki {expected.set!r}')
            if dict_name == 'WEAPONS':
                for field in ('min_damage', 'max_damage', 'attacks_per_second', 'damage_type', 'delivery', 'mana_cost', 'aura_damage', 'curses', 'explosive_damage'):
                    if getattr(item, field) != getattr(expected, field):
                        problems.append(f'{name!r} {field} {getattr(item, field)} != wiki {getattr(expected, field)}')
    return problems


def check_sets():
    sets = set(wiki_data()['sets'])
    return [f'SET_BONUSES {label!r} needs unknown set {s!r}' for _, label, _, required, _ in SET_BONUSES for s in required if s not in sets | SOLVER_GROUPS]


def check_engine(samples, seed=0):
    from ck_dps_solver.defaults import CONSUMABLES, perk_trees, skill_levels
    from ck_dps_solver.engine.solver import catalogue_search_items, consumable_effects
    rng = random.Random(seed)
    toggles = ['Max health', 'Standing still', 'Range stacks', 'Not hit', 'Kill stacks', 'Recently dodged', 'Burning', 'Well fed', 'Low health', 'Recently mined', 'Vs boss',
               'Adjacent to water', 'Full barrier', 'Druidra soul', 'Cursed target']
    problems, checked = [], 0
    for trial in range(15):
        damage_type = ['Range', 'Melee', 'Magic', 'Summoning', 'Explosives'][trial % 5]
        settings = Character(skill_levels, perk_trees).settings
        for t in toggles:
            settings[t] = rng.random() < 0.5
        settings['Fight length'] = rng.choice([5, 20, 60, 300])
        settings['Permanent max health'] = rng.choice([0, 275, 520])
        food_effects, potion_effects = consumable_effects(CONSUMABLES[damage_type]), {}
        weapons, slots, ring_copies, fixed = catalogue_search_items(damage_type)
        slots = {slot: items or [empty_item(slot)] for slot, items in slots.items()} # No item for the type: an empty slot
        weapons = rng.sample(weapons, min(3, len(weapons)))
        if damage_type == 'Summoning':
            pool = catalogue_search_items(damage_type)[0]
            weapons = summoner_kits(rng.sample([w for w in pool if not w.curses], 2) + rng.sample([w for w in pool if w.curses], 2))
        kwargs = dict(skill_levels=skill_levels, perks=perk_trees, food_effects=food_effects, potion_effects=potion_effects, settings=copy.deepcopy(settings))
        space = SearchSpace(weapons, slots, fixed, kwargs, ring_copies=ring_copies)
        neck_idx, pair_idx, off_idx = space.inner_index
        for _ in range(3):
            w = rng.randrange(len(weapons))
            h, b, p = (rng.randrange(len(slots[s])) for s in ('Helm', 'Breast armor', 'Pants armor'))
            dps = space.evaluate(w, h, b, p)
            if space.upper_bound(w, h, b, p) < dps.max():
                problems.append(f'upper bound below a real DPS ({damage_type}, {weapons[w].name}): {space.upper_bound(w, h, b, p)} < {dps.max()}')
            for inner in rng.sample(range(len(dps)), min(len(dps), samples // 45)):
                r1, r2 = space.ring_pairs[pair_idx[inner]]
                c = Character(skill_levels, perk_trees, food_effects=food_effects, potion_effects=potion_effects, settings=copy.deepcopy(settings))
                c.equip(weapons[w])
                for item in [slots['Helm'][h], slots['Breast armor'][b], slots['Pants armor'][p], slots['Necklace'][neck_idx[inner]],
                             slots['Ring'][r1], slots['Ring'][r2], slots['Offhand'][off_idx[inner]]] + list(fixed):
                    c.equip(item)
                c.reinforce_items()
                checked += 1
                if calculate_dps(c) != int(dps[inner]):
                    problems.append(f'engine mismatch ({damage_type}, {weapons[w].name}): {calculate_dps(c)} vs {int(dps[inner])}')
    return problems, checked


if __name__ == '__main__':
    args = sys.argv[1:]
    level = int(args[args.index('--level') + 1]) if '--level' in args else 20
    samples = int(args[args.index('--samples') + 1]) if '--samples' in args else 3000
    failed = False
    for label, problems in [('catalogue.py vs wiki data', check_items(level)), ('set bonus table', check_sets())]:
        print(f'{label}: {"OK" if not problems else f"{len(problems)} problems"}')
        for p in problems[:50]:
            print('   ', p)
        failed |= bool(problems)
    problems, checked = check_engine(samples)
    print(f'batch engine vs single loadout: {checked} loadouts, {"OK" if not problems else f"{len(problems)} mismatches"}')
    for p in problems[:10]:
        print('   ', p)
    failed |= bool(problems)
    sys.exit(1 if failed else 0)
