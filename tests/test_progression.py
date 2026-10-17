"""Progression: what counts as reached for a biome choice."""
import unittest

from tests import REPO # noqa: F401
from ck_dps_solver.model.progression import biomes_up_to, souls_reached


class Souls(unittest.TestCase):
    def test_a_soul_counts_once_its_boss_is_beaten(self):
        # Druidra and Pyrdra are Shimmering Frontier's gate bosses: reached from the next biome on
        self.assertEqual(souls_reached(biomes_up_to('Shimmering Frontier')), {'Druidra soul': False, 'Pyrdra soul': False})
        self.assertEqual(souls_reached(biomes_up_to('Passage')), {'Druidra soul': True, 'Pyrdra soul': True})
        self.assertTrue(all(souls_reached(None).values())) # No progression chosen: everything


if __name__ == '__main__':
    unittest.main()
