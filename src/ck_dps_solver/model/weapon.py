from ck_dps_solver.model.item import FLAT_ATTRIBUTES, Item
import math

class Weapon(Item):
    def __init__(self, name, min_damage, max_damage, attacks_per_second, damage_type, consider_for, set = None, attributes: dict = {}, reinforced = False,
                 has_durability = True, level = None, delivery = None, mana_cost = 0, aura_damage = 0, curses = False, explosive_damage = 0):
        super().__init__(name, 'Weapon', consider_for, set, attributes, reinforced, has_durability, level)
        self.min_damage = min_damage
        self.max_damage = max_damage
        self.attacks_per_second = attacks_per_second
        self.damage_type = damage_type # 'Melee', 'Range', 'Magic', 'Summoning' or 'Explosives'
        # How hits land: 'Melee' or 'Range' (magic weapons: staffs and scepters are range, the Zealot's Scimitar melee).
        # Range/melee talents and attack speed follow the delivery; physical damage bonuses only apply to physical weapons.
        self.delivery = delivery or {'Magic': 'Range', 'Summoning': 'Minion', 'Explosives': 'Thrown'}.get(damage_type, damage_type)
        self.mana_cost = mana_cost # Mana per attack (magic weapons), or mana each minion reserves (summon tomes)
        # Summon tomes: min/max_damage and attacks_per_second are the minion's; aura_damage is damage per second from
        # the minion's aura (counted once, auras don't stack)
        self.aura_damage = aura_damage
        self.curses = curses # Scepters: hits curse targets, so minions deal 40% more damage to them
        # Explosion per attack (grenades; mortars and zookas on top of their range hit). Explosions only get explosives bonuses
        self.explosive_damage = explosive_damage

    def reinforce(self):
        if not self.reinforced and self.has_durability:
            self.reinforced = True
            self.attributes = {k: round(v*1.15, 0 if k in FLAT_ATTRIBUTES else 3) for k, v in self.attributes.items()}
            self.min_damage = math.ceil(self.min_damage*1.15)
            self.max_damage = math.floor(self.max_damage*1.15)
            self.explosive_damage = round(self.explosive_damage*1.15)


class SummonerKit(Weapon):
    """A summoner's two weapons: a summon tome (its minions keep fighting) and a scepter held and attacked with.
    Damage and attack speed are the minions'; the scepter's are in scepter_*. Equipped effects are the scepter's (it's
    the one held). scepter is None for a tome alone."""
    def __init__(self, tome, scepter=None):
        name = tome.name + (f' + {scepter.name}' if scepter is not None else '')
        super().__init__(name, tome.min_damage, tome.max_damage, tome.attacks_per_second, 'Summoning', 'Summoning',
                         set=scepter.set if scepter is not None else tome.set, attributes=scepter.attributes if scepter is not None else tome.attributes,
                         has_durability=tome.has_durability or (scepter is not None and scepter.has_durability), delivery='Range' if scepter is not None else 'Minion',
                         mana_cost=tome.mana_cost, aura_damage=tome.aura_damage)
        self.tome, self.scepter = tome, scepter
        # The parts' values are copied as they are now: a part already reinforced (e.g. a scepter an earlier magic search
        # reinforced in place) mustn't be reinforced again by the kit
        self.parts_reinforced = (tome.reinforced, scepter is not None and scepter.reinforced)
        self.level = None # Shown in the name instead
        self.scepter_min_damage = scepter.min_damage if scepter is not None else 0
        self.scepter_max_damage = scepter.max_damage if scepter is not None else 0
        self.scepter_attacks_per_second = scepter.attacks_per_second if scepter is not None else 0
        self.scepter_mana_cost = scepter.mana_cost if scepter is not None else 0
        self.curses = scepter is not None and scepter.curses

    def reinforce(self):
        if self.reinforced:
            return
        self.reinforced = True
        tome_done, scepter_done = self.parts_reinforced
        if self.tome.has_durability and not tome_done:
            self.min_damage = math.ceil(self.min_damage*1.15)
            self.max_damage = math.floor(self.max_damage*1.15)
        if self.scepter is not None and self.scepter.has_durability and not scepter_done:
            self.attributes = {k: round(v*1.15, 0 if k in FLAT_ATTRIBUTES else 3) for k, v in self.attributes.items()}
            self.scepter_min_damage = math.ceil(self.scepter_min_damage*1.15)
            self.scepter_max_damage = math.floor(self.scepter_max_damage*1.15)
