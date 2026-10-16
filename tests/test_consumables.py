"""Food and potions: dishes as cooked (exact owned dishes and the catalogue model), stacking."""
import unittest

from tests import REPO # noqa: F401
from ck_dps_solver.model import consumables
from ck_dps_solver.model.item_stats import wiki_data


def dish(dish_object, first, second):
    """An owned dish's key: its object and the variation holding its two ingredients"""
    ids = {name: record['id'] for name, record in wiki_data()['objects'].items()}
    return consumables.cooked_key(dish_object, ids[first] | (ids[second] << 16))


class OwnedDishes(unittest.TestCase):
    def test_rare_cereal_of_tornis_kingfish_and_golden_bloat_oat_gives_63_percent(self):
        source = consumables.cooked_source(dish('CookedCerealRare', 'TornisKingfish', 'BloatOatRare')) # Read in game: 63%
        self.assertEqual(dict((a, v) for _, a, v in source.effects)['%_damage'], 0.63)

    def test_epic_is_one_and_a_half_times_common(self):
        epic = consumables.cooked_source(dish('CookedCerealEpic', 'TornisKingfish', 'BloatOatRare'))
        self.assertEqual(dict((a, v) for _, a, v in epic.effects)['%_damage'], 0.756)

    def test_a_dish_matches_the_catalogue_model_for_one_golden_ingredient(self):
        owned = consumables.cooked_source(dish('CookedCerealRare', 'TerraTrilobite', 'BloatOatRare'))
        self.assertEqual(owned.effects, consumables.lookup('dish:TerraTrilobite').effects) # Rare, not both golden

    def test_owned_keys(self):
        self.assertEqual(consumables.owned_keys('UnusualPotion', 0), ['potion:UnusualPotion'])
        self.assertEqual(consumables.owned_keys('MoldShark', 0), ['dish:MoldShark']) # An ingredient: the dish you can cook
        self.assertEqual(consumables.owned_keys('Wood', 0), [])


class Stacking(unittest.TestCase):
    def test_the_same_effect_counts_once(self):
        _, rows = consumables.combine(['dish:TornisKingfish', 'dish:MarbledMeat'])
        counted = [name for attribute, name, _, counted, _ in rows if attribute == '%_damage' and counted]
        self.assertEqual(len(counted), 1)


if __name__ == '__main__':
    unittest.main()
