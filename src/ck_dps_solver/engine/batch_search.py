"""Loadout search.

For each (weapon, helm, breast armor, pants) a compiled loop (numba) scores every necklace x ring pair x offhand
combination, using the same set bonus table and DPS formula (engine/dps_utils.dps_core) as the single-loadout path
(Character + calculate_dps). Effects are summed in the same order as Character.get_active_effects, so the results
are identical, not approximate. Work is spread over processes, one per CPU thread.
"""
from concurrent.futures import Future, ProcessPoolExecutor, FIRST_COMPLETED, wait
import hashlib
import itertools
import os

import numba
import numpy as np

from ck_dps_solver.engine.dominance import undominated_pairs
from ck_dps_solver.engine.dps_utils import CACHE, FORMULA_SETS, dps_core_compiled, dps_from_effects, params
from ck_dps_solver.model import Character
from ck_dps_solver.model.character import ACTIVE_EFFECTS_DICT, SET_BONUSES, item_groups, set_bonus_value

ATTRIBUTES = list(ACTIVE_EFFECTS_DICT.keys())


def _clear_stale_kernel_cache():
    """numba caches the compiled kernel below by this file only, but the kernel inlines the DPS formula from
    engine/dps_utils.py (and attribute lists from model/). When those change, drop the cached kernel so it recompiles."""
    here = os.path.dirname(os.path.abspath(__file__))
    cache_dir = os.path.join(here, '__pycache__')
    if os.environ.get('NUMBA_CACHE_DIR'): # Packaged app: numba keeps its cache in a user folder (paths.py)
        cache_dir = os.environ['NUMBA_CACHE_DIR']
    sources = [os.path.join(here, 'dps_utils.py')] + [os.path.join(os.path.dirname(here), 'model', f) for f in ('character.py', 'item.py')]
    if not all(os.path.exists(f) for f in sources): # Packaged without sources: no cache to keep current
        return
    digest = hashlib.sha256(b''.join(open(f, 'rb').read() for f in sources)).hexdigest()
    stamp = os.path.join(cache_dir, 'batch_search_formula.sha256')
    try:
        if open(stamp).read() == digest:
            return
    except OSError:
        pass
    os.makedirs(cache_dir, exist_ok=True)
    for folder, _, names in os.walk(cache_dir): # numba's own folder layout under NUMBA_CACHE_DIR
        for name in names:
            if name.startswith('batch_search.') and (name.endswith('.nbi') or name.endswith('.nbc')):
                try: os.remove(os.path.join(folder, name))
                except OSError: pass
    with open(stamp, 'w') as f:
        f.write(digest)

_clear_stale_kernel_cache()
BOUNDS_DISABLED = os.environ.get('CK_DISABLE_BOUNDS') == '1' # For testing: search every loadout
OUTER_SLOTS = ['Helm', 'Breast armor', 'Pants armor']
INNER_SLOTS = ['Necklace', 'Ring1', 'Ring2', 'Offhand']


class SlotTable:
    """Reinforced attribute values (items x attributes) and set membership for one equipment slot"""
    def __init__(self, items, set_names):
        for item in items: item.reinforce()
        self.items = items
        self.names = [item.name for item in items]
        self.values = np.array([[item.attributes[k] for k in ATTRIBUTES] for item in items], dtype=float).reshape(len(items), len(ATTRIBUTES))
        self.sets = np.array([[s in item_groups(item) for s in set_names] for item in items], dtype=np.int16).reshape(len(items), len(set_names))


class SearchSpace:
    def __init__(self, weapons, slots, tail_items, character_kwargs, ring_copies=None, prune_ring_pairs_for=None, pets=None, exact_attributes=(), unused_attributes=(),
                 extras=None):
        """
        weapons: list of Weapon. slots: {'Helm', 'Breast armor', 'Pants armor', 'Necklace', 'Ring', 'Offhand'} -> list of Item.
        tail_items: items equipped in every loadout after the offhand, in Character.items order (e.g. lantern, bag, pet).
        character_kwargs: arguments for Character (skill_levels, perks, food_effects, potion_effects, settings).
        ring_copies: copies available of each ring in slots['Ring'] (default: unlimited). A ring can be worn twice only with 2+ copies.
        prune_ring_pairs_for: relevant sets/groups (utils.dominance.relevant_groups); if given, drop ring pairs another pair dominates.
        pets: pets to search (tail_items then shouldn't include a pet). Each weapon and pet pair is a 'kit'; without pets, one kit per weapon.
        extras: instead of pets, always-equipped options to search: each a list of items (e.g. a lantern, a bag and a pet;
            tail_items then shouldn't include those categories). Each weapon and option pair is a kit.
        exact_attributes: attributes that must be equal for a ring pair to dominate another (utils.dominance.exact_attributes).
        unused_attributes: attributes ring pair dominance ignores (utils.dominance.unused_attributes).
        """
        if extras is None and pets:
            extras = [[pet] for pet in pets]
        all_items = list(weapons) + list(tail_items) + [item for option in extras or [] for item in option] + [item for items in slots.values() for item in items]
        self.set_names = sorted({group for item in all_items for group in item_groups(item)})
        self.weapons = SlotTable(list(weapons), self.set_names)
        self.tail = SlotTable(list(tail_items), self.set_names)
        self.extras = [SlotTable(list(option), self.set_names) for option in extras] if extras else None
        self.kits = [(w, e) for w in range(len(self.weapons.names)) for e in (range(len(self.extras)) if self.extras else [None])]
        self.outer = {slot: SlotTable(slots[slot], self.set_names) for slot in OUTER_SLOTS}
        self.necklaces = SlotTable(slots['Necklace'], self.set_names)
        self.rings = SlotTable(slots['Ring'], self.set_names)
        self.offhands = SlotTable(slots['Offhand'], self.set_names)
        self.character_kwargs = character_kwargs

        # Ring pairs: order doesn't matter. Ring1 is the name that sorts last (matches the solver's CSV convention),
        # and for two copies with the same name, the one listed first.
        ring_copies = ring_copies if ring_copies is not None else [2] * len(self.rings.names)
        ring_order = lambda i: (self.rings.names[i], -i)
        pairs = [(max(a, b, key=ring_order), min(a, b, key=ring_order))
                 for a, b in itertools.combinations_with_replacement(range(len(self.rings.names)), 2) if a != b or ring_copies[a] >= 2]
        self.ring_pairs = np.array(pairs, dtype=np.int32).reshape(-1, 2)
        if prune_ring_pairs_for is not None and len(pairs):
            pair_values = self.rings.values[self.ring_pairs[:, 0]] + self.rings.values[self.ring_pairs[:, 1]]
            # Pairs in a relevant set, and pairs with an empty slot (so a ring that adds nothing can show as empty), are kept
            has_groups = [bool((item_groups(self.rings.items[a]) | item_groups(self.rings.items[b])) & prune_ring_pairs_for)
                          or 'None' in (self.rings.items[a].name, self.rings.items[b].name) for a, b in pairs]
            self.ring_pairs = self.ring_pairs[undominated_pairs(pair_values, has_groups, exact_attributes, unused_attributes)]

        n_neck, n_pairs, n_off = len(self.necklaces.names), len(self.ring_pairs), len(self.offhands.names)
        neck_idx, pair_idx, off_idx = [a.ravel() for a in np.meshgrid(np.arange(n_neck), np.arange(n_pairs), np.arange(n_off), indexing='ij')]
        self.inner_index = (neck_idx, pair_idx, off_idx)
        ring1_idx, ring2_idx = self.ring_pairs[pair_idx, 0], self.ring_pairs[pair_idx, 1]
        # Set pieces from the inner slots; two copies of the same ring (same name) count once
        ring_names = np.array(self.rings.names, dtype=object)
        same_ring = ring_names[ring1_idx] == ring_names[ring2_idx]
        ring2_sets = np.where(same_ring[:, None], 0, self.rings.sets[ring2_idx])
        self.inner_sets = (self.necklaces.sets[neck_idx] + self.rings.sets[ring1_idx] + ring2_sets + self.offhands.sets[off_idx]).T
        # Inputs for the compiled evaluation
        self.kernel_index = tuple(np.ascontiguousarray(a, dtype=np.int64) for a in (neck_idx, ring1_idx, ring2_idx, off_idx))
        # Only sets that a set bonus or the formula uses are counted per loadout
        used = {s for _, _, _, required, _ in SET_BONUSES for s in required} | set(FORMULA_SETS)
        self.tracked_sets = [s for s in self.set_names if s in used]
        tracked_rows = [self.set_names.index(s) for s in self.tracked_sets]
        self.inner_sets_i64 = np.ascontiguousarray(self.inner_sets[tracked_rows], dtype=np.int64).reshape(len(tracked_rows), len(neck_idx)) # Explicit width: no tracked sets is possible
        self.formula_index = np.array([self.tracked_sets.index(s) if s in self.tracked_sets else -1 for s in FORMULA_SETS], dtype=np.int64)

        self._weapon_context = {}
        self._kernel_tables = {}

    def n_inner(self): return len(self.inner_index[0])

    def kit_tail(self, kit):
        """Items equipped after the offhand for a kit (lantern, bag, pet: the fixed ones and the kit's option): items, values, set membership"""
        _, option = self.kits[kit]
        if option is None:
            return self.tail.items, self.tail.values, self.tail.sets
        extra = self.extras[option]
        return (self.tail.items + extra.items, np.vstack([self.tail.values, extra.values]), np.vstack([self.tail.sets, extra.sets]))

    def weapon_context(self, kit):
        """Character effects (which depend on the weapon) and consumables, as ordered value lists per attribute"""
        if kit not in self._weapon_context:
            weapon_index = self.kits[kit][0]
            character = Character(**self.character_kwargs)
            character.equip(self.weapons.items[weapon_index])
            for item in self.kit_tail(kit)[0]: character.equip(item)
            character_effects = character.get_character_active_effects()
            consumables_effects = character.get_consumables_active_effects()
            constants = {k: list(character_effects[k].values()) + list(consumables_effects[k].values()) for k in ATTRIBUTES}
            set_bonuses = [(attribute, set_bonus_value(value, character.perks), required, setting) for attribute, _, value, required, setting in SET_BONUSES
                           if setting is None or character.settings[setting]]
            self._weapon_context[kit] = (character, constants, set_bonuses)
        return self._weapon_context[kit]

    def kernel_tables(self, kit):
        """Arrays for the compiled evaluation: set bonuses, talent/food constants and formula inputs for a kit"""
        if kit not in self._kernel_tables:
            character, constants, set_bonuses = self.weapon_context(kit)
            set_index = {s: i for i, s in enumerate(self.tracked_sets)}
            # Set bonuses that can apply (a required set no item belongs to can never be completed)
            usable = [(attribute, value, required) for attribute, value, required, _ in set_bonuses
                      if value != 0 and all(s in set_index for s in required)]
            bonus_attr = np.array([ATTRIBUTES.index(a) for a, _, _ in usable], dtype=np.int64)
            bonus_value = np.array([v for _, v, _ in usable], dtype=np.float64)
            # Requirements as flat lists: bonus b needs req_n[i] pieces of tracked set req_set[i] for req_start[b] <= i < req_start[b + 1]
            req_start = np.zeros(len(usable) + 1, dtype=np.int64)
            req_set, req_n = [], []
            for b, (_, _, required) in enumerate(usable):
                for s, n in required.items():
                    req_set.append(set_index[s]); req_n.append(n)
                req_start[b + 1] = len(req_set)
            bonus_req = (req_start, np.array(req_set, dtype=np.int64), np.array(req_n, dtype=np.int64))
            n_const = max([len(constants[k]) for k in ATTRIBUTES] + [1])
            const_vals = np.zeros((len(ATTRIBUTES), n_const), dtype=np.float64)
            const_n = np.zeros(len(ATTRIBUTES), dtype=np.int64)
            for ki, k in enumerate(ATTRIBUTES):
                const_vals[ki, :len(constants[k])] = constants[k]
                const_n[ki] = len(constants[k])
            p = params(character.items['Weapon'], character.perks, character.settings)
            self._kernel_tables[kit] = (bonus_attr, bonus_value, bonus_req, const_vals, const_n, p)
        return self._kernel_tables[kit]

    def evaluate(self, kit, helm, breast_armor, pants_armor):
        """DPS for every necklace x ring pair x offhand combination with the given kit (weapon and pet)/helm/breast armor/pants"""
        outer = [(self.weapons, self.kits[kit][0]), (self.outer['Helm'], helm), (self.outer['Breast armor'], breast_armor), (self.outer['Pants armor'], pants_armor)]
        _, tail_values, tail_sets = self.kit_tail(kit)
        outer_rows = np.array([table.values[i] for table, i in outer], dtype=np.float64)
        outer_counts = np.array([sum(int(table.sets[i, self.set_names.index(s)]) for table, i in outer) + int(tail_sets[:, self.set_names.index(s)].sum())
                                 for s in self.tracked_sets], dtype=np.int64)
        bonus_attr, bonus_value, bonus_req, const_vals, const_n, p = self.kernel_tables(kit)
        out = np.empty(self.n_inner(), dtype=np.int64)
        _evaluate_kernel(outer_rows, outer_counts, self.necklaces.values, self.rings.values, self.offhands.values, np.ascontiguousarray(tail_values, dtype=np.float64),
                         self.kernel_index[0], self.kernel_index[1], self.kernel_index[2], self.kernel_index[3], self.inner_sets_i64,
                         bonus_attr, bonus_value, bonus_req[0], bonus_req[1], bonus_req[2], const_vals, const_n, self.formula_index, p, out)
        return out

    def _slot_maxima(self):
        """Per-attribute maximum each searched slot can contribute (rings: the best ring pair)"""
        if not hasattr(self, '_maxima'):
            pair_values = self.rings.values[self.ring_pairs[:, 0]] + self.rings.values[self.ring_pairs[:, 1]]
            self._maxima = {'Pants armor': self.outer['Pants armor'].values.max(axis=0), 'Necklace': self.necklaces.values.max(axis=0),
                            'Ring pair': pair_values.max(axis=0), 'Offhand': self.offhands.values.max(axis=0)}
        return self._maxima

    def upper_bound(self, kit, helm, breast_armor, pants_armor=None):
        """A DPS no loadout with this weapon/helm/breast armor (and pants, if given) can exceed.
        DPS never decreases when a stat increases, so each remaining slot contributes its per-stat maximum and every
        set bonus counts as active. Magic: with unlimited mana (more attack speed can lower real magic DPS by running
        out of mana sooner, but never above the unlimited-mana DPS)."""
        character, constants, set_bonuses = self.weapon_context(kit)
        maxima = self._slot_maxima()
        outer = [self.weapons.values[self.kits[kit][0]], self.outer['Helm'].values[helm], self.outer['Breast armor'].values[breast_armor]]
        outer.append(maxima['Pants armor'] if pants_armor is None else self.outer['Pants armor'].values[pants_armor])
        total = np.sum(outer, axis=0) + maxima['Necklace'] + maxima['Ring pair'] + maxima['Offhand'] + self.kit_tail(kit)[1].sum(axis=0)
        active_effects = {k: float(total[ki]) for ki, k in enumerate(ATTRIBUTES)}
        for attribute, value, _, _ in set_bonuses:
            if value > 0: active_effects[attribute] += value
        for k in ATTRIBUTES:
            active_effects[k] += sum(constants[k])
        all_sets = {set_name: 1000 for set_name in self.set_names}
        bound = float(dps_from_effects(character.items['Weapon'], character.perks, character.settings, active_effects, all_sets, optimistic=True))
        return bound * (1 + 1e-9) + 2 # Margin for floating point rounding


@numba.njit(cache=CACHE)
def _evaluate_kernel(outer_rows, outer_counts, neck_values, ring_values, off_values, tail_values, neck_idx, ring1_idx, ring2_idx, off_idx,
                     inner_sets, bonus_attr, bonus_value, req_start, req_set, req_n, const_vals, const_n, formula_index, p, out):
    """Compiled loop over inner combinations. Attributes are summed in Character.get_active_effects order (weapon, helm,
    breast armor, pants, necklace, ring 1, ring 2, offhand, lantern/bag/pet, set bonuses, talents and consumables), so
    the floating point results match the single-loadout path exactly."""
    n_attr = outer_rows.shape[1]
    n_sets = inner_sets.shape[0]
    base = np.zeros(n_attr)
    for k in range(n_attr):
        total = 0.0
        for r in range(outer_rows.shape[0]):
            total = total + outer_rows[r, k]
        base[k] = total
    e = np.empty(n_attr)
    set_counts = np.empty(n_sets, dtype=np.int64)
    counts = np.empty(formula_index.shape[0], dtype=np.int64)
    for j in range(neck_idx.shape[0]):
        for k in range(n_attr):
            total = base[k] + neck_values[neck_idx[j], k]
            total = total + ring_values[ring1_idx[j], k]
            total = total + ring_values[ring2_idx[j], k]
            total = total + off_values[off_idx[j], k]
            for r in range(tail_values.shape[0]):
                total = total + tail_values[r, k]
            e[k] = total
        for s in range(n_sets):
            set_counts[s] = outer_counts[s] + inner_sets[s, j]
        for b in range(bonus_attr.shape[0]):
            active = True
            for i in range(req_start[b], req_start[b + 1]):
                if set_counts[req_set[i]] < req_n[i]:
                    active = False
                    break
            if active:
                e[bonus_attr[b]] = e[bonus_attr[b]] + bonus_value[b]
        for k in range(n_attr):
            for c in range(const_n[k]):
                e[k] = e[k] + const_vals[k, c]
        for f in range(formula_index.shape[0]):
            counts[f] = set_counts[formula_index[f]] if formula_index[f] >= 0 else 0
        out[j] = dps_core_compiled(e, counts, p)


_space = None

def _init_worker(space):
    global _space
    _space = space

def _search_task(kit, helm, breast_armor, threshold, top_n):
    """Best loadouts (at or above threshold) for one weapon/helm/breast armor, over every pants and inner combination"""
    dps_parts, index_parts = [], []
    for pants_armor in range(len(_space.outer['Pants armor'].names)):
        if threshold > -np.inf and not BOUNDS_DISABLED and _space.upper_bound(kit, helm, breast_armor, pants_armor) < threshold:
            continue # No combination with these pants can make the top N
        dps = _space.evaluate(kit, helm, breast_armor, pants_armor)
        keep = np.flatnonzero(dps >= threshold)
        if len(keep) > top_n: keep = keep[np.argpartition(-dps[keep], top_n - 1)[:top_n]]
        dps_parts.append(dps[keep])
        index_parts.append(np.column_stack([np.full(len(keep), pants_armor), keep]))
    if not dps_parts:
        return kit, helm, breast_armor, np.empty(0, dtype=np.int64), np.empty((0, 2), dtype=np.int64)
    dps = np.concatenate(dps_parts)
    index = np.concatenate(index_parts)
    if len(dps) > top_n:
        best = np.argpartition(-dps, top_n - 1)[:top_n]
        dps, index = dps[best], index[best]
    return kit, helm, breast_armor, dps.astype(np.int64), index


class _InlineExecutor:
    """Runs tasks in this process as they're submitted (workers=1: small searches, or searches inside a worker)"""
    def __init__(self, initializer, initargs):
        initializer(*initargs)
    def submit(self, fn, *args):
        future = Future()
        future.set_result(fn(*args))
        return future
    def shutdown(self, wait=True, cancel_futures=False):
        pass
    def __enter__(self):
        return self
    def __exit__(self, *exc):
        return False


def search(space: SearchSpace, top_n, workers=None, progress=None, should_stop=None, min_dps=None):
    """Top `top_n` loadouts as a list of (dps, weapon, helm, breast armor, pants, necklace, ring1, ring2, offhand, pet) items
    (the last field is the kit's searched items, e.g. [pet] or [lantern, bag, pet]; None unless the space searches pets or extras).
    progress: object with update(n), called once per (weapon, helm, breast armor) group.
    workers: processes (default: one per CPU thread); 1 runs in this process.
    should_stop: callable; when it returns True the search stops early and returns the best loadouts found so far.
    min_dps: only loadouts with at least this DPS are wanted (e.g. upgrades must reach the current best): groups that
        can't reach it are skipped from the start.

    Exact: (weapon, helm, breast armor) groups are searched from the highest DPS upper bound down, and a group is
    skipped only when its upper bound is below the current N-th best DPS, so it can't contribute to the top N."""
    tasks = [(k, h, b) for k in range(len(space.kits)) for h in range(len(space.outer['Helm'].names)) for b in range(len(space.outer['Breast armor'].names))]
    bounds = {task: space.upper_bound(*task) for task in tasks}
    tasks.sort(key=lambda task: -bounds[task])
    workers = workers or os.cpu_count()
    best_dps = np.empty(0, dtype=np.int64)
    best_rows = np.empty((0, 5), dtype=np.int64) # weapon, helm, breast armor, pants, inner combination
    threshold = -np.inf if min_dps is None else min_dps

    pool = _InlineExecutor(_init_worker, (space,)) if workers == 1 else ProcessPoolExecutor(max_workers=workers, initializer=_init_worker, initargs=(space,))
    with pool as executor:
        pending, task_iter = set(), iter(tasks)
        def submit_next():
            for task in task_iter:
                if bounds[task] < threshold:
                    if progress is not None: progress.update(1) # Can't make the top N
                    continue
                pending.add(executor.submit(_search_task, *task, threshold, top_n))
                return
        for _ in range(workers * 2): submit_next()
        while pending:
            if should_stop is not None and should_stop():
                for future in pending: future.cancel()
                executor.shutdown(wait=True, cancel_futures=True)
                break
            done, _ = wait(pending, return_when=FIRST_COMPLETED, timeout=0.5)
            for future in done:
                pending.remove(future)
                kit, helm, breast_armor, dps, index = future.result()
                rows = np.column_stack([np.full(len(dps), kit), np.full(len(dps), helm), np.full(len(dps), breast_armor), index])
                best_dps = np.concatenate([best_dps, dps])
                best_rows = np.concatenate([best_rows, rows.reshape(-1, 5)])
                if len(best_dps) > top_n:
                    keep = np.argpartition(-best_dps, top_n - 1)[:top_n]
                    best_dps, best_rows = best_dps[keep], best_rows[keep]
                    threshold = best_dps.min()
                if progress is not None: progress.update(1)
                submit_next()

    neck_idx, pair_idx, off_idx = space.inner_index
    results = []
    for dps, (k, h, b, p, inner) in zip(best_dps, best_rows):
        ring1, ring2 = space.ring_pairs[pair_idx[inner]]
        w, pet = space.kits[k]
        results.append((int(dps), space.weapons.items[w], space.outer['Helm'].items[h], space.outer['Breast armor'].items[b], space.outer['Pants armor'].items[p],
                        space.necklaces.items[neck_idx[inner]], space.rings.items[ring1], space.rings.items[ring2], space.offhands.items[off_idx[inner]],
                        list(space.extras[pet].items) if pet is not None else None))
    # Ties: empty slots first, so an item that adds nothing (e.g. a lone set piece) isn't shown as if it helped
    results.sort(key=lambda r: (-r[0], [(item.name != 'None', item.name, item.level or 0) for item in list(r[1:-1]) + (r[-1] or [])]))
    return results, len(tasks)


def loadout_items(loadout, fixed):
    """The items a search result loadout equips: its slots, its searched always-equipped items (lantern, bag, pet), and the
    fixed ones it doesn't replace. loadout: (dps, weapon, helm, breast armor, pants, necklace, ring1, ring2, offhand, searched)"""
    searched = loadout[-1] or []
    replaced = {item.item_category for item in searched}
    return [item for item in loadout[1:-1] if item is not None] + list(searched) + [item for item in fixed if item.item_category not in replaced]
