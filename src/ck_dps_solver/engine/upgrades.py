"""Upgrade suggestions: items from the chosen biomes you don't own yet, ranked by how much they raise your best DPS.

Each suggestion is the best loadout of your owned items plus that one new item (at its base level, as found).
Set pieces are also tried together (every missing piece of a set at once), since a set bonus can be worth more
than any single piece. Gains are exact for those additions, not estimates: each one is a full search.
"""
from concurrent.futures import ProcessPoolExecutor, FIRST_COMPLETED, wait
import os

from ck_dps_solver.model import Character
from ck_dps_solver.model.character import item_groups

from ck_dps_solver.engine.batch_search import SearchSpace, loadout_items, search
from ck_dps_solver.engine.dominance import completes_sets, drop_dominated, exact_attributes, relevant_groups, set_only_requirements, undominated, unused_attributes
from ck_dps_solver.model.item_stats import wiki_data
from ck_dps_solver.model.progression import item_biome
from ck_dps_solver.model.sources import _scene_name, is_seasonal, where_to_get
from ck_dps_solver.model.summoning import summoner_kits

TIES_KEPT = 20
SLOTS = ['Weapon', 'Helm', 'Breast armor', 'Pants armor', 'Necklace', 'Ring', 'Offhand']


def _slot(item):
    return 'Weapon' if item.item_category == 'Weapon' else item.item_category


def _with(owned_weapons, owned_slots, owned_ring_copies, additions):
    """Owned items plus new ones (new rings count as 2 copies: you can get two)"""
    weapons = list(owned_weapons) + [i for i in additions if _slot(i) == 'Weapon']
    slots = {slot: list(items) for slot, items in owned_slots.items()}
    ring_copies = list(owned_ring_copies) if owned_ring_copies is not None else None
    for item in additions:
        slot = _slot(item)
        if slot in slots:
            slots[slot].insert(0, item)
            if slot == 'Ring' and ring_copies is not None: ring_copies.insert(0, 2)
    return weapons, slots, ring_copies


def can_help(item, owned_weapons, owned_slots, owned_ring_copies, groups, damage_type=None):
    """False when an owned item in the same slot is at least as good in every stat (so the item can't raise DPS)"""
    slot = _slot(item)
    if slot == 'Weapon':
        return damage_type in ('Magic', 'Summoning', 'Explosives') or 0 in undominated([item] + list(owned_weapons), groups, unused=unused_attributes(damage_type))
    copies = [2] + list(owned_ring_copies) if slot == 'Ring' and owned_ring_copies is not None else None
    return 0 in undominated([item] + list(owned_slots[slot]), groups, copies=copies, exact=exact_attributes(damage_type), unused=unused_attributes(damage_type))


def bundles(candidates, owned_weapons, owned_slots, owned_ring_copies, settings, prefilter=True, damage_type=None):
    """Single items that could help, plus one bundle per set (in a modeled set bonus) with 2+ missing pieces"""
    groups = relevant_groups(settings, damage_type)
    singles = [[item] for item in candidates if not prefilter or can_help(item, owned_weapons, owned_slots, owned_ring_copies, groups, damage_type)]
    sets = set(wiki_data()['sets']) & groups
    by_set = {}
    for item in candidates:
        for group in item_groups(item) & sets:
            by_set.setdefault(group, []).append(item)
    return singles + [items for _, items in sorted(by_set.items()) if len(items) >= 2]


_context = None

def _init_worker(context):
    global _context
    _context = context

def _best_with(additions):
    """Best DPS (and loadout) with owned items plus `additions`"""
    c = _context
    weapons, slots, ring_copies = _with(c['weapons'], c['slots'], c['ring_copies'], additions)
    if c['drop_dominated']:
        perks = Character(c['character_kwargs']['skill_levels'], c['character_kwargs']['perks']).perks
        weapons, slots, ring_copies = drop_dominated(weapons, slots, c['settings'], ring_copies, c['damage_type'], perks)
    if len(additions) == 1:
        # A single new item only helps in loadouts that wear it: search its slot with just that item (rings pair with
        # other rings, and Summoning weapons pair a tome with a scepter, so those slots stay whole)
        item = additions[0]
        slot = _slot(item)
        if slot == 'Weapon' and c['damage_type'] != 'Summoning':
            weapons = [item]
        elif slot in slots and slot != 'Ring':
            slots[slot] = [item]
    if c['damage_type'] == 'Summoning':
        weapons = summoner_kits(weapons)
    space = SearchSpace(weapons, slots, c['fixed'], c['character_kwargs'], ring_copies=ring_copies,
                        prune_ring_pairs_for=relevant_groups(c['settings'], c['damage_type']) if c['drop_dominated'] else None, extras=c['extras'],
                        exact_attributes=exact_attributes(c['damage_type']), unused_attributes=unused_attributes(c['damage_type']))
    # Only loadouts that beat the current best matter. A few are kept so that among exact ties the one with empty slots
    # wins (search sorts ties empty-first), instead of one wearing an item that adds nothing
    best, _ = search(space, TIES_KEPT, workers=1, min_dps=c['baseline'])
    # An item that only counts through its set is left out unless the loadout completes the set (see run_search)
    candidates = list(weapons) + [i for items in slots.values() for i in items] + [i for option in c['extras'] or [] for i in option] + list(c['fixed'])
    set_only = set_only_requirements(candidates, c['settings'], c['damage_type'])
    best = [loadout for loadout in best if completes_sets(loadout_items(loadout, c['fixed']), set_only)]
    return best[0] if best else None


def suggest_upgrades(candidates, owned_weapons, owned_slots, owned_ring_copies, fixed, extras, character_kwargs, baseline,
                     drop_dominated=True, damage_type=None, progress=None, should_stop=None, log=print, workers=None):
    """
    Ranked upgrades: list of dicts (Upgrade, Slot, DPS, Gain, Gain %, Biome, Seasonal, Uses, Where to get), best first.
    candidates: new items to try (not owned). owned_*: the items of the owned search (with empty slots).
    baseline: best DPS with owned items only.
    """
    settings = character_kwargs['settings']
    tasks = bundles(candidates, owned_weapons, owned_slots, owned_ring_copies, settings, prefilter=drop_dominated, damage_type=damage_type)
    log(f'Upgrades: {len(candidates)} new items from the chosen biomes; trying {len(tasks)} (others are beaten by an item you own)')
    if progress is not None: progress.start(len(tasks), f'Trying {len(tasks)} upgrades')
    context = dict(weapons=owned_weapons, slots=owned_slots, ring_copies=owned_ring_copies, fixed=fixed, extras=extras, baseline=baseline,
                   character_kwargs=character_kwargs, settings=settings, drop_dominated=drop_dominated, damage_type=damage_type)
    found = []
    with ProcessPoolExecutor(max_workers=workers or os.cpu_count(), initializer=_init_worker, initargs=(context,)) as executor:
        pending = {executor.submit(_best_with, additions): additions for additions in tasks}
        while pending:
            if should_stop is not None and should_stop():
                executor.shutdown(wait=True, cancel_futures=True)
                break
            done, _ = wait(pending, return_when=FIRST_COMPLETED, timeout=0.5)
            for future in done:
                additions = pending.pop(future)
                best = future.result()
                if progress is not None: progress.update(1)
                if best is None or best[0] <= baseline: continue
                loadout = [item for item in best[1:-1] if item is not None] + list(best[-1] or [])
                used = [item for item in additions if any(item is i or (item.name == i.name and item.level == i.level) for i in loadout)]
                found.append((best, additions, used))

    rows, seen = [], set()
    for best, additions, used in sorted(found, key=lambda f: -f[0][0]):
        key = tuple(sorted(i.name for i in used))
        if not used or key in seen: continue # A set bundle whose best loadout only uses one piece repeats that single item
        seen.add(key)
        dps = best[0]
        set_name = next(iter(item_groups(additions[0]) & set(wiki_data()['sets'])), None) if len(additions) > 1 else None
        rows.append({
            'Upgrade': ' + '.join(i.name for i in used) + (f' ({_scene_name(set_name)})' if set_name else ''),
            'Slot': ', '.join(dict.fromkeys(_slot(i) for i in used)),
            'DPS': dps, 'Gain': dps - baseline, 'Gain %': round(100 * (dps - baseline) / baseline, 1) if baseline else None,
            'Biome': ', '.join(dict.fromkeys(item_biome(i) or '?' for i in used)),
            'Seasonal': 'Yes' if any(is_seasonal(i.name) for i in used) else '',
            'Uses': ' | '.join(f'{label}: {item.name}' for label, item in list(zip(['Weapon', 'Helm', 'Breast', 'Pants', 'Necklace', 'Ring', 'Ring', 'Offhand'], best[1:-1]))
                               + [(i.item_category, i) for i in best[-1] or []] if item is not None and item.name != 'None'),
            'Where to get': ' || '.join(f'{i.name}: {where_to_get(i.name)}' for i in used),
        })
    return rows
