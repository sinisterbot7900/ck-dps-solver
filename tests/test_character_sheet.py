"""The character sheet against a character's screen in game: an early summoner in the reinforced Witch Doctor set
(level 3), well fed, with one permanent food (Giant Mushroom) and a common Heart Berry dish, an Owlux pet; weapons
held one at a time. Every expected value below was read in game."""
import unittest

from tests import REPO # noqa: F401
from ck_dps_solver import defaults
from ck_dps_solver.catalogue import PETS
from ck_dps_solver.engine import solver
from ck_dps_solver.engine.character_sheet import sheet
from ck_dps_solver.model import Character
from ck_dps_solver.model.consumables import sources
from ck_dps_solver.model.item_stats import find_internal_id, make_item
from ck_dps_solver.saves.owned_items import empty_item

LEVELS = {'Mining': 20, 'Running': 25, 'Melee': 0, 'Vitality': 8, 'Crafting': 11, 'Range': 0, 'Gardening': 16, 'Fishing': 0,
          'Cooking': 10, 'Magic': 8, 'Summoning': 12, 'Explosives': 0}
PERKS = {skill: [0] * 8 for skill in LEVELS}
PERKS.update(Vitality=[1, 0, 0, 0, 0, 0, 0, 0], Cooking=[2, 0, 0, 0, 0, 0, 0, 0], Magic=[1, 0, 0, 0, 0, 0, 0, 0], Mining=[4, 0, 0, 0, 0, 0, 0, 0])


def item(name, level, reinforced=False):
    """An item as read from a save: at its level, reinforced or not (and not reinforced again by the sheet)"""
    found = make_item(find_internal_id(name), level)
    found.level = level
    if reinforced:
        found.reinforce()
    found.has_durability = False
    return found


class EarlySummoner(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        settings = dict(Character(defaults.skill_levels, defaults.perk_trees).settings)
        settings.update({'Well fed': True, 'Permanent max health': 25, 'Druidra soul': False, 'Pyrdra soul': False, 'Consumables active': True})
        cls.food = [next(key for key, s in sources('Common', False).items() if s.name == 'Heart Berry dish')]
        cls.kwargs = dict(skill_levels=LEVELS, perks=PERKS, food_effects=solver.consumable_effects(cls.food, 'Common', False),
                          potion_effects={}, settings=settings)
        cls.owlux = PETS['Owlux']
        cls.armor = [item(name, 3, reinforced=True) for name in ('Witch Doctor Hat', 'Witch Doctor Vest', 'Witch Doctor Jeans')]

    def stat(self, label, weapon='Wood Crossbow', level=2, armor=None, fixed=()):
        pieces = self.armor if armor is None else [p if p.name in armor else empty_item(p.item_category) for p in self.armor]
        loadout = (0, item(weapon, level), *pieces, empty_item('Necklace'), empty_item('Ring'), empty_item('Ring'), empty_item('Offhand'), None)
        rows = sheet(loadout, [self.owlux, *fixed], self.kwargs, self.food, 'Common', False)
        return next(value for _, name, value in rows if name == label)

    def test_max_health_rounds_to_nearest(self):
        self.assertEqual(self.stat('Max health'), '206') # 196 x 1.05 = 205.8
        self.assertEqual(self.stat('Max health', fixed=[item('Small Backpack', 2)]), '212') # +6: 202 x 1.05 = 212.1

    def test_armor_pieces_pairs_and_the_full_set(self):
        self.assertEqual(self.stat('Armor'), '13') # 3 + 5 + 4, and +1 with all three
        self.assertEqual(self.stat('Armor', armor={'Witch Doctor Hat', 'Witch Doctor Vest'}), '8')
        self.assertEqual(self.stat('Armor', armor={'Witch Doctor Vest', 'Witch Doctor Jeans'}), '9')
        self.assertEqual(self.stat('Armor', armor={'Witch Doctor Hat', 'Witch Doctor Jeans'}), '7')
        self.assertEqual(self.stat('Armor', armor=set()), '0')

    def test_damage_ranges(self):
        self.assertEqual(self.stat('Damage per hit', 'Wood Crossbow', 2), '47 - 57')
        self.assertEqual(self.stat('Damage per hit', 'Sticky Stick', 4), '108 - 130')
        self.assertEqual(self.stat('Damage per hit', 'Runestone Scepter', 7), '48 - 58')

    @unittest.expectedFailure
    def test_simple_staff(self):
        # The game shows 72 - 86: its damage is ~68.5, the wiki lists 68 (rounded down), so the low end comes out 71.
        # This fails (as expected) until the data has the fraction; if it starts passing, remove expectedFailure.
        self.assertEqual(self.stat('Damage per hit', 'Simple Staff', 2), '72 - 86')


if __name__ == '__main__':
    unittest.main()
