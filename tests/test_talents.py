"""Talent tree rules (model/talents.py): points per level, the links between tiers, legal builds."""
import unittest

from tests import REPO # noqa: F401 (puts the repository on the path)
from ck_dps_solver import defaults
from ck_dps_solver.model import talents
from ck_dps_solver.model.item_stats import wiki_data

MELEE = wiki_data()['skills']['Melee']['talents'] # Quick strikes, Building anger, Fast and furious, Heavy swings, Stubborn
                                                  # fighter, Taking a step back, Seething blade, Strength of the Ancients


def melee(*named):
    """Melee points with 5 in each named talent"""
    return [5 if name in named else 0 for name in MELEE]


class Points(unittest.TestCase):
    def test_a_point_every_five_levels_and_five_more_at_100(self):
        self.assertEqual([talents.available('Melee', level) for level in (0, 4, 5, 96, 99, 100)], [0, 0, 1, 19, 19, 25])


class Links(unittest.TestCase):
    def test_every_tree_is_1_2_3_2(self):
        for skill in wiki_data()['skills']:
            self.assertEqual([len(tier) for tier in talents.tree(skill)], [1, 2, 3, 2], skill)

    def test_melee_links_as_in_game(self):
        named = {(MELEE[a], MELEE[b]) for a, b in talents.links('Melee')}
        self.assertEqual(named, {
            ('Quick strikes', 'Building anger'), ('Quick strikes', 'Fast and furious'),
            ('Building anger', 'Heavy swings'), ('Building anger', 'Stubborn fighter'),
            ('Fast and furious', 'Stubborn fighter'), ('Fast and furious', 'Taking a step back'),
            ('Heavy swings', 'Seething blade'), ('Stubborn fighter', 'Seething blade'),
            ('Stubborn fighter', 'Strength of the Ancients'), ('Taking a step back', 'Strength of the Ancients')})

    def test_a_talent_opens_only_below_a_full_linked_talent(self):
        opened = {MELEE[i] for i in talents.unlocked('Melee', melee('Quick strikes', 'Building anger'))}
        self.assertIn('Heavy swings', opened)
        self.assertNotIn('Taking a step back', opened) # Needs Fast and furious
        self.assertIn('Fast and furious', talents.why_not_add('Melee', 100, melee('Quick strikes', 'Building anger'), MELEE.index('Taking a step back')))

    def test_legal_and_illegal_builds(self):
        self.assertTrue(talents.is_legal('Melee', 100, melee('Quick strikes', 'Fast and furious', 'Taking a step back', 'Strength of the Ancients')))
        self.assertFalse(talents.is_legal('Melee', 100, melee('Quick strikes', 'Building anger', 'Heavy swings', 'Strength of the Ancients')))
        self.assertFalse(talents.is_legal('Melee', 10, melee('Quick strikes', 'Building anger'))) # 10 points at level 10 is too many

    def test_the_solvers_default_builds_are_legal(self):
        for damage_type in ['Melee', 'Range', 'Magic', 'Summoning', 'Explosives']:
            for skill, points in defaults.perk_trees_for(damage_type).items():
                self.assertTrue(talents.is_legal(skill, defaults.skill_levels.get(skill, 0), points), (damage_type, skill))
                self.assertEqual(sum(points), talents.available(skill, defaults.skill_levels.get(skill, 0)), (damage_type, skill)) # Every point spent

    def test_damage_types_get_their_own_talent_changes(self):
        self.assertEqual(defaults.default_config('Range')['perk_trees']['Summoning'], defaults.PERK_TREES_FOR['Range']['Summoning'])
        self.assertEqual(defaults.default_config('Melee')['perk_trees'], defaults.perk_trees) # No changes for Melee
        defaults.perk_trees_for('Magic')['Magic'][0] = 0 # A copy: changing it leaves the defaults alone
        self.assertEqual(defaults.perk_trees['Magic'][0], 5)

    def test_removing_a_point_others_depend_on_is_refused(self):
        points = melee('Quick strikes')
        points[MELEE.index('Building anger')] = 1
        self.assertIsNotNone(talents.why_not_remove('Melee', 100, points, MELEE.index('Quick strikes')))


class LowerLevel(unittest.TestCase):
    def test_points_come_off_the_bottom_of_the_tree_first(self):
        start = [5, 5, 5, 0, 5, 0, 1, 4] # 25 points
        self.assertEqual(talents.fit_to_level('Melee', 90, start), [5, 5, 5, 0, 3, 0, 0, 0]) # 18 points
        self.assertEqual(talents.fit_to_level('Melee', 24, start), [4, 0, 0, 0, 0, 0, 0, 0]) # 4 points


if __name__ == '__main__':
    unittest.main()
