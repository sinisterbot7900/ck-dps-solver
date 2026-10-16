"""Cooking planner: the best dishes you can cook from the ingredients you own, by the DPS they add to a loadout.

Every pair of owned ingredients (two of the same counts, if you have two) makes a dish with the strongest of each of
their cooked effects (model/consumables.pair_dish). Each dish is scored on a loadout twice: added to the food and potions
the search used (same effect: only the stronger counts) and on its own, without other food or potions.
"""
import itertools

from ck_dps_solver.model.consumables import combine, pair_key, pair_source
from ck_dps_solver.model.item_stats import wiki_data


def owned_ingredients(owned):
    """{ingredient internal id: amount} from owned_consumables() keys ('dish:<id>' = an ingredient you can cook)"""
    return {key.split(':', 1)[1]: amount for key, amount in owned.items() if key.startswith('dish:')}


def pairs(ingredients):
    """(first, second, how many you can cook) for every dish your ingredients make"""
    found = []
    for first, second in itertools.combinations_with_replacement(sorted(ingredients), 2):
        count = ingredients[first] // 2 if first == second else min(ingredients[first], ingredients[second])
        if count > 0:
            found.append((first, second, count))
    return found


def plan(ingredients, items, character_kwargs, food_keys, dps, should_stop=None):
    """Rows (best first) for the dishes your ingredients make, scored on `items` (a loadout's equipped items).
    dps: loadout_dps(items, kwargs) for the DPS function (so this module doesn't import the solver).
    food_keys: the food and potions the loadout's DPS was found with."""
    # Food always counts here (whatever the "Consumables active" setting says): it's what's being scored
    settings = dict(character_kwargs.get('settings') or {}, **{'Consumables active': True})
    with_food = lambda keys: dict(character_kwargs, food_effects=combine(keys)[0], settings=settings)
    baseline = dps(items, with_food(list(food_keys)))
    unfed = dps(items, with_food([]))
    names = {i: r['name'] for i, r in wiki_data().get('consumables', {}).items()}
    rows, scored = [], {} # Dishes with the same effects score the same: compute once
    for first, second, count in pairs(ingredients):
        if should_stop and should_stop():
            break
        key = pair_key(first, second)
        source = pair_source(key)
        if source is None:
            continue
        if source.effects not in scored:
            scored[source.effects] = (dps(items, with_food(list(food_keys) + [key])), dps(items, with_food([key])))
        added, alone = scored[source.effects]
        rows.append({'Gain %': round((added / baseline - 1) * 100, 2) if baseline else float('nan'), 'Dish': source.name,
                     'DPS': added, 'Gain': added - baseline, 'Alone %': round((alone / unfed - 1) * 100, 2) if unfed else float('nan'),
                     'Can cook': count, 'Effects': source.describe(),
                     'Ingredients': f'{names.get(first, first)} x{ingredients[first]}' + ('' if first == second else f', {names.get(second, second)} x{ingredients[second]}'),
                     'key': key, 'ingredient_ids': (first,) if first == second else (first, second)})
    rows.sort(key=lambda r: (-r['Gain'], -r['Alone %'] if r['Alone %'] == r['Alone %'] else 0, r['Dish']))
    return rows, baseline
