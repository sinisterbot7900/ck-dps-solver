"""The cooking planner: dishes from two ingredients, how many you can cook, and scoring."""
import unittest

from tests import REPO # noqa: F401
from ck_dps_solver.model import cooking
from ck_dps_solver.model.consumables import DISH_RARITIES, GOLDEN_PAIR_MULTIPLIER, lookup, pair_dish, pair_key
from ck_dps_solver.model.item_stats import wiki_data


def consumable(name):
    return next(i for i, r in wiki_data()['consumables'].items() if r['name'] == name)


class PairDishes(unittest.TestCase):
    def test_key_ignores_order(self):
        self.assertEqual(pair_key('LarvaMeat', 'HeartBerry'), pair_key('HeartBerry', 'LarvaMeat'))

    def test_strongest_of_each_effect(self):
        # Heart Berry and Giant Mushroom both give max health: the stronger one counts, once
        _, conditions, multiplier = pair_dish(consumable('Heart Berry'), consumable('Giant Mushroom'))
        values = {c['id']: c['value'] for c in conditions}
        records = wiki_data()['consumables']
        for name in ('Heart Berry', 'Giant Mushroom'):
            for c in records[consumable(name)]['cooked']:
                self.assertGreaterEqual(values[c['id']], c['value'])
        self.assertEqual(multiplier, 1.0) # No golden ingredient: common

    def test_golden_rarity(self):
        golden = [i for i, r in wiki_data()['consumables'].items() if r['rareIngredient'] and r['cooked']][:2]
        plain = consumable('Heart Berry')
        self.assertEqual(pair_dish(golden[0], plain)[2], DISH_RARITIES['Rare'])
        self.assertAlmostEqual(pair_dish(golden[0], golden[1])[2], DISH_RARITIES['Rare'] * GOLDEN_PAIR_MULTIPLIER)

    def test_lookup_resolves_planned_dishes(self):
        source = lookup(pair_key(consumable('Heart Berry'), consumable('Larva Meat')))
        self.assertIsNotNone(source)
        self.assertEqual(source.kind, 'Dish')


class Pairs(unittest.TestCase):
    def test_counts(self):
        found = {(a, b): n for a, b, n in cooking.pairs({'A': 3, 'B': 1})}
        self.assertEqual(found, {('A', 'A'): 1, ('A', 'B'): 1}) # One B can't be cooked with itself

    def test_owned_ingredients(self):
        owned = {'dish:HeartBerry': 4, 'food:HeartBerry': 4, 'potion:MagicPotion': 2, 'cooked:CookedCerealRare:1': 1}
        self.assertEqual(cooking.owned_ingredients(owned), {'HeartBerry': 4})


class Plan(unittest.TestCase):
    def test_scores_and_sorts(self):
        # A stand-in DPS: 100 plus 1 per point of max health from food
        def dps(items, kwargs):
            self.assertTrue(kwargs['settings']['Consumables active']) # Food always counts when planning
            return 100 + sum(sum(v.values()) for a, v in kwargs['food_effects'].items() if a == '+_max_health')
        berry, mushroom = consumable('Heart Berry'), consumable('Giant Mushroom')
        rows, baseline = cooking.plan({berry: 2, mushroom: 2}, [], {'settings': {'Consumables active': False}}, [], dps)
        self.assertEqual(baseline, 100)
        self.assertEqual(len(rows), 3)
        self.assertEqual([r['Gain'] for r in rows], sorted((r['Gain'] for r in rows), reverse=True))
        self.assertGreater(rows[0]['Gain'], 0)


if __name__ == '__main__':
    unittest.main()
