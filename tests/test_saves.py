"""Reading saves without save files: skill levels from experience, chests that count as owned, souls."""
import unittest

from tests import REPO # noqa: F401
from ck_dps_solver.model.item_stats import wiki_data
from ck_dps_solver.saves import save_reader

# (skill, experience in the save, level shown in game), read across five characters after update 1.3.0.1
LEVEL_READINGS = [
    ('Gardening', 115, 11), ('Magic', 271, 8), ('Summoning', 487, 12), ('Running', 9604, 25), ('Crafting', 420, 11),
    ('Mining', 1501, 20), ('Cooking', 45, 7), ('Vitality', 19239, 8),
    ('Magic', 2037, 37), ('Summoning', 3327, 40), ('Running', 421511, 96),
    ('Melee', 1804, 34), ('Range', 5093, 61),
    ('Gardening', 1138, 53), ('Gardening', 2220, 71),
    ('Melee', 20001, 100), ('Range', 20001, 100),
]


class SkillLevels(unittest.TestCase):
    def test_levels_match_the_game(self):
        skills = wiki_data()['skills']
        for skill, xp, level in LEVEL_READINGS:
            self.assertEqual(save_reader.skill_level(xp, skills[skill]), level, f'{skill} at {xp} xp')


class Chests(unittest.TestCase):
    def test_storage_chests_count_everything(self):
        self.assertTrue(save_reader._counts('IronChest', 123, discovered=set()))

    def test_loot_chests_count_only_discovered_items(self):
        self.assertFalse(save_reader._counts('InventoryAncientChest', 123, discovered={7}))
        self.assertTrue(save_reader._counts('InventoryAncientChest', 7, discovered={7}))


class Souls(unittest.TestCase):
    def test_soul_ids_follow_the_wiki_order(self):
        self.assertEqual(save_reader.SOUL_SETTINGS, {4: 'Druidra soul', 6: 'Pyrdra soul'}) # Azeos, Omoroth, Ra-Akar, Druidra, Crydra, Pyrdra


class PermanentFoods(unittest.TestCase):
    def test_all_ten_foods_add_up_to_590(self):
        foods = save_reader.permanent_health_foods()
        self.assertEqual(len(foods), 10)
        self.assertEqual(sum(value for *_, value in foods), 590)


if __name__ == '__main__':
    unittest.main()
