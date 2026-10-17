"""Runs a search: builds the items to try (every item for the progression, or the ones in your saves), searches every
loadout with the compiled engine (engine/batch_search.py) and suggests upgrades.

run_search(config) is the entry point; config is defaults.default_config() with your changes. Also here: a single
loadout's DPS, its DPS over a fight and its stat breakdown, used by the window's details panels.
"""
import copy
import itertools
import math
import os
import time

import pandas as pd
from tqdm import tqdm

from ck_dps_solver.catalogue import (BAGS, BREAST_ARMORS, HELMS, LANTERNS, NECKLACES, OFFHANDS, PANTS_ARMORS, PETS, RINGS, WEAPONS,
                                    get_keys_for_damage_type)
from ck_dps_solver.defaults import CONSUMABLES, FIXED_ITEM_NAMES, default_config, skill_levels
from ck_dps_solver.engine.batch_search import SearchSpace, loadout_items, search
from ck_dps_solver.engine.dominance import (completes_sets, drop_dominated, exact_attributes, relevant_groups, set_only_requirements,
                                           undominated, unused_attributes, worthless_attributes)
from ck_dps_solver.engine.dps_utils import calculate_dps
from ck_dps_solver.engine.upgrades import suggest_upgrades
from ck_dps_solver.model import Character
from ck_dps_solver.model.character import count_set_pieces
from ck_dps_solver.model.consumables import DEFAULT_DISH_RARITY, combine, default_keys, lookup as consumable_lookup
from ck_dps_solver.model.item_stats import find_internal_id, make_item
from ck_dps_solver.model.pets import catalogue_pets
from ck_dps_solver.model.progression import filter_items, souls_reached
from ck_dps_solver.model.summoning import summoner_kits
from ck_dps_solver.saves.owned_items import empty_item, owned_search_items
from ck_dps_solver.saves.save_reader import base_level, permanent_max_health, read_character_stats, read_owned, soul_settings


def best_consumables(damage_type, skill_levels, perk_trees, biomes=None, dish_rarity=DEFAULT_DISH_RARITY, golden=True, only=None):
    """The strongest food and potion per effect for a damage type, from the chosen biomes (None = all), skipping effects
    your talents make worthless (e.g. mining dishes without Miner's strength; see dominance.worthless_attributes).
    only: choose from these keys alone (the food and potions you own)"""
    perks = Character(skill_levels, perk_trees).perks
    weapons, slots, _, _ = catalogue_search_items(damage_type)
    pool = filter_items(list(weapons) + [item for items in slots.values() for item in items], biomes)
    unused = unused_attributes(damage_type) + worthless_attributes(damage_type, perks, pool)
    return default_keys(damage_type, unused, biomes, dish_rarity, golden, only)


def consumable_effects(keys, dish_rarity=DEFAULT_DISH_RARITY, golden=True):
    """Food and potion effects for Character (food_effects) from source keys"""
    return combine(keys, dish_rarity, golden)[0]


BEST_FIXED_LOADOUTS = 1000 # Loadouts the quick search keeps; combinations are scored on the best one per weapon
BEST_FIXED_SEARCH_ALL = 4 # With this many combinations or fewer, Best just tries them all in the one search (exact, and no extra pass)
# Searching every item: pets are assumed to have learned this many talents (one version per talent, all points in it)
CATALOGUE_PET_TALENT_POINTS = 5
# ...and only these talents (Triple Trouble's triple damage makes it the best pick). None = try every talent
CATALOGUE_PET_TALENTS = ['ChanceToDealTripleDamage']
# ...per damage type where it differs: minions only get minion effects, so Summoning tries the minion talents
CATALOGUE_PET_TALENTS_FOR = {'Summoning': ['MinionDamage', 'MinionAttackSpeed', 'MinionCritChance', 'MinionCritDamage', 'MinionBossDamage', 'ChanceToDealTripleDamage']}
UPGRADE_COLUMNS = ['Gain %', 'Upgrade', 'Slot', 'DPS', 'Gain', 'Biome', 'Seasonal', 'Uses', 'Where to get'] # Gain % first, like DPS on the loadouts

FIXED_ITEM_DICTS = {'Lantern': LANTERNS, 'Bag': BAGS, 'Pet': PETS}


def fixed_items(names):
    """Items from names, looked up in LANTERNS, BAGS and PETS"""
    found = []
    for name in names:
        item = next((d[name] for d in FIXED_ITEM_DICTS.values() if name in d), None)
        if item is None:
            raise KeyError(f'{name!r} is not in LANTERNS, BAGS or PETS in catalogue.py')
        found.append(item)
    return found


FIXED_ITEMS = {damage_type: fixed_items(names) for damage_type, names in FIXED_ITEM_NAMES.items()}


def catalogue_search_items(damage_type, config=None):
    """Every item in catalogue.py for a damage type"""
    weapons = [WEAPONS[k] for k in get_keys_for_damage_type([WEAPONS], damage_type)[0]]
    helms, breast_armors, pants_armors, necklaces, rings, offhands = get_keys_for_damage_type([HELMS, BREAST_ARMORS, PANTS_ARMORS, NECKLACES, RINGS, OFFHANDS], damage_type)
    slots = {
        'Helm': [HELMS[k] for k in helms], 'Breast armor': [BREAST_ARMORS[k] for k in breast_armors], 'Pants armor': [PANTS_ARMORS[k] for k in pants_armors],
        'Necklace': [NECKLACES[k] for k in necklaces], 'Ring': [RINGS[k] for k in rings], 'Offhand': [OFFHANDS[k] for k in offhands],
    }
    names = (config or default_config())['fixed_items'][damage_type]
    return weapons, slots, None, fixed_items(names)


def owned_search_items_for(damage_type, config=None, log=print, return_pets=False):
    """Items from the save files, at their actual levels. return_pets: also return the owned pets and the other owned
    items by category (lanterns, bags...)"""
    config = config or default_config()
    save_filter = config['save_filter']
    center = tuple(save_filter['center']) if save_filter.get('center') is not None else None
    owned = read_owned(save_filter['player_files'], save_filter['world_files'], center=center, radius=save_filter['radius'])
    catalogue = {name: item for items in [WEAPONS, HELMS, BREAST_ARMORS, PANTS_ARMORS, NECKLACES, RINGS, OFFHANDS, BAGS, LANTERNS, PETS] for name, item in items.items()}
    weapons, slots, ring_copies, other = owned_search_items(owned, damage_type, catalogue, save_filter['reinforcement'], save_filter.get('level', 'actual'))
    # Lantern and bag: the configured ones, at the level you own them (left out if you don't own them). The pet is kept as configured.
    fixed = []
    for item in fixed_items(config['fixed_items'][damage_type]):
        owned_copies = [i for i in other.get(item.item_category, []) if i.name == item.name]
        fixed += owned_copies[:1] if item.item_category in ('Lantern', 'Bag') else [item]
    pets = other.get('Pet', [])
    log(f'Owned: {len(owned)} equipment items -> {len(weapons)} weapons, ' + ', '.join(f'{len(v) - 1} {k.lower()}' for k, v in slots.items())
        + f' (plus empty slots), {len(pets)} pets')
    return (weapons, slots, ring_copies, fixed, pets, other) if return_pets else (weapons, slots, ring_copies, fixed)


def has_talent(perk_trees, skill, talent):
    """Whether a talent has points, by name (talent order from Character)"""
    names = list(Character(skill_levels, perk_trees).perks[skill])
    return perk_trees[skill][names.index(talent)] > 0


def upgrade_candidates(damage_type, config, biomes, owned_names):
    """catalogue.py items for a damage type from the chosen biomes that you don't own, at their base level"""
    weapons, slots, _, _ = catalogue_search_items(damage_type, config)
    items = weapons + [item for items in slots.values() for item in items]
    if not has_talent(config['perk_trees'], 'Crafting', 'Jewelry crafter'):
        items = [item for item in items if not item.name.startswith('Polished ')] # Polished jewelry needs the talent
    return [at_base_level(item) for item in filter_items(items, biomes) if item.name not in owned_names and item.name != 'None']


def dps_over_time(loadout, fixed, character_kwargs, seconds=60, step=0.5):
    """DPS over a fight for one loadout (a search result: dps, weapon, helm, ..., offhand, pet).
    Returns (times, average, at_moment): average[i] is the DPS of a fight lasting times[i] seconds (what the search ranks
    by); at_moment[i] is the DPS around that moment, from the change in total damage (shows mana running out and
    poison landing)."""
    items = [copy.deepcopy(item) for item in loadout_items(loadout, fixed) if item.name != 'None']
    for item in items: item.reinforce() # As in the search (copies, so a ring worn twice is reinforced once each)
    times, average = [], []
    for i in range(1, int(round(seconds / step)) + 1):
        t = i * step
        character = Character(**dict(character_kwargs, settings=dict(character_kwargs['settings'], **{'Fight length': t})))
        for item in items: character.equip(item)
        times.append(t)
        average.append(calculate_dps(character))
    at_moment = [average[0]] + [(times[i] * average[i] - times[i - 1] * average[i - 1]) / (times[i] - times[i - 1]) for i in range(1, len(times))]
    return times, average, at_moment


def loadout_breakdown(loadout, fixed, character_kwargs):
    """Where each stat of a loadout (a search result) comes from.
    Returns (rows [(attribute, total, [(source, value), ...])] for nonzero stats, active sets {set: pieces})."""
    items = [copy.deepcopy(item) for item in loadout_items(loadout, fixed) if item.name != 'None']
    for item in items: item.reinforce() # As in the search
    character = Character(**character_kwargs)
    for item in items: character.equip(item)
    effects, set_keywords = character.get_active_effects()
    rows = [(attribute, round(sum(sources.values()), 4), sorted(sources.items(), key=lambda kv: -abs(kv[1])))
            for attribute, sources in effects.items() if sources and abs(sum(sources.values())) > 1e-9]
    return rows, count_set_pieces(set_keywords)


def loadout_dps(items, character_kwargs):
    """DPS of equipped items (reinforced as in the search)"""
    items = [copy.deepcopy(item) for item in items if item is not None and item.name != 'None']
    for item in items: item.reinforce()
    character = Character(**character_kwargs)
    for item in items: character.equip(item)
    return calculate_dps(character)


def pick_best_fixed(space, fixed, choices, character_kwargs, log=print, should_stop=None):
    """The best lantern / bag / pet for the categories in `choices` ({category: candidate items}): a quick search without
    them, then every combination scored on the best loadout of each weapon. Returns the chosen items (empty slots left out)."""
    names = ', '.join(category.lower() for category in choices)
    log(f'Picking the best {names}: a quick search without them, then each combination on the best loadout of each weapon')
    found, _ = search(space, BEST_FIXED_LOADOUTS, should_stop=should_stop)
    # One loadout per weapon: an item can matter for one weapon only (e.g. mana for a staff that runs out of it)
    top = list({loadout[1].name: loadout for loadout in reversed(found)}.values())
    combos = list(itertools.product(*choices.values()))
    best, best_dps = combos[0], -1
    for combo in combos:
        dps = max((loadout_dps(loadout_items(loadout, fixed) + list(combo), character_kwargs) for loadout in top), default=0)
        if dps > best_dps: # Ties keep the earlier combination (empty slots first)
            best, best_dps = combo, dps
    log('Best ' + ', '.join(f'{category.lower()}: {item.name}' for category, item in zip(choices, best)) + f' ({len(combos)} combinations tried)')
    return [item for item in best if item.name != 'None']


def at_base_level(item):
    """An catalogue.py item rebuilt at its base (unupgraded) level from the wiki data. Pets and empty slots are unchanged."""
    if item.item_category == 'Pet' or item.name == 'None':
        return item
    internal_id = find_internal_id(item.name)
    if internal_id is None:
        return item
    level = base_level(internal_id)
    rebuilt = make_item(internal_id, level, consider_for=item.consider_for)
    if rebuilt is None:
        return item
    rebuilt.level = level
    return rebuilt


def display_name(item):
    return item.name if item.level is None or item.name == 'None' else f'{item.name} (lv {item.level})'


def run_search(config, progress=None, should_stop=None, log=print):
    """
    One full run: pick items, search, write the CSV.
    progress: object with start(total, description) and update(n); None shows a tqdm bar.
    should_stop: callable; when it returns True the search stops early (results so far are still returned and saved).
    Returns (results DataFrame, info dict).
    """
    start = time.time()
    damage_type = config['damage_type']
    config = copy.deepcopy(config)
    save_filter = config['save_filter']
    if save_filter['enabled'] and save_filter.get('character_stats', True) and save_filter['player_files']:
        config['skill_levels'], config['perk_trees'] = read_character_stats(save_filter['player_files'][0], list(config['skill_levels']))
        player = save_filter['player_files'][0]
        config['settings'] = dict(config['settings'], **soul_settings(player), **{'Permanent max health': permanent_max_health(player)})
        log(f"Skills and talents from {os.path.basename(save_filter['player_files'][0])}")
    if config.get('biomes') is not None and not save_filter['enabled']:
        # Progression check (every-item searches): the food and potions from these biomes, items at their base level
        # (as found). Owned searches use everything you own and the food you ticked; progression only limits upgrades
        rarity, golden = config.get('dish_rarity', DEFAULT_DISH_RARITY), config.get('golden_ingredients', True)
        if config.get('consumables_from_ticks'): # The GUI ticks the best ones for the progression; use them, without later biomes'
            def allowed(key): # Owned dishes have no biome: you have them
                source = consumable_lookup(key, rarity, golden)
                return source is not None and (source.biome is None or source.biome in config['biomes'])
            keys = [k for k in config['consumables'].get(damage_type, []) if allowed(k)]
        else:
            keys = best_consumables(damage_type, config['skill_levels'], config['perk_trees'], config['biomes'], rarity, golden)
        config['consumables'] = dict(config['consumables'], **{damage_type: keys})
        log('Biome check: items at their base level; food and potions from these biomes: ' + ', '.join(consumable_lookup(k, rarity, golden).name for k in keys))
        # Souls of bosses that progression hasn't reached yet don't count
        unreached = [setting for setting, reached in souls_reached(config['biomes']).items() if not reached and config['settings'].get(setting)]
        if unreached:
            config['settings'] = dict(config['settings'], **{setting: False for setting in unreached})
            log(f"Not reached yet with this progression, so off: {', '.join(unreached)}")
    if config['save_filter']['enabled']:
        weapons, slots, ring_copies, fixed, pets, other = owned_search_items_for(damage_type, config, log, return_pets=True)
        searchable = {'Lantern': list(other.get('Lantern', [])), 'Bag': list(other.get('Bag', []))}
        owned_names = {item.name for item in weapons} | {item.name for items in slots.values() for item in items}
    else:
        weapons, slots, ring_copies, fixed = catalogue_search_items(damage_type, config)
        pets = catalogue_pets(CATALOGUE_PET_TALENT_POINTS, CATALOGUE_PET_TALENTS_FOR.get(damage_type, CATALOGUE_PET_TALENTS))
        searchable = {'Lantern': list(LANTERNS.values()), 'Bag': list(BAGS.values())}
    original_rings = list(slots['Ring'])
    if not config['save_filter']['enabled'] and not has_talent(config['perk_trees'], 'Crafting', 'Jewelry crafter'):
        # Polished jewelry only comes from the Jewelry crafter talent
        slots['Necklace'] = [i for i in slots['Necklace'] if not i.name.startswith('Polished ')]
        slots['Ring'] = [i for i in slots['Ring'] if not i.name.startswith('Polished ')]
        original_rings = list(slots['Ring'])
    biomes = config.get('biomes')
    if biomes is not None and config['save_filter']['enabled']:
        # Items you own are all available, wherever the wiki says they come from; the progression only limits the
        # food and the upgrade suggestions
        log(f'Progression up to {biomes[-1]}: all your items are used; it only limits the upgrade suggestions')
    elif biomes is not None:
        weapons = filter_items(weapons, biomes)
        slots = {slot: filter_items(items, biomes) for slot, items in slots.items()}
        if ring_copies is not None:
            kept = {id(item) for item in slots['Ring']}
            ring_copies = [c for item, c in zip(original_rings, ring_copies) if id(item) in kept]
        pets = filter_items(pets, biomes)
        fixed = filter_items(fixed, biomes)
        searchable = {category: filter_items(items, biomes) for category, items in searchable.items()}
        # catalogue.py has level 20 stats; use each item's base (unupgraded) level instead
        weapons = [at_base_level(item) for item in weapons]
        slots = {slot: [at_base_level(item) for item in items] for slot, items in slots.items()}
        fixed = [at_base_level(item) for item in fixed]
        searchable = {category: [at_base_level(item) for item in items] for category, items in searchable.items()}
        log(f'Biomes: {len(biomes)} chosen -> {len(weapons)} weapons, ' + ', '.join(f"{len(v)} {k.lower()}" for k, v in slots.items()))
        if not weapons:
            raise ValueError(f'No {damage_type.lower()} weapon is available from the chosen biomes')
    # Every slot can stay empty (owned-item runs already offer it): with nothing available, or when an item adds nothing,
    # results show the slot as empty instead of a useless item
    for slot, items in slots.items():
        if not any(item.name == 'None' for item in items):
            slots[slot] = list(items) + [empty_item(slot)]
            if slot == 'Ring' and ring_copies is not None: ring_copies = list(ring_copies) + [2]
    settings = config['settings']
    prune = config['drop_dominated']
    # Magic DPS can drop when attack speed rises (mana runs out sooner): items only dominate with equal attack speed
    exact = exact_attributes(damage_type)
    perks = Character(config['skill_levels'], config['perk_trees']).perks
    worthless = worthless_attributes(damage_type, perks, list(weapons) + [i for items in slots.values() for i in items])
    unused = unused_attributes(damage_type) + worthless
    configured_pet = next((item for item in fixed if item.item_category == 'Pet'), None)
    all_pets = list(pets or []) # Before the configured pet narrows them (for Best)
    if not config.get('search_pets'):
        # Owned items: your own copies of the configured pet (with their talents); otherwise the configured entry
        own = [p for p in pets if configured_pet is not None and p.name == configured_pet.name] if config['save_filter']['enabled'] else []
        pets = own or None
    # Always-equipped items to search: every lantern / bag (or none) when asked for, and the pets
    options = {}
    for category, key in (('Lantern', 'search_lanterns'), ('Bag', 'search_bags')):
        if config.get(key):
            choices = [empty_item(category)] + searchable[category] # Empty first: it wins ties with items that add nothing
            if prune:
                choices = [choices[i] for i in undominated(choices, relevant_groups(settings, damage_type, worthless), exact=exact, unused=unused)]
            options[category] = choices
    if pets:
        options['Pet'] = pets
    # Best: candidates for the categories to pick one item for (Try all overrides it)
    try_all = {'Lantern': config.get('search_lanterns'), 'Bag': config.get('search_bags'), 'Pet': config.get('search_pets')}
    best_choices = {}
    for category in (c for c in ('Lantern', 'Bag', 'Pet') if c in (config.get('best_fixed') or {}).get(damage_type, []) and not try_all[c]):
        choices = all_pets if category == 'Pet' else [empty_item(category)] + searchable[category]
        if prune and (category != 'Pet' or not config['save_filter']['enabled']):
            choices = [choices[i] for i in undominated(choices, relevant_groups(settings, damage_type, worthless), exact=exact, unused=unused)]
        best_choices[category] = choices or [empty_item(category)]
    if 'Pet' in best_choices: # Best pet instead of the configured one
        options.pop('Pet', None)
        pets = None
    if best_choices and math.prod(len(c) for c in best_choices.values()) <= BEST_FIXED_SEARCH_ALL:
        options.update(best_choices) # Few enough to search them all
        best_choices = {}
    fixed = [item for item in fixed if item.item_category not in options and item.item_category not in best_choices]
    owned = (list(weapons), {slot: list(items) for slot, items in slots.items()}, list(ring_copies) if ring_copies is not None else None)
    if prune:
        weapons, slots, ring_copies = drop_dominated(weapons, slots, settings, ring_copies, damage_type, perks)
    if damage_type == 'Summoning':
        weapons = summoner_kits(weapons) # Tome + scepter pairs
        log(f"Summoner kits: {len(weapons)} (tome + scepter)" if any(w.scepter for w in weapons) else 'No scepter available: tomes alone (no curse)')
        if pets and not config['save_filter']['enabled']:
            # The catalogue's many pet versions, judged for the minions; pets you own are few, so all are tried (one that
            # only helps the scepter, e.g. Owlux's damage, still counts)
            options['Pet'] = [pets[i] for i in undominated(pets, relevant_groups(settings, damage_type, worthless), exact=exact, unused=unused)]
    for category, choices in options.items():
        if not choices: # Nothing left to try: no item in that slot
            options[category] = [empty_item(category)]
    extras = [list(combo) for combo in itertools.product(*options.values())] if options else None # Lantern x bag x pet
    keys = config['consumables'].get(damage_type, CONSUMABLES[damage_type])
    character_kwargs = dict(skill_levels=config['skill_levels'], perks=config['perk_trees'], food_effects=consumable_effects(keys, config.get('dish_rarity', DEFAULT_DISH_RARITY), config.get('golden_ingredients', True)),
                            potion_effects={}, settings=settings)
    def make_space(fixed_items):
        return SearchSpace(weapons, slots, fixed_items, character_kwargs, ring_copies=ring_copies,
                           prune_ring_pairs_for=relevant_groups(settings, damage_type, worthless) if prune else None, extras=extras, exact_attributes=exact,
                           unused_attributes=unused)
    if best_choices:
        fixed = fixed + pick_best_fixed(make_space(fixed), fixed, best_choices, character_kwargs, log, should_stop)
    space = make_space(fixed)
    for category, choices in options.items():
        log(f"Searching {len(choices)} {category.lower()} options: {', '.join(c.name for c in choices)}")

    outer = [len(slots[s]) for s in ['Helm', 'Breast armor', 'Pants armor']]
    n_loadouts = len(space.kits) * outer[0] * outer[1] * outer[2] * space.n_inner()
    n_groups = len(space.kits) * outer[0] * outer[1]
    description = f'Calculating DPS for {n_loadouts:,} loadouts'
    log(description)
    # Items that only count through their set appear only in loadouts that complete it (otherwise the same loadout with
    # that slot empty is equal): keep extra loadouts so the top N is still full after leaving those out
    candidates = list(weapons) + [i for items in slots.values() for i in items] + [i for option in extras or [] for i in option] + list(fixed)
    set_only = set_only_requirements(candidates, settings, damage_type, worthless)
    kept = config['top_n'] * (2 if set_only else 1)
    if progress is None:
        with tqdm(total=n_groups, desc=description) as bar:
            best, _ = search(space, kept, progress=bar, should_stop=should_stop)
    else:
        progress.start(n_groups, description)
        best, _ = search(space, kept, progress=progress, should_stop=should_stop)
    if set_only:
        best = [loadout for loadout in best if completes_sets(loadout_items(loadout, fixed), set_only)][:config['top_n']]

    fixed_names = {item.item_category: display_name(item) for item in fixed}
    def tail_name(searched, category):
        chosen = next((item for item in searched or [] if item.item_category == category), None)
        return display_name(chosen) if chosen is not None else fixed_names.get(category, 'None')
    results = pd.DataFrame([
        {'Weapon': display_name(weapon), 'Helm': display_name(helm), 'Breast armor': display_name(breast_armor), 'Pants armor': display_name(pants_armor),
         'Necklace': display_name(necklace), 'Ring1': display_name(ring1), 'Ring2': display_name(ring2), 'Offhand': display_name(offhand),
         'Lantern': tail_name(searched, 'Lantern'), 'Bag': tail_name(searched, 'Bag'), 'Pet': tail_name(searched, 'Pet'), 'DPS': dps}
        for dps, weapon, helm, breast_armor, pants_armor, necklace, ring1, ring2, offhand, searched in best
    ])
    output = config['output'].format(damage_type=damage_type.lower())
    os.makedirs(os.path.dirname(output) or '.', exist_ok=True)
    results.to_csv(output)
    stopped = bool(should_stop and should_stop())
    info = {'loadouts': n_loadouts, 'groups': n_groups, 'seconds': time.time() - start, 'output': output, 'stopped': stopped,
            # For dps_over_time: the best loadouts' items (in CSV order) and what every loadout shares
            'best_loadouts': best[:1000], 'fixed_items': fixed, 'character_kwargs': character_kwargs,
            'consumable_keys': keys, 'dish_rarity': config.get('dish_rarity', DEFAULT_DISH_RARITY), 'golden_ingredients': config.get('golden_ingredients', True)}
    if config['save_filter']['enabled'] and biomes is not None and config.get('suggest_upgrades', True) and not stopped:
        candidates = upgrade_candidates(damage_type, config, biomes, owned_names)
        suggest = lambda items, owned_items, baseline: suggest_upgrades(items, *owned_items, fixed, extras, character_kwargs, baseline, drop_dominated=prune,
                                                                        damage_type=damage_type, progress=progress, should_stop=should_stop, log=log)
        if best:
            rows = suggest(candidates, owned, best[0][0])
        else:
            # No loadout (no weapon of this type): the weapons to get first, then the rest as if you got the best of them
            rows = suggest([c for c in candidates if c.item_category == 'Weapon'], owned, 0)
            if rows and not (should_stop and should_stop()):
                top = next(c for c in candidates if c.item_category == 'Weapon' and c.name == rows[0]['Upgrade'])
                log(f"No {damage_type.lower()} weapon owned: weapons are ranked by the DPS they give; the other upgrades assume you get {top.name}")
                with_top = ([top] + list(owned[0]), owned[1], owned[2])
                more = suggest([c for c in candidates if c.item_category != 'Weapon'], with_top, rows[0]['DPS'])
                for row in more:
                    row['Uses'] = f"(with {top.name}) {row['Uses']}"
                rows += more
        upgrades = pd.DataFrame(rows, columns=UPGRADE_COLUMNS)
        info['upgrades'] = upgrades
        info['upgrades_output'] = os.path.splitext(output)[0] + '_upgrades.csv'
        upgrades.to_csv(info['upgrades_output'], index=False)
        log(f"{len(upgrades)} upgrades found (written to {info['upgrades_output']})" + (', best first:' if len(upgrades) else ''))
        for _, row in upgrades.head(10).iterrows():
            gain = f"+{row['Gain']:,} DPS ({row['Gain %']}%)" if pd.notna(row['Gain %']) else f"{row['DPS']:,} DPS (new weapon)"
            log(f"  {gain}  {row['Upgrade']}  [{row['Biome']}]  {row['Where to get']}")
        info['seconds'] = time.time() - start
    log(f"{'Stopped' if stopped else 'Done'} in {info['seconds']:.0f}s; {len(results):,} loadouts written to {output}")
    return results, info
