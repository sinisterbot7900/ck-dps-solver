"""Names and texts shared by the Qt app's tabs"""
from ck_dps_solver.engine import solver

# Explosives works in the solver (defaults.DAMAGE_TYPE = 'Explosives'; mortars and zookas use its explosions) but isn't
# offered here: grenades alone are far weaker than every other damage type
DAMAGE_TYPES = ['Melee', 'Range', 'Magic', 'Summoning']
RESULT_COLUMNS = ['DPS', 'Weapon', 'Helm', 'Breast armor', 'Pants armor', 'Necklace', 'Ring1', 'Ring2', 'Offhand', 'Lantern', 'Bag', 'Pet']
UPGRADE_COLUMNS = solver.UPGRADE_COLUMNS
KEPT_RESULTS = 1000 # Rows the results table can filter and sort (the run keeps the items of this many loadouts)
CURVE_SECONDS = 60 # DPS curve length (seconds)
# What each setting affects (hover text)
SETTING_HELP = {
    'Well fed': 'Well fed buff from eating: +5% damage and max health, more with Healthy diet; Cooking Pot and Pot sets',
    'Max health': 'At full health: Crystal and Galaxite sets, Strong and healthy',
    'Low health': 'At 25% health or less: Octarine set (75% missing health), Desperate fighter',
    'Running stacks': 'Keeping tempo talent stacks',
    'Range stacks': 'Keeping momentum talent stacks, Dreamer set',
    'Standing still': 'Focused accuracy, Hunter set, Chime Necklace',
    'Melee stacks': 'Building anger and Stubborn fighter stacks',
    'Consumables active': 'Food and potions from the Consumables tab',
    'Ate fish-derived food': 'Power of Omega-3! (damage against bosses)',
    'Pyrdra soul': "Pyrdra's soul: +10% damage",
    'Druidra soul': "Druidra's soul: +10% max health (Summoning: Heartbound horde)",
    'Cursed target': "Summoning: your scepter's curse works on the target, so minions deal 40% more damage (some creatures are immune)",
    'Permanent max health': 'Max health from permanent foods eaten (all ten: 590). Summoning: Heartbound horde. Load on the Items tab reads them from the save',
    'Summon active': 'Power in numbers (range attack speed with a summon out)',
    'Not hit': "You haven't taken damage: Pandorium set",
    'Kill stacks': 'Scarlet set: 5 kill stacks of crit chance',
    'Recently dodged': 'Assassin set attack speed after a dodge',
    'Burning': 'You are burning: Welder set',
    'Recently mined': 'Carapace set damage after mining a wall',
    'Vs boss': 'Target is a boss: all damage against bosses (Golem set, Strength of the Ancients, food...)',
    'Adjacent to water': 'Magic: Swamp Mage set',
    'Full barrier': 'Magic: barrier counts for The best offense, Mage Low set, Arcane transfusion and the Warped set',
    'Burst at full mana': ('Magic and scepters, once mana runs out. On: wait for mana to refill, then attack at full speed until it runs '
                           'out again (mana regenerates at the full rate while you wait). Off: attack whenever there is mana for it '
                           '(regeneration stays halved while you keep attacking)'),
    'Fight length': 'Seconds of nonstop attacking from full mana and unpoisoned targets: magic mana runs out, poison takes time to land',
}
