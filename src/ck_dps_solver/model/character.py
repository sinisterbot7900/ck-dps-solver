ACTIVE_EFFECTS_DICT = {
    '%_damage': {},
    '%_physical_melee_damage': {},
    '%_physical_range_damage': {},
    '%_mining_damage': {},
    '%_melee_attack_speed': {},
    '%_range_attack_speed': {},
    '%_melee_and_range_attack_speed': {},
    '%_damage_against_bosses': {},
    '%_critical_hit_damage': {},
    '%_critical_hit_chance': {},
    '%_damage_against_burning': {},
    '%_critical_hit_damage_against_burning': {},
    '%_triple_hit_chance': {},
    '+_fishing': {},
    '+_mining_damage': {},
    '+_thorns_damage': {},
    '%_chance_to_apply_poison': {}, # Your chance on hit to poison (15 sec; see engine/dps_utils.py)
    '%_pet_poison_chance': {}, # An attacking pet's chance to poison (keeps targets poisoned; not poison you apply)
    '%_damage_against_poisoned': {}, # Damage against poisoned targets, scaled by how much of the fight targets are poisoned
    '%_critical_hit_chance_after_poisoning': {}, # Crit chance while poison you applied is active (Ivy set), scaled the same way
    '%_range_damage_while_standing_still': {}, # Added to range damage with the 'Standing still' setting
    '%_melee_attack_speed_proc_chance': {}, # Chance on melee hit for +50% melee attack speed (2 sec), same proc as Fast and furious
    '+_burn_damage_on_hit': {}, # Burn damage itself isn't modeled; makes the item a burn source
    '%_melee_damage': {}, # Melee damage of any kind (physical or magic melee weapons)
    '%_range_damage': {}, # Range damage of any kind (physical or magic range weapons)
    '%_magic_damage': {},
    '%_magic_damage_near_water': {}, # Magic damage with the 'Adjacent to water' setting
    '%_magic_damage_from_mana': {}, # Up to this much magic damage at full mana, scaling down to 0 at empty (Fully charged, Mage Mid set)
    '%_magic_damage_on_crit': {}, # Magic damage for 3 sec after a critical hit (Soaring set)
    '+_max_mana': {},
    '+_mana_regen': {}, # Mana per second
    '%_mana_regen_while_casting': {},
    '%_mana_regen_delay_reduction': {}, # Shortens the 1 sec of halved mana regeneration after an attack
    '%_minion_damage': {},
    '%_minion_attack_speed': {},
    '%_minion_critical_hit_chance': {},
    '%_minion_critical_hit_damage': {},
    '%_minion_damage_against_bosses': {},
    '+_max_minions': {}, # Minions beyond the first
    '%_mana_reservation_reduction': {}, # Less mana reserved per minion
    '%_magic_to_minion_damage': {}, # Share of your magic damage bonus added to minion damage (Trickle down arcana, Grim set)
    '+_max_health': {},
    '%_max_health': {},
    '%_explosives_damage': {}, # Explosion damage (explosions get only explosives bonuses)
    '%_napalm_chance': {}, # Chance for an explosion to spawn napalm
    '%_burning_damage': {}, # Burn damage (napalm)
    '+_magic_barrier': {},
    '%_barrier_as_magic_damage': {}, # Share of magic barrier added as flat magic damage per hit
    '%_barrier_as_mana_regen': {}, # Share of magic barrier recovered as mana every second
}

# Item groups that aren't wiki sets, counted like set pieces
BURN_SOURCE = 'Burn source' # Any equipped item that burns targets on hit

# Octarine set: 'Low health' is 25% health or less (checked in game), so assume the minimum 75% missing health
LOW_HEALTH_MISSING_HEALTH_PERCENT = 75

# Set bonuses (and other effects that depend on equipped item groups), applied in this order.
# (attribute, label, value or value(perks), {set or group: pieces required}, setting that must be on)
SET_BONUSES = [
    ('%_damage', '(Set Effect) Core Commander Set', 0.25, {'CoreCommanderSet': 2}, None),
    ('%_critical_hit_chance_after_poisoning', '(Set Effect) Ivy\'s Set', 0.25, {'IvySet': 2}, None),
    ('%_damage', '(Set Effect) Shadow Set', 0.313, {'ShadowSet': 2}, None),
    ('%_melee_and_range_attack_speed', '(Set Effect) Easter Set', 0.07, {'EasterSet': 3}, None),
    ('%_physical_range_damage', '(Set Effect) Slime Ring And Necklace', 0.131, {'SlimeRingAndNecklace': 2}, None),
    ('+_mining_damage', '(Set Effect) Rock And Stone Rings', 49, {'RockAndStoneRings': 2}, None),
    ('%_damage', '(Set Effect) Crystal Set', 0.236, {'CrystalSet': 3}, 'Max health'),
    ('%_damage', '(Set Effect) Galaxite Set', 0.127, {'GalaxiteSet': 3}, 'Max health'),
    ('%_physical_melee_damage', '(Set Effect) Pandorium Set', 0.8, {'PandoriumSet': 3}, 'Not hit'),
    ('%_range_damage', '(Set Effect) Dreamer Set', 10 * 0.02, {'DreamerSet': 3}, 'Range stacks'),
    ('%_critical_hit_chance', '(Set Effect) Hunter Set', 0.15, {'HunterSet': 2}, 'Standing still'),
    ('%_critical_hit_chance', '(Set Effect) Scarlet Set', 5 * 0.03, {'ScarletArmorSet': 3}, 'Kill stacks'),
    ('%_melee_and_range_attack_speed', '(Set Effect) Assassin Set', 0.266, {'AssassinSet': 2}, 'Recently dodged'),
    ('%_melee_attack_speed', '(Set Effect) Warrior Set', 0.036, {'WarriorSet': 3}, None),
    # Pot sets make the well fed buff (5% damage) stronger, on top of the Healthy diet perk
    ('%_damage', '(Set Effect) Cooking Pot Set', 0.84 * 0.05, {'CookingPotSet': 2}, 'Well fed'),
    ('%_damage', '(Set Effect) Pot Set', 0.40 * 0.05, {'PotSet': 2}, 'Well fed'),
    ('%_damage', '(Set Effect) Welder Set', 1.0, {'PlateSet': 3}, 'Burning'),
    ('%_damage_against_bosses', '(Set Effect) Golem Set', 0.2, {'GolemSet': 2}, None),
    ('%_critical_hit_damage_against_burning', '(Set Effect) Flame Set', 0.27, {'FlameSet': 2}, None), # Only counts against burning targets (engine/dps_utils.py)
    ('%_melee_and_range_attack_speed', '(Set Effect) Octarine Set', LOW_HEALTH_MISSING_HEALTH_PERCENT * 0.002, {'OctarineSet': 3}, 'Low health'), # 0.2% per 1% missing health
    ('%_damage', '(Set Effect) Carapace Set', 0.238, {'CarapaceArmorSet': 2}, 'Recently mined'),
    # Magic
    ('+_max_mana', '(Set Effect) Azure Set', 15, {'AzureSet': 2}, None),
    ('%_mana_regen_while_casting', '(Set Effect) Mage High Set', 0.3, {'MageHighSet': 3}, None),
    ('%_barrier_as_magic_damage', '(Set Effect) Mage Low Set', 0.06, {'MageLowSet': 3}, None),
    ('%_magic_damage_from_mana', '(Set Effect) Mage Mid Set', 0.26, {'MageMidSet': 3}, None),
    ('%_magic_damage_on_crit', '(Set Effect) Soaring Set', 0.23, {'SoaringSet': 3}, None),
    ('%_magic_damage_near_water', '(Set Effect) Swamp Mage Set', 0.3, {'SwampMageSet': 2}, None),
    ('%_barrier_as_mana_regen', '(Set Effect) Warped Set', 0.01, {'WarpedSet': 2}, None),
    # Summoning (Desert Guardian 3-piece: minions explode when they despawn; not modeled, minions don't despawn)
    ('+_max_minions', '(Set Effect) Chieftain Set', 2, {'ChieftainSet': 2}, None),
    ('%_minion_damage', '(Set Effect) Desert Guardian Set', 0.25, {'DesertGuardianSet': 2}, None),
    ('%_minion_damage', '(Set Effect) Scholar Set', 0.237, {'ScholarSet': 2}, None),
    ('%_minion_attack_speed', '(Set Effect) Witch Doctor Set', 0.315, {'SummonerLowSet': 3}, None),
    ('%_minion_critical_hit_chance', '(Set Effect) Corrupt Warden Set', 0.15, {'SummonerMidSet': 3}, None),
    ('%_magic_to_minion_damage', '(Set Effect) Grim Set', 0.48, {'SummonerHighSet': 3}, None),
    # Explosives (Sulfur 3-piece: explosion when you take damage; not modeled)
    ('%_explosives_damage', '(Set Effect) Sulfur Set', 0.25, {'SulfurSet': 2}, None),
]

def set_bonus_value(value, perks): return value(perks) if callable(value) else value

def item_groups(item):
    """Sets and groups an item counts toward"""
    groups = set()
    if item.set is not None: groups.add(item.set)
    if item.attributes.get('+_burn_damage_on_hit', 0) > 0: groups.add(BURN_SOURCE)
    return groups

def count_set_pieces(set_keywords):
    """Number of distinct equipped items per set or group (two copies of the same ring count once)"""
    counts = {}
    for groups in set_keywords.values():
        for group in groups: counts[group] = counts.get(group, 0) + 1
    return counts

class Character():
    def __init__(self, skill_levels: dict, perks: dict, items: dict = None, food_effects = None, potion_effects = None, settings: dict = None):
        self.skill_levels = skill_levels
        
        perk_to_label = {
            'Mining':    ['Efficient excavation', 'Meticulous miner', 'Self-mending alloy', 'Miner\'s strength', 'Mine, mine, mine!', 'Explosives engineer', 'Pick and run!', 'Archaeologist'],
            'Running':   ['Endurance runner', 'Balanced stance', 'Gotta go fast!', 'On your toes', 'Escape artist', 'Keeping tempo', 'Encumbering presence', 'Breaking barriers'],
            'Melee':     ['Quick strikes', 'Building anger', 'Fast and furious', 'Heavy swings', 'Stubborn fighter', 'Taking a step back', 'Seething blade', 'Strength of the Ancients'],
            'Vitality':  ['Maxed out!', 'Strong and healthy', 'Desperate fighter', 'Stayin\' alive', 'Healing potency', 'Lingering potions', 'Protection of the Ancients', 'Cheat death'],
            'Crafting':  ['Base builder', 'The right tools in the right hands', 'High quality equipment', 'Alchemist', 'Industry specialist', 'Blacksmith', 'Jewelry crafter', 'Unbreakable'],
            'Range':     ['Rapid shots', 'Keeping momentum', 'Weakness detection', 'Slimy bullets', 'Charging in', 'Stun shot', 'Focused accuracy', 'Amplified precision'],
            'Gardening': ['Grateful gardener', 'Eat your vegetables!', 'Feast for the eyes', 'Thorny weapons', 'Thorny skin', 'Poison coated weapons', 'Expert gardener', 'Potent poison'],
            'Fishing':   ['Improved bait', 'Fisherman\'s luck', 'Angler\'s advantage', 'Studied patterns', 'Steady feet', 'Chewy bait', 'Well-trained aim', 'Power of Omega-3!'],
            'Cooking':   ['Utilizing every nutrient', 'Not so picky', 'Healthy diet', 'Fast food', 'Long-lasting food', 'The smell of food', 'Master chef', 'Sharing is caring'],
            'Magic':     ['True sight', 'Mana channeling', 'Arcane frenzy', 'The best offense', 'Mental defense', 'Arcane transfusion', 'Fully charged', 'Mana recharge'],
            'Explosives': ['High Velocity Charge', 'Phantom Bombs', 'Auto Salvage', 'Composite Armor', 'Mana Blast', 'Adrenaline Rush', 'After Burn', 'Napalm'],
            'Summoning': ['Efficient binding', 'Ferocious creatures', 'Critical command', 'Trickle down arcana', 'Tough gang', 'Group effort', 'Heartbound horde', 'Power in numbers'],
        }

        self.perks = {}
        for skill, tier_choices in perks.items():
            self.perks[skill] = {perk_to_label[skill][i]: v for i, v in enumerate(tier_choices)}
        for skill, labels in perk_to_label.items(): # Skills missing from older configs: no points
            self.perks.setdefault(skill, {label: 0 for label in labels})
    
        self.items = {
            'Weapon': None, 'Helm': None, 'Breast armor': None, 'Pants armor': None, 'Necklace': None,
            'Ring1': None, 'Ring2': None, 'Offhand': None, 'Lantern': None, 'Bag': None, 'Pet': None,
        }

        self.settings = settings if settings is not None else {
            'Well fed': True,
            'Max health': True,
            'Low health': False,
            'Running stacks': True,
            'Range stacks': True,
            'Standing still': False,
            'Melee stacks': True,
            'Consumables active': True,
            'Ate fish-derived food': True,
            'Pyrdra soul': True,
            'Druidra soul': True,       # +10% max health (Summoning: Heartbound horde)
            'Cursed target': True,      # Summoning: your scepter's curse works on the target (minions deal 40% more damage)
            'Summon active': True,
            'Not hit': True,            # Pandorium set: you haven't taken damage
            'Kill stacks': True,        # Scarlet set: 5 kill stacks of crit chance
            'Recently dodged': True,    # Assassin set: attack speed after a dodge
            'Burning': True,            # Welder set: you are burning (so your hits set targets burning too)
            'Recently mined': True,     # Carapace set: damage after mining a wall
            'Vs boss': True,            # Target is a boss: damage against bosses applies
            'Adjacent to water': True,  # Magic: standing next to water (Swamp Mage set, Lily Pad items)
            'Full barrier': True,       # Magic: your magic barrier is full (not worn down by hits), for barrier-based damage and mana
            'Fight length': 60,         # Seconds of continuous attacking, starting at full mana and with unpoisoned targets (a number, not on/off)
            'Permanent max health': 590, # Max health from permanent foods eaten (all ten: 590; read from the save when a character is loaded)
        }

        if items is not None:
            for item_category, item in items.items():
                self.items[item_category] = item

        self.food_effects = food_effects
        self.potion_effects = potion_effects

    def equip(self, item):
        if item.item_category=='Ring':
            self.items[item.item_category + ('1' if self.items['Ring1'] is None else '2')] = item
        else: 
            self.items[item.item_category] = item

    def unequip_items(self, except_categories=[]):
        for item_category in [ic for ic in self.items.keys() if ic not in except_categories]:
            self.items[item_category] = None

    def reinforce_items(self): [item.reinforce() for item in self.items.values() if item is not None]

    def printable_loadout(self): return ', '.join([item_name for item_name in self.items.keys() if item_name is not None])

    def get_consumables_active_effects(self):
        active_effects = {k: {} for k in ACTIVE_EFFECTS_DICT.keys()}
        if self.settings['Consumables active']:
            if self.food_effects is not None:
                [self.update_effect(active_effects[k], *item) for k in self.food_effects.keys() for item in self.food_effects[k].items()]
            if self.potion_effects is not None:
                [self.update_effect(active_effects[k], *item) for k in self.potion_effects.keys() for item in self.potion_effects[k].items()]

        return active_effects

    def get_item_active_effects(self, return_set=True):
        active_effects = {k: {} for k in ACTIVE_EFFECTS_DICT.keys()}
        set_keywords = {}
        for item_category, item in self.items.items():
            if item is not None:
                set_keywords.update({item.name: item_groups(item)})
                for attribute_name, value in item.attributes.items():
                    self.update_effect(active_effects[attribute_name], f'(Item Effect: {item_category}) {item.name}', value)
        set_counts = count_set_pieces(set_keywords)
        for attribute, label, value, required_pieces, setting in SET_BONUSES:
            active = all(set_counts.get(set_name, 0)>=n for set_name, n in required_pieces.items()) and (setting is None or self.settings[setting])
            self.update_effect(active_effects[attribute], label, set_bonus_value(value, self.perks) if active else 0)

        if return_set: return active_effects, set_keywords
        return active_effects
    
    def get_character_active_effects(self):
        active_effects = {k: {} for k in ACTIVE_EFFECTS_DICT.keys()}

        self.update_effect(active_effects['%_damage'], '(Cooking Perk) The smell of food', self.perks['Cooking']['The smell of food'] * 0.04)
        self.update_effect(active_effects['%_damage'], '(Setting) Pyrdra soul', self.settings['Pyrdra soul'] * 0.1)
        self.update_effect(active_effects['%_damage'], '(Vitality Perk) Strong and healthy', self.perks['Vitality']['Strong and healthy'] * 0.02 if self.settings['Max health'] else 0)
        self.update_effect(active_effects['%_damage'], '(Vitality Perk) Desperate fighter', self.perks['Vitality']['Desperate fighter'] * 0.04 if self.settings['Low health'] else 0)
        self.update_effect(active_effects['%_damage'], '(Cooking Perk) Healthy diet', (1 + (self.perks['Cooking']['Healthy diet']) * 0.2) * 0.05 if self.settings['Well fed'] else 0)
        self.update_effect(active_effects['%_damage'], '(Running Perk) Keeping tempo', self.perks['Running']['Keeping tempo'] * 0.03 if self.settings['Running stacks'] else 0)
        self.update_effect(active_effects['%_critical_hit_chance'], '(Magic Perk) True sight', self.perks['Magic']['True sight'] * 0.01)
        self.update_effect(active_effects['%_critical_hit_damage'], '(Base Effect) Base', 0.5)
        self.update_effect(active_effects['%_critical_hit_damage'], '(Gardening Perk) Thorny weapons', self.perks['Gardening']['Thorny weapons'] * 0.05)
        self.update_effect(active_effects['%_critical_hit_damage'], '(Range Perk) Amplified precision', self.perks['Range']['Amplified precision'] * 0.08)
        self.update_effect(active_effects['%_damage_against_bosses'], '(Melee Perk) Strength of the Ancients', self.perks['Melee']['Strength of the Ancients'] * 0.04)
        self.update_effect(active_effects['%_damage_against_bosses'], '(Fishing Perk) Power of Omega-3!', self.perks['Fishing']['Power of Omega-3!'] * 0.03 if self.settings['Ate fish-derived food'] else 0)
        self.update_effect(active_effects['+_thorns_damage'], '(Gardening Perk) Thorny skin', self.perks['Gardening']['Thorny skin'] * 10)
        self.update_effect(active_effects['%_chance_to_apply_poison'], '(Gardening Perk) Poison coated weapons', self.perks['Gardening']['Poison coated weapons'] * 0.03)
        self.update_effect(active_effects['%_damage_against_poisoned'], '(Gardening Perk) Potent poison', self.perks['Gardening']['Potent poison'] * 0.05)
        # Explosions (grenades, mortars, zookas): only explosives bonuses
        if self.items['Weapon'].explosive_damage:
            self.update_effect(active_effects['%_explosives_damage'], '(Explosives Skill) Skill level bonus', self.skill_levels.get('Explosives', 0) * 0.01)
            self.update_effect(active_effects['%_explosives_damage'], '(Mining Perk) Explosives engineer', self.perks['Mining']['Explosives engineer'] * 0.04)
            self.update_effect(active_effects['%_napalm_chance'], '(Explosives Perk) Napalm', self.perks['Explosives']['Napalm'] * 0.2)
            self.update_effect(active_effects['%_burning_damage'], '(Explosives Perk) After Burn', self.perks['Explosives']['After Burn'] * 0.1)

        weapon = self.items['Weapon']
        physical = weapon.damage_type in ('Melee', 'Range')
        # Range/melee talents follow how the weapon hits; the Range/Melee skills and flat fishing/mining damage are physical only
        if weapon.delivery=='Range':
            if physical: self.update_effect(active_effects['%_physical_range_damage'], '(Range Skill) Skill level bonus', self.skill_levels['Range']/200)
            self.update_effect(active_effects['%_range_damage'], '(Range Perk) Keeping momentum', self.perks['Range']['Keeping momentum'] * 2 * 0.02 if self.settings['Range stacks'] else 0)
            self.update_effect(active_effects['%_range_damage'], '(Range Perk) Focused accuracy', self.perks['Range']['Focused accuracy'] * 0.05 if self.settings['Standing still'] else 0)
            self.update_effect(active_effects['%_range_attack_speed'], '(Range Perk) Rapid shots', self.perks['Range']['Rapid shots'] * 0.02)
            self.update_effect(active_effects['%_range_attack_speed'], '(Summoning Perk) Power in numbers', self.perks['Summoning']['Power in numbers'] * 0.01 if self.settings['Summon active'] and weapon.damage_type != 'Summoning' else 0) # 1% per minion; assumes one (summoners: the real count, in the formula)
            if physical: self.update_effect(active_effects['+_fishing'], '(Fishing Skill) Skill level bonus', self.skill_levels['Fishing'])
        if weapon.delivery=='Melee':
            if physical: self.update_effect(active_effects['%_physical_melee_damage'], '(Melee Skill) Skill level bonus', self.skill_levels['Melee']/200)
            self.update_effect(active_effects['%_melee_damage'], '(Melee Perk) Building anger', self.perks['Melee']['Building anger'] * 2 * 0.02 if self.settings['Melee stacks'] else 0)
            self.update_effect(active_effects['%_melee_damage'], '(Melee Perk) Stubborn fighter', self.perks['Melee']['Stubborn fighter'] * 0.03 if self.settings['Melee stacks'] else 0)
            self.update_effect(active_effects['%_melee_attack_speed'], '(Melee Perk) Quick strikes', self.perks['Melee']['Quick strikes'] * 0.02)
            if physical:
                self.update_effect(active_effects['+_mining_damage'], '(Mining Skill) Skill level bonus', self.skill_levels['Mining'])
                self.update_effect(active_effects['+_mining_damage'], '(Base Effect) Base', 20)
                self.update_effect(active_effects['%_mining_damage'], '(Mining Perk) Efficient excavation', self.perks['Mining']['Efficient excavation'] * 0.02)
        scepter = getattr(weapon, 'scepter', None) # Summoners attack with a scepter (model/summoning.py)
        if weapon.damage_type == 'Magic' or scepter is not None:
            magic = self.perks['Magic']
            self.update_effect(active_effects['%_magic_damage'], '(Magic Skill) Skill level bonus', self.skill_levels['Magic']/200)
            self.update_effect(active_effects['+_max_mana'], '(Base Effect) Base', 100)
            self.update_effect(active_effects['+_mana_regen'], '(Base Effect) Base', 10)
            self.update_effect(active_effects['%_magic_damage_from_mana'], '(Magic Perk) Fully charged', magic['Fully charged'] * 0.06)
            self.update_effect(active_effects['%_barrier_as_magic_damage'], '(Magic Perk) The best offense', magic['The best offense'] * 0.04)
            self.update_effect(active_effects['%_barrier_as_mana_regen'], '(Magic Perk) Arcane transfusion', magic['Arcane transfusion'] * 0.005)
            self.update_effect(active_effects['%_mana_regen_while_casting'], '(Magic Perk) Mana recharge', magic['Mana recharge'] * 0.06)
            # Mana channeling, Arcane frenzy and Mental defense are in the DPS formula (engine/dps_utils.py)
        if weapon.damage_type == 'Summoning':
            # Minions only get effects that say minion; your magic damage bonus counts for Trickle down arcana and the Grim set
            summoning = self.perks['Summoning']
            self.update_effect(active_effects['%_minion_damage'], '(Summoning Skill) Skill level bonus', self.skill_levels['Summoning']/200)
            self.update_effect(active_effects['%_minion_attack_speed'], '(Summoning Perk) Ferocious creatures', summoning['Ferocious creatures'] * 0.04)
            self.update_effect(active_effects['%_minion_critical_hit_chance'], '(Summoning Perk) Critical command', summoning['Critical command'] * 0.04)
            self.update_effect(active_effects['%_magic_to_minion_damage'], '(Summoning Perk) Trickle down arcana', summoning['Trickle down arcana'] * 0.1)
            self.update_effect(active_effects['%_mana_reservation_reduction'], '(Summoning Perk) Efficient binding', summoning['Efficient binding'] * 0.08)
            if scepter is None: # With a scepter, the magic effects above already count these
                self.update_effect(active_effects['%_magic_damage'], '(Magic Skill) Skill level bonus', self.skill_levels['Magic']/200)
                self.update_effect(active_effects['+_max_mana'], '(Base Effect) Base', 100)
            # Max health (Heartbound horde, in the formula): flat sources, then percentages
            self.update_effect(active_effects['+_max_health'], '(Base Effect) Base', 100)
            self.update_effect(active_effects['+_max_health'], '(Vitality Skill) Skill level bonus', self.skill_levels['Vitality'])
            self.update_effect(active_effects['+_max_health'], '(Vitality Perk) Maxed out!', round(self.perks['Vitality']['Maxed out!'] * 0.06 * sum(self.skill_levels.values())))
            self.update_effect(active_effects['+_max_health'], '(Setting) Permanent max health', self.settings['Permanent max health'])
            self.update_effect(active_effects['%_max_health'], '(Setting) Druidra soul', 0.1 if self.settings['Druidra soul'] else 0)
            self.update_effect(active_effects['%_max_health'], '(Cooking Perk) Well fed', (1 + self.perks['Cooking']['Healthy diet'] * 0.2) * 0.05 if self.settings['Well fed'] else 0)

        return active_effects
    

    def update_effect(self, effect: dict, key: str, value): 
        if value != 0: effect.update({key: value})


    def get_active_effects(self):
        active_effects = {k: {} for k in ACTIVE_EFFECTS_DICT.keys()}

        item_effects, set_keywords = self.get_item_active_effects()
        character_effects = self.get_character_active_effects()
        consumables_effects = self.get_consumables_active_effects()

        [[self.update_effect(active_effects[k], *item) for k in effects.keys() for item in effects[k].items()] for effects in [item_effects, character_effects, consumables_effects]]

        return active_effects, set_keywords