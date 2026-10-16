# Flat (not percentage) attributes, rounded to whole numbers when reinforced
FLAT_ATTRIBUTES = {'+_fishing', '+_mining_damage', '+_thorns_damage', '+_burn_damage_on_hit', '+_max_mana', '+_magic_barrier', '+_max_minions', '+_max_health'}


class Item():
    def __init__(self, name, item_category, consider_for, set = None, attributes: dict = {}, reinforced = False, has_durability = None, level = None):
        self.name = name
        self.level = level # Item level the stats are for, when known (e.g. read from a save file)
        self.item_category = item_category
        self.consider_for = consider_for
        self.set = set
        self.attributes = {
            '%_damage': 0.,
            '%_physical_melee_damage': 0.,
            '%_physical_range_damage': 0.,
            '%_mining_damage': 0.,
            '%_melee_attack_speed': 0.,
            '%_range_attack_speed': 0.,
            '%_melee_and_range_attack_speed': 0.,
            '%_damage_against_bosses': 0.,
            '%_critical_hit_damage': 0.,
            '%_critical_hit_chance': 0.,
            '%_damage_against_burning': 0.,
            '%_critical_hit_damage_against_burning': 0.,
            '%_triple_hit_chance': 0.,
            '+_fishing': 0.,
            '+_mining_damage': 0.,
            '+_thorns_damage': 0.,
            '%_chance_to_apply_poison': 0.,
            '%_pet_poison_chance': 0.,
            '%_damage_against_poisoned': 0.,
            '%_critical_hit_chance_after_poisoning': 0.,
            '%_range_damage_while_standing_still': 0.,
            '%_melee_attack_speed_proc_chance': 0.,
            '+_burn_damage_on_hit': 0.,
            '%_melee_damage': 0.,
            '%_range_damage': 0.,
            '%_magic_damage': 0.,
            '%_magic_damage_near_water': 0.,
            '%_magic_damage_from_mana': 0.,
            '%_magic_damage_on_crit': 0.,
            '+_max_mana': 0.,
            '+_mana_regen': 0.,
            '%_mana_regen_while_casting': 0.,
            '%_mana_regen_delay_reduction': 0.,
            '%_minion_damage': 0.,
            '%_minion_attack_speed': 0.,
            '%_minion_critical_hit_chance': 0.,
            '%_minion_critical_hit_damage': 0.,
            '%_minion_damage_against_bosses': 0.,
            '+_max_minions': 0.,
            '%_mana_reservation_reduction': 0.,
            '%_magic_to_minion_damage': 0.,
            '+_max_health': 0.,
            '%_max_health': 0.,
            '%_explosives_damage': 0.,
            '%_napalm_chance': 0.,
            '%_burning_damage': 0.,
            '+_magic_barrier': 0.,
            '%_barrier_as_magic_damage': 0.,
            '%_barrier_as_mana_regen': 0.,
        }

        for attribute_name, value in attributes.items():
            self.attributes[attribute_name] += value
            
        # Whether the item can be reinforced. Default: armor can, other items can't
        self.has_durability = has_durability if has_durability is not None else item_category in ['Helm', 'Breast armor', 'Pants armor']
        self.reinforced = False
        if has_durability: self.reinforced = reinforced
        if reinforced and has_durability: self.reinforce()

    def reinforce(self):
        if not self.reinforced and self.has_durability:
            self.reinforced = True
            self.attributes = {k: round(v*1.15, 0 if k in FLAT_ATTRIBUTES else 3) for k, v in self.attributes.items()}