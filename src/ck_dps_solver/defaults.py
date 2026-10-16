"""Default options for a search: skills, talents, food, settings, items to search and save files.

default_config() returns them as one dict, the "config" that engine.solver.run_search takes. The window starts from it
(and saves your changes in your user folder); the command line reads a JSON file of the options to change
(ck-dps-solver search --config my.json; ck-dps-solver defaults prints them all).
"""
import copy

from ck_dps_solver.engine.dominance import unused_attributes
from ck_dps_solver.model import Character
from ck_dps_solver.model.consumables import DEFAULT_DISH_RARITY, default_keys


skill_levels = {
    'Mining':       100,
    'Running':      100,
    'Melee':        100,
    'Vitality':     100,
    'Crafting':     100,
    'Range':        100,
    'Gardening':    100,
    'Fishing':      100,
    'Cooking':      100,
    'Magic':        100,
    'Summoning':    100,
    'Explosives':   100,
}

# Talents (points per talent in tree order, 25 at level 100): the best legal build for each skill, found by trying every
# legal build on each damage type's best loadouts (Melee, Range, Magic, Summoning, Explosives; every item, default
# settings, so Magic assumes a full barrier). Where builds tie, the one closest to the previous default. A skill's tree
# here is the best for its own damage type; PERK_TREES_FOR has the other damage types that do better with another build.
# Talents named below; a number is its points when fewer than 5.
perk_trees = {
    'Mining':     [5, 5, 5, 5, 0, 5, 0, 0], # Efficient excavation, Meticulous miner, Self-mending alloy, Miner's strength, Explosives engineer
    'Running':    [5, 0, 5, 0, 5, 5, 0, 5], # Endurance runner, Gotta go fast!, Escape artist, Keeping tempo, Breaking barriers
    'Melee':      [5, 5, 5, 0, 5, 0, 0, 5], # Quick strikes, Building anger, Fast and furious, Stubborn fighter, Strength of the Ancients
    'Vitality':   [5, 5, 5, 0, 5, 0, 5, 0], # Maxed out!, Strong and healthy, Desperate fighter, Healing potency, Protection of the Ancients
    'Crafting':   [5, 5, 5, 5, 0, 0, 5, 0], # Base builder, The right tools in the right hands, High quality equipment, Alchemist, Jewelry crafter
    'Range':      [5, 5, 5, 0, 0, 5, 0, 5], # Rapid shots, Keeping momentum, Weakness detection, Stun shot, Amplified precision
    'Gardening':  [5, 5, 0, 5, 5, 0, 0, 5], # Grateful gardener, Eat your vegetables!, Thorny weapons, Thorny skin, Potent poison
    'Fishing':    [5, 5, 0, 0, 5, 0, 5, 5], # Improved bait, Fisherman's luck, Steady feet, Well-trained aim, Power of Omega-3!
    'Cooking':    [5, 5, 5, 5, 0, 5, 0, 0], # Utilizing every nutrient, Not so picky, Healthy diet, Fast food, The smell of food
    'Magic':      [5, 5, 5, 1, 0, 5, 0, 4], # True sight, Mana channeling, Arcane frenzy, The best offense 1, Arcane transfusion, Mana recharge 4
    'Summoning':  [5, 5, 5, 5, 0, 2, 3, 0], # Efficient binding, Ferocious creatures, Critical command, Trickle down arcana, Group effort 2, Heartbound horde 3
    'Explosives': [5, 0, 5, 0, 5, 0, 5, 5], # High Velocity Charge, Auto Salvage, Mana Blast, After Burn, Napalm
}

# Per damage type, the skill trees where it does better with another build than perk_trees (see perk_trees_for)
PERK_TREES_FOR = {
    # Power in numbers: range attack speed per minion, with "Summon active" (+3.9% Range, +4.2% Magic: magic weapons
    # hit at range too)
    'Range': {'Summoning': [5, 0, 5, 0, 5, 0, 5, 5]}, # Efficient binding, Critical command, Tough gang, Heartbound horde, Power in numbers
    'Magic': {'Summoning': [5, 0, 5, 0, 5, 0, 5, 5]},
    # The scepter's magic damage: The best offense over Mana recharge (+0.8%)
    'Summoning': {'Magic': [5, 5, 5, 4, 1, 5, 0, 0]}, # True sight, Mana channeling, Arcane frenzy, The best offense 4, Mental defense 1, Arcane transfusion
}


def perk_trees_for(damage_type):
    """The default talents for a damage type: perk_trees with its PERK_TREES_FOR changes"""
    return copy.deepcopy(dict(perk_trees, **PERK_TREES_FOR.get(damage_type, {})))

# Food and potions per damage type: keys of model/consumables.py sources (see the Consumables tab).
# Default: the strongest dish or potion for each effect the damage type uses. Same-effect sources don't stack.
CONSUMABLES = {damage_type: default_keys(damage_type, unused_attributes(damage_type)) for damage_type in ('Melee', 'Range', 'Magic', 'Summoning', 'Explosives')}

# Cooked dishes' rarity: 'Rare' (dishes with a golden ingredient), 'Common', or 'Epic' (by chance with Master chef)
DISH_RARITY = DEFAULT_DISH_RARITY
# Whether you have golden ingredients (grown with the Expert gardener talent). Without them dishes are common.
GOLDEN_INGREDIENTS = True

TOP_N = 100_000 # Number of best loadouts written to the CSV
# Try every pet (the catalogue's pets for the damage type, or the pets you own) instead of the configured one below
SEARCH_PETS = False
# Try every lantern / bag (the catalogue's, or the ones you own; or none) instead of the configured one below
SEARCH_LANTERNS = False
SEARCH_BAGS = False
# Per damage type, the always-equipped categories ('Lantern', 'Bag', 'Pet') to pick the best item for (from the
# progression, or what you own) instead of the configured one: a quick search without them, then the best combination
# on its top loadouts, then the real search with it. Much faster than trying them all; Try all (above) overrides it.
BEST_FIXED = {}

# Biomes to load items from (see model/progression.py), e.g. biomes_up_to('Sunken Sea') for gear up to Omoroth. None = all
BIOMES = None # e.g. biomes_up_to('Sunken Sea'): that biome and every one before it

# Skip items another item in the same slot beats in every stat (never set items). The best loadout is unchanged;
# the CSV no longer lists loadouts that only differ by a dominated item. See engine/dominance.py.
DROP_DOMINATED_ITEMS = True
# Owned items with biomes chosen: after the search, rank the items from those biomes you don't own yet by how much
# they'd raise your best DPS, with where to get them (written next to the output, e.g. outputs/range_dps_upgrades.csv)
SUGGEST_UPGRADES = True

DAMAGE_TYPE = 'Range' # 'Melee', 'Range', 'Magic', 'Summoning' or 'Explosives'
OUTPUT = 'outputs/{damage_type}_dps.csv'

# Equipped in every loadout of a damage type (in Character.items order: lantern, bag, pet)
FIXED_ITEM_NAMES = {
    'Range': ['Pheromoth'],
    'Melee': ['Orb Lantern', 'Morpha\'s Bubble Backpack', 'Owlux'],
    'Magic': ['Pearl Lantern', 'Scholar Backpack', 'Owlux'],
    'Summoning': ['Soul Lantern', 'Earie'],
    'Explosives': [],
}

# Only search items you own: your character's save (saves/<n>.json) and its world (worlds/<n>.world.gzip), in
# %USERPROFILE%\AppData\LocalLow\Pugstorm\Core Keeper\Steam\<your Steam id>\
SAVE_FILTER = {
    'enabled': False,
    'player_files': [],                         # Equipped and inventory items
    'world_files': [],                          # Items stored in chests
    'radius': 300,                              # Only chests within this many tiles (None = whole world, including generated loot chests)
    'center': None,                             # (x, z) to measure from; None = your character's position in the world
    'reinforcement': 'assume',                  # 'assume': owned gear counts as reinforced; 'detected': only gear the save shows as reinforced
    'level': 'actual',                          # 'actual': items at their level in the save; 'max': as if every item were upgraded to level 20
    'character_stats': True,                    # Use the character's skill levels and talents from its save (first player file)
}



def default_config(damage_type=None):
    """Every option of a run, from the values above, with the talents for damage_type (default DAMAGE_TYPE). The window
    and the command line edit a copy of this."""
    damage_type = damage_type or DAMAGE_TYPE
    return copy.deepcopy({
        'damage_type': damage_type,
        'skill_levels': skill_levels,
        'perk_trees': perk_trees_for(damage_type),
        'consumables': CONSUMABLES,
        'dish_rarity': DISH_RARITY,
        'golden_ingredients': GOLDEN_INGREDIENTS,
        'settings': Character(skill_levels, perk_trees).settings,
        'top_n': TOP_N,
        'drop_dominated': DROP_DOMINATED_ITEMS,
        'fixed_items': FIXED_ITEM_NAMES,
        'search_pets': SEARCH_PETS,
        'search_lanterns': SEARCH_LANTERNS,
        'search_bags': SEARCH_BAGS,
        'best_fixed': BEST_FIXED,
        'biomes': BIOMES,
        'suggest_upgrades': SUGGEST_UPGRADES,
        'save_filter': SAVE_FILTER,
        'output': OUTPUT,
    })
