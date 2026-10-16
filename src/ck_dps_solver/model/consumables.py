"""Food and potions as named effect sources, from the wiki's item data.

Sources:
  - Potions and other things you drink or eat as they are (their effects when consumed)
  - Dishes: a cooked meal with the ingredient, at its cooked effect x the dish's rarity bonus. Cooking (wiki): a dish has
    the strongest of each effect of its two ingredients; rare dishes get +25% and epic +50% on effects, and another
    x1.15 if both ingredients are golden. Dishes with a golden ingredient come out rare (checked in game: Tornis
    Kingfish + Golden Bloat Oat gives 63% damage = 50.4% x 1.25); epic only by chance with the Master chef talent.
    Golden ingredients are assumed cooked with another golden one.

Each source has the biome it comes from (the wiki's area), so biome checks can use only what's available.

Owned dishes (read from a save) are exact: key 'cooked:<dish object>:<variation>', where the variation holds the two
ingredients. Their effects are the strongest of each effect of the two ingredients x the dish's own rarity (x1.15 when
both ingredients are golden), whatever the dish rarity setting says. lookup() resolves every kind of key.

Planned dishes (the cooking planner, model/cooking.py) use key 'pair:<ingredient>+<ingredient>'.

Stacking follows the game's condition data: an effect that isn't "additive with itself" only counts once, from the
strongest source that has it. Different effects stack, e.g. a dish's damage and a potion's "damage from potion".
Set STACK_SAME_EFFECT to True to add up same-effect sources instead.
"""
from dataclasses import dataclass
import functools
import re

from ck_dps_solver.model.item_stats import CONDITION_ATTRIBUTES, scale_condition, wiki_data
from ck_dps_solver.model.progression import _BIOME_OF_AREA

DISH_RARITIES = {'Common': 1.0, 'Rare': 1.25, 'Epic': 1.5} # Bonus on a dish's effects
DEFAULT_DISH_RARITY = 'Rare'
GOLDEN_PAIR_MULTIPLIER = 1.15 # Rare or epic dish with both ingredients golden
STACK_SAME_EFFECT = False
KINDS = ['Potion', 'Dish', 'Food']
# Effects left out of the defaults (still selectable): Oblidra's Heart's damage aura, a boss drop
DEFAULT_SKIP = {'AuraApplyDamageIncrease'}


@dataclass(frozen=True)
class Source:
    key: str      # Stable id, e.g. 'dish:GoldenSunrice'
    name: str     # e.g. 'Golden Sunrice dish'
    kind: str     # 'Potion', 'Dish' (cooked) or 'Food' (eaten raw)
    biome: str    # Biome it comes from (model/progression.py), or None if unknown
    effects: tuple  # ((condition id, attribute, value), ...) for the effects the solver uses

    def describe(self):
        return ', '.join(format_effect(attribute, value) for _, attribute, value in self.effects)


def format_effect(attribute, value):
    label = attribute[2:].replace('_', ' ')
    if attribute.startswith('%_'):
        return f'+{value * 100:.3g}% {label}'
    return f'+{value:g} {label}'


def _effects(conditions, multiplier=1.0):
    found = []
    for condition in conditions:
        attribute = CONDITION_ATTRIBUTES.get(condition['id'])
        if attribute is None or not condition.get('value'):
            continue
        value = scale_condition(condition['id'], condition['value']) * multiplier
        found.append((condition['id'], attribute, round(value, 4) if attribute.startswith('%_') else round(value, 1)))
    return tuple(found)


@functools.lru_cache(maxsize=None)
def sources(dish_rarity=DEFAULT_DISH_RARITY, golden=True):
    """Every food and potion with an effect the solver uses, by key (dish values for the given dish rarity).
    golden=False: no golden ingredients, so no golden dishes, and dishes are common (rarity needs a golden ingredient)."""
    if not golden:
        dish_rarity = 'Common'
    found = {}
    for internal_id, record in sorted(wiki_data().get('consumables', {}).items(), key=lambda kv: kv[1]['name']):
        if not golden and record['rareIngredient']:
            continue
        biome = _BIOME_OF_AREA.get(record.get('area'))
        raw = _effects(record['conditions'])
        if raw:
            kind = 'Potion' if 'Potion' in record['categories'] else 'Food'
            found[f'{kind.lower()}:{internal_id}'] = Source(f'{kind.lower()}:{internal_id}', record['name'], kind, biome, raw)
        multiplier = DISH_RARITIES[dish_rarity]
        if dish_rarity != 'Common' and record['rareIngredient']:
            multiplier *= GOLDEN_PAIR_MULTIPLIER
        cooked = _effects(record['cooked'], multiplier)
        if cooked:
            found[f'dish:{internal_id}'] = Source(f'dish:{internal_id}', f"{record['name']} dish", 'Dish', biome, cooked)
    return found


def cooked_key(internal_id, variation):
    """Key of a dish as a save stores it (dish object, e.g. 'CookedCerealRare', and the variation holding its ingredients)"""
    return f'cooked:{internal_id}:{variation}'


def cooked_parts(key):
    """(dish name, ingredient records, effect multiplier) of an owned dish key, or None if it can't be read"""
    try:
        _, internal_id, variation = key.split(':')
        variation = int(variation)
    except ValueError:
        return None
    by_number = _objects_by_number()
    records = wiki_data().get('consumables', {})
    ingredients = [by_number.get(variation & 0xFFFF), by_number.get(variation >> 16)]
    found = [records[i] for i in ingredients if i in records]
    if not found:
        return None
    rarity = 'Epic' if internal_id.endswith('Epic') else 'Rare' if internal_id.endswith('Rare') else 'Common'
    multiplier = DISH_RARITIES[rarity]
    if rarity != 'Common' and len(found) == 2 and all(r['rareIngredient'] for r in found):
        multiplier *= GOLDEN_PAIR_MULTIPLIER
    base = re.sub(r'(?<=[a-z])(?=[A-Z])', ' ', re.sub(r'^Cooked|Rare$|Epic$', '', internal_id)) # 'CookedPanCurryRare' -> 'Pan Curry'
    dish = f'{rarity} {base}' if rarity != 'Common' else base
    return f"{dish} ({' + '.join(r['name'] for r in found)})", found, multiplier


def cooked_conditions(key):
    """(conditions, multiplier) of an owned dish: the strongest of each effect of its ingredients (unscaled values)"""
    parts = cooked_parts(key)
    if parts is None:
        return [], 1.0
    _, records, multiplier = parts
    best = {}
    for record in records:
        for condition in record['cooked']:
            if condition['id'] not in best or (condition.get('value') or 0) > (best[condition['id']].get('value') or 0):
                best[condition['id']] = condition
    return list(best.values()), multiplier


@functools.lru_cache(maxsize=None)
def _objects_by_number():
    return {record['id']: internal_id for internal_id, record in wiki_data()['objects'].items()}


@functools.lru_cache(maxsize=None)
def cooked_source(key):
    parts = cooked_parts(key)
    if parts is None:
        return None
    conditions, multiplier = cooked_conditions(key)
    effects = _effects(conditions, multiplier)
    return Source(key, parts[0], 'Dish', None, effects) if effects else None


def pair_key(first, second):
    """Key of a dish you could cook from two ingredients (internal ids; the order doesn't matter)"""
    return 'pair:' + '+'.join(sorted((first, second)))


def pair_dish(first, second):
    """(name, conditions, multiplier) of the dish two ingredients make: the strongest of each of their cooked effects,
    common without a golden ingredient, rare with one (x1.15 more when both are golden; epic needs luck, so isn't planned)"""
    records = wiki_data().get('consumables', {})
    found = [records[first], records[second]]
    best = {}
    for record in found:
        for condition in record['cooked']:
            if condition['id'] not in best or (condition.get('value') or 0) > (best[condition['id']].get('value') or 0):
                best[condition['id']] = condition
    golden = sum(bool(r['rareIngredient']) for r in found)
    rarity = 'Rare' if golden else 'Common'
    multiplier = DISH_RARITIES[rarity] * (GOLDEN_PAIR_MULTIPLIER if golden == 2 else 1.0)
    name = ' + '.join(r['name'] for r in found)
    return (f'{rarity} dish ({name})' if golden else f'Dish ({name})'), list(best.values()), multiplier


@functools.lru_cache(maxsize=None)
def pair_source(key):
    try:
        first, second = key.split(':', 1)[1].split('+')
        name, conditions, multiplier = pair_dish(first, second)
    except (ValueError, KeyError):
        return None
    effects = _effects(conditions, multiplier)
    return Source(key, name, 'Dish', None, effects) if effects else None


def lookup(key, dish_rarity=DEFAULT_DISH_RARITY, golden=True):
    """The source for any key (catalogue food and potions, an owned dish, or a dish planned from two ingredients), or None"""
    if key.startswith('cooked:'):
        return cooked_source(key)
    if key.startswith('pair:'):
        return pair_source(key)
    return sources(dish_rarity, golden).get(key)


def owned_keys(internal_id, variation):
    """Source keys an item a save holds gives: a cooked dish (exact), a potion, or an ingredient (eaten raw, and the dish
    you can cook with it, at the dish rarity setting). Empty if it isn't food or a potion the solver uses."""
    if internal_id.startswith('Cooked') and variation > 0:
        key = cooked_key(internal_id, variation)
        return [key] if cooked_source(key) else []
    return [key for key in (f'potion:{internal_id}', f'food:{internal_id}', f'dish:{internal_id}') if key in sources()]


def combine(keys, dish_rarity=DEFAULT_DISH_RARITY, golden=True):
    """Effects of the chosen sources after stacking.
    Returns (effects {attribute: {label: value}} for Character, rows [(attribute, source name, value, counted, note)])."""
    chosen = [s for s in (lookup(k, dish_rarity, golden) for k in keys) if s is not None]
    conditions = wiki_data()['conditions']
    best = {} # condition id -> (value, source) that counts
    for source in chosen:
        for condition_id, attribute, value in source.effects:
            stacks = STACK_SAME_EFFECT or conditions.get(condition_id, {}).get('isAdditiveWithSelf')
            if not stacks and (condition_id not in best or value > best[condition_id][0]):
                best[condition_id] = (value, source)
    effects, rows = {}, []
    for source in chosen:
        for condition_id, attribute, value in source.effects:
            stacks = STACK_SAME_EFFECT or conditions.get(condition_id, {}).get('isAdditiveWithSelf')
            counted = stacks or best[condition_id][1] is source
            note = '' if counted else f'same effect as {best[condition_id][1].name}, which is stronger'
            if counted:
                effects.setdefault(attribute, {})[f'({source.kind} Effect) {source.name}'] = value
            rows.append((attribute, source.name, value, counted, note))
    return effects, rows


def totals(keys, dish_rarity=DEFAULT_DISH_RARITY, golden=True):
    """{attribute: total value} after stacking"""
    effects, _ = combine(keys, dish_rarity, golden)
    return {attribute: round(sum(values.values()), 4) for attribute, values in effects.items()}


def default_keys(damage_type, unused=(), biomes=None, dish_rarity=DEFAULT_DISH_RARITY, golden=True, only=None):
    """For each effect a damage type can use, the strongest source (dishes and potions; raw food is never stronger here).
    biomes: only sources from these biomes (None = all; sources of unknown biome are always allowed).
    only: choose from these keys alone (e.g. the food and potions you own; then biomes don't matter, and raw food counts)."""
    allowed = set(biomes) if biomes is not None and only is None else None
    pool = sources(dish_rarity, golden).values() if only is None else [s for s in (lookup(k, dish_rarity, golden) for k in only) if s is not None]
    best = {}
    for source in pool:
        if (source.kind == 'Food' and only is None) or (allowed is not None and source.biome is not None and source.biome not in allowed):
            continue
        for condition_id, attribute, value in source.effects:
            if attribute in unused or value <= 0 or condition_id in DEFAULT_SKIP:
                continue
            if condition_id not in best or value > best[condition_id][0]:
                best[condition_id] = (value, source.key)
    return sorted({key for _, key in best.values()})
