"""The search: catalogue.py against the wiki data, the set bonus table, the batch engine against single loadouts, and the
rule that a piece kept only for its set appears only when it completes the set."""
import os
import unittest

from tests import REPO # noqa: F401
from tools.verify import check_engine, check_items, check_sets
from ck_dps_solver import defaults
from ck_dps_solver.engine import solver
from ck_dps_solver.engine.dominance import completes_sets, set_only_requirements
from ck_dps_solver.model import Character

FAST = bool(os.environ.get('CK_FAST_TESTS'))


class Data(unittest.TestCase):
    def test_items_match_the_wiki_data(self):
        self.assertEqual(check_items(20), [])

    def test_set_bonuses_name_real_sets(self):
        self.assertEqual(check_sets(), [])


@unittest.skipIf(FAST, 'CK_FAST_TESTS: skipping the engine check')
class Engine(unittest.TestCase):
    def test_batch_engine_matches_single_loadouts(self):
        problems, checked = check_engine(450)
        self.assertGreater(checked, 0)
        self.assertEqual(problems, [])


class SetOnlyItems(unittest.TestCase):
    def test_a_set_only_piece_needs_its_set(self):
        weapons, slots, _, _ = solver.catalogue_search_items('Range')
        pool = list(weapons) + [i for items in slots.values() for i in items]
        settings = Character(defaults.skill_levels, defaults.perk_trees).settings
        needs = set_only_requirements(pool, settings, 'Range')
        get = lambda name: next(i for i in pool if i.name == name)
        tome, necklace, ring = get('Blue Leather Tome'), get('Skull Necklace'), get('Skull Ring')
        self.assertFalse(completes_sets([tome], needs))
        self.assertFalse(completes_sets([tome, necklace], needs))
        self.assertTrue(completes_sets([tome, necklace, ring], needs))
        self.assertTrue(completes_sets([tome, necklace, ring, ring], needs)) # Two copies of a ring count once


if __name__ == '__main__':
    unittest.main()


class SummonerKits(unittest.TestCase):
    def test_a_kit_doesnt_reinforce_an_already_reinforced_scepter_again(self):
        # A magic search reinforces scepters in place; a summoner kit made from one afterwards must not add another 15%
        import copy
        from ck_dps_solver.catalogue import WEAPONS
        from ck_dps_solver.model import SummonerKit
        tome = next(w for w in WEAPONS.values() if w.damage_type == 'Summoning' and w.has_durability)
        scepter = next(w for w in WEAPONS.values() if getattr(w, 'curses', False) and w.has_durability)
        fresh = SummonerKit(copy.deepcopy(tome), copy.deepcopy(scepter))
        fresh.reinforce()
        done = copy.deepcopy(scepter)
        done.reinforce()
        later = SummonerKit(copy.deepcopy(tome), done)
        later.reinforce()
        self.assertEqual((later.scepter_min_damage, later.scepter_max_damage, later.attributes),
                         (fresh.scepter_min_damage, fresh.scepter_max_damage, fresh.attributes))
        self.assertEqual((later.min_damage, later.max_damage), (fresh.min_damage, fresh.max_damage))


class Mana(unittest.TestCase):
    def test_bursting_at_full_mana_never_loses_to_spending_as_it_comes(self):
        # Waiting to refill only happens when it pays (never at the end of a fight with no time to spend it)
        from ck_dps_solver.catalogue import WEAPONS
        config = defaults.default_config('Magic')
        for fight in (15.0, 60.0, 180.0):
            for weapon in [w for w in WEAPONS.values() if w.damage_type == 'Magic' and w.mana_cost > 0]:
                dps = {}
                for burst in (False, True):
                    settings = dict(config['settings'], **{'Burst at full mana': burst, 'Fight length': fight})
                    kwargs = dict(skill_levels=config['skill_levels'], perks=config['perk_trees'], food_effects={}, potion_effects={}, settings=settings)
                    dps[burst] = solver.loadout_dps([weapon], kwargs)
                self.assertGreaterEqual(dps[True], dps[False], (weapon.name, fight))
