"""Build Item/Weapon objects from data/wiki_data.json at any item level.

This is the single place that maps wiki conditions to the solver's attributes. catalogue.py is generated
with the same mapping, and the save-file filter uses it to score owned items at their actual level.
"""
import functools
import json
import os

from ck_dps_solver.model import Item, Weapon

from ck_dps_solver.paths import resource

DATA_PATH = resource('data', 'wiki_data.json')

# Wiki condition id -> solver attribute. Conditions not listed here don't affect the solver.
CONDITION_ATTRIBUTES = {
    'AllDamageIncrease': '%_damage',
    'AllDamageDecrease': '%_damage', # Stored as a negative value
    'AuraApplyDamageIncrease': '%_damage',
    'DamageIncreaseAgainstPoisoned': '%_damage_against_poisoned',
    'PhysicalMeleeDamageIncrease': '%_physical_melee_damage',
    'MeleeDamageIncrease': '%_melee_damage',
    'PhysicalRangeDamageIncrease': '%_physical_range_damage',
    'RangeDamageIncrease': '%_range_damage',
    'MiningPercentageIncrease': '%_mining_damage',
    'MeleeAttackSpeedIncrease': '%_melee_attack_speed',
    'RangeAttackSpeedIncrease': '%_range_attack_speed',
    'AttackSpeed': '%_melee_and_range_attack_speed',
    'IncreasedDamageAgainstBosses': '%_damage_against_bosses',
    'CriticalDamagePercentageIncrease': '%_critical_hit_damage',
    'CriticalDamagePercentageIncreaseFromRange': '%_critical_hit_damage',
    'CritChance': '%_critical_hit_chance',
    'CriticalHitChanceFromShot': '%_critical_hit_chance',
    'DamageIncreaseAgainstBurning': '%_damage_against_burning',
    'CritDamageIncreaseAgainstBurning': '%_critical_hit_damage_against_burning',
    'ChanceToDealTripleDamage': '%_triple_hit_chance',
    'IncreasedFishing': '+_fishing',
    'MiningIncrease': '+_mining_damage',
    'ThornsDamage': '+_thorns_damage',
    'ChanceToApplyPoisoned': '%_chance_to_apply_poison',
    'ApplyBurning': '+_burn_damage_on_hit', # Makes the item a burn source; burn damage itself isn't modeled
    'GainRangeDamageIncreaseFromStandingStill': '%_range_damage_while_standing_still',
    'ChanceOnHitToGainMeleeAttackSpeed': '%_melee_attack_speed_proc_chance',
    # Magic
    'IncreasedMagicDamagePercentage': '%_magic_damage',
    'MagicDamageIncreaseFromPotion': '%_magic_damage',
    # Potions (separate effects from food's, so they stack with it)
    'MeleeDamageIncreaseFromPotion': '%_physical_melee_damage',
    'RangeDamageIncreaseFromPotion': '%_physical_range_damage',
    'AttackSpeedIncreaseFromPotion': '%_melee_and_range_attack_speed',
    'IncreasedMagicDamagePercentageWhileAdjacentToWater': '%_magic_damage_near_water',
    'IncreasedMagicDamagePercentageFromAdjacentWater': '%_magic_damage_near_water',
    'GainRemainingManaAsMagicDamagePercentage': '%_magic_damage_from_mana',
    'GainMagicDamagePercentageBoostAfterCrit': '%_magic_damage_on_crit',
    'IncreasedMaxMana': '+_max_mana',
    'IncreasedManaRegen': '+_mana_regen',
    'IncreasedManaRegenPercentageWhileCasting': '%_mana_regen_while_casting',
    'ReducedManaRegenDelayPercentage': '%_mana_regen_delay_reduction',
    # Summoning (minions only get effects that say minion)
    'IncreasedMinionDamagePercentage': '%_minion_damage',
    'MinionDamageIncreaseFromPotion': '%_minion_damage',
    'IncreasedMinionAttackSpeed': '%_minion_attack_speed',
    'IncreasedMinionCritChance': '%_minion_critical_hit_chance',
    'IncreasedMinionCritDamagePercentage': '%_minion_critical_hit_damage',
    'IncreasedMinionBossDamagePercentage': '%_minion_damage_against_bosses',
    'IncreasedMaxMinions': '+_max_minions',
    'ReducedManaReservationPercentage': '%_mana_reservation_reduction',
    'IncreasedMagicDamageToMinionDamage': '%_magic_to_minion_damage',
    'IncreasedMaxHealth': '+_max_health', # Heartbound horde: minion attack speed per 10 max health
    'IncreasedMaxHealthPercentage': '%_max_health',
    # Explosives
    'IncreasedExplosivesDamage': '%_explosives_damage',
    'ChanceToSpawnNapalmFromExplosives': '%_napalm_chance',
    'ChanceToSpawnNapalmOnExplosion': '%_napalm_chance',
    'IncreasedBurningDamagePercentage': '%_burning_damage',
    'MagicBarrier': '+_magic_barrier',
    'PercentageOfMagicBarrierAsMagicDamage': '%_barrier_as_magic_damage',
    'MagicBarrierAsManaRegen': '%_barrier_as_mana_regen',
}

# Conditions that never affect damage (not flagged as "not modeled" on generated items)
IGNORED_CONDITIONS = {'ArmorIncrease', 'OrangeGlow', 'BlueGlow', 'MovementSpeedIncrease', 'LifeOnHit', 'HealOverTime',
                      'MiningSpeedIncrease', 'DodgeChance', 'ManaBarrier', 'ApplyTakeMoreDamageFromMinions'}

# Wiki object type -> Item.item_category
ITEM_CATEGORIES = {
    'Helm': 'Helm', 'BreastArmor': 'Breast armor', 'PantsArmor': 'Pants armor', 'Necklace': 'Necklace', 'Ring': 'Ring',
    'Offhand': 'Offhand', 'Bag': 'Bag', 'Lantern': 'Lantern', 'Pet': 'Pet',
}
# Wiki weapon types, and the damage values (wiki field -> Weapon.damage_type) the DPS formula supports
WEAPON_TYPES = {'MeleeWeapon', 'RangeWeapon', 'BeamWeapon', 'SummoningWeapon', 'ThrowingWeapon'}
WEAPON_DAMAGE_TYPES = {'meleeDamage': 'Melee', 'rangeDamage': 'Range', 'magicDamage': 'Magic'}

# Attributes that only matter for one damage type, used to decide which searches an item is considered for
DAMAGE_TYPE_ATTRIBUTES = {
    'Melee': {'%_physical_melee_damage', '%_melee_attack_speed', '%_mining_damage', '+_mining_damage', '%_melee_attack_speed_proc_chance'},
    'Range': {'%_physical_range_damage', '%_range_attack_speed', '+_fishing', '%_range_damage_while_standing_still', '%_range_damage'},
    'Explosives': {'%_explosives_damage', '%_napalm_chance', '%_burning_damage'},
    'Summoning': {'%_minion_damage', '%_minion_attack_speed', '%_minion_critical_hit_chance', '%_minion_critical_hit_damage',
                  '%_minion_damage_against_bosses', '+_max_minions', '%_mana_reservation_reduction', '%_magic_to_minion_damage'},
    'Magic': {'%_magic_damage', '%_magic_damage_near_water', '%_magic_damage_from_mana', '%_magic_damage_on_crit', '+_max_mana', '+_mana_regen',
              '%_mana_regen_while_casting', '%_mana_regen_delay_reduction', '+_magic_barrier', '%_barrier_as_magic_damage', '%_barrier_as_mana_regen'},
}
# Summon tomes: each minion's attack cycle in seconds (the wiki's tome pages; contact minions: the cooldown after a hit,
# assuming steady contact with the target). Minions not listed (the Pickaxe: no known rate) aren't usable.
MINION_ATTACK_SECONDS = {'BatMinion': 1.66, 'FireMiteMinion': 1.73, 'MeleeMinion': 1.83, 'PoisonMinion': 1.66, 'OrbitingMinion': 0.5, 'RadiatingMinion': 0.5}
# Minion auras: wiki condition -> seconds between hits (the Radioactive Minion's radiation, every 2 sec)
MINION_AURAS = {'AuraApplyRadioactiveDamageOverTime': 2.0}

# Attributes only physical weapons use
PHYSICAL_ONLY_ATTRIBUTES = {'%_physical_melee_damage', '%_physical_range_damage', '+_fishing', '+_mining_damage', '%_mining_damage'}


def considered_for(item, damage_type):
    """Whether an item belongs in a search for a damage type. Magic and summoning searches go by the item's stats (magic
    also takes range and melee items that help magic weapons: attack speed, range/melee damage, crits...)."""
    if item.item_category == 'Weapon':
        # Summoners also hold a scepter (its curse makes minions deal more damage): see model/summoning.py
        return item.damage_type == damage_type or (damage_type == 'Summoning' and getattr(item, 'curses', False))
    # Explosives and summoning go by stats only ("Both" means melee and range, whose generic stats don't help them)
    if damage_type == 'Explosives': # Explosions only get explosives bonuses
        return set_helps(item.set, damage_type) or any(v for k, v in item.attributes.items() if k in DAMAGE_TYPE_ATTRIBUTES['Explosives'])
    if damage_type == 'Summoning': # Items for the minions (see dominance.SUMMON_ITEM_ATTRIBUTES)
        from ck_dps_solver.engine.dominance import SUMMON_ITEM_ATTRIBUTES
        return set_helps(item.set, damage_type) or any(v for k, v in item.attributes.items() if k in SUMMON_ITEM_ATTRIBUTES)
    if item.consider_for in (damage_type, 'Both'):
        return True
    if damage_type == 'Magic': # By stats: any the damage type uses
        from ck_dps_solver.engine.dominance import unused_attributes
        unused = set(unused_attributes(damage_type))
        return set_helps(item.set, damage_type) or any(v for k, v in item.attributes.items() if k not in unused)
    return False


def set_helps(set_id, damage_type):
    """Whether a set has a bonus (or formula effect) a damage type can use, e.g. not a mining-damage set for magic"""
    if set_id is None:
        return False
    from ck_dps_solver.model.character import SET_BONUSES
    from ck_dps_solver.engine.dominance import FORMULA_SETS_FOR, unused_attributes
    from ck_dps_solver.engine.dps_utils import FORMULA_SETS
    if damage_type == 'Explosives': # Sets with an explosives bonus (the formula's sets don't affect explosions)
        return any(set_id in required and attribute in DAMAGE_TYPE_ATTRIBUTES['Explosives'] for attribute, _, _, required, _ in SET_BONUSES)
    if damage_type == 'Summoning': # Sets with a bonus for the minions
        from ck_dps_solver.engine.dominance import SUMMON_ITEM_ATTRIBUTES
        return any(set_id in required and attribute in SUMMON_ITEM_ATTRIBUTES for attribute, _, _, required, _ in SET_BONUSES)
    unused = set(unused_attributes(damage_type))
    if any(set_id in required and attribute not in unused for attribute, _, _, required, _ in SET_BONUSES):
        return True
    return set_id in FORMULA_SETS and damage_type in FORMULA_SETS_FOR.get(set_id, {damage_type})


@functools.lru_cache(maxsize=1)
def wiki_data():
    with open(DATA_PATH, encoding='utf8') as f:
        return json.load(f)


def value_at_level(value, level):
    """Per-level values are {level: value}; use the highest level at or below `level` (or the lowest available)"""
    if not isinstance(value, dict):
        return value
    levels = sorted(int(k) for k in value)
    at = max([lv for lv in levels if lv <= level] or levels[:1])
    return value[str(at)] if str(at) in value else value[at]


def scale_condition(condition_id, raw):
    """Wiki percentages are stored in tenths (showDecimal) or whole percents; flat values with showDecimal in tenths (mana regen)"""
    condition = wiki_data()['conditions'].get(condition_id, {})
    if not condition.get('descriptionIsAPercentage'):
        return round(raw / 10, 4) if condition.get('showDecimal') else raw
    return round(raw / (1000 if condition.get('showDecimal') else 100), 4)


def item_attributes(internal_id, level):
    """(attributes, unmodeled condition ids) of an equipment item at a level"""
    record = wiki_data()['equipment'][internal_id]
    attributes, unmodeled = {}, []
    conditions = (record.get('equipped') or {}).get('conditions', []) if record.get('type') != 'Pet' else record.get('conditions', [])
    for condition in conditions:
        attribute = CONDITION_ATTRIBUTES.get(condition['id'])
        if attribute is None:
            unmodeled.append(condition['id'])
            continue
        attributes[attribute] = attributes.get(attribute, 0) + scale_condition(condition['id'], value_at_level(condition['value'], level))
    return {k: v for k, v in attributes.items() if v}, unmodeled


def infer_consider_for(attributes, damage_type=None):
    """Which damage type searches an item belongs in: a specific one if all its attributes are specific to it"""
    if damage_type is not None:
        return damage_type
    keys = set(attributes)
    for candidate, specific in DAMAGE_TYPE_ATTRIBUTES.items():
        if keys and keys <= specific:
            return candidate
    return 'Both'


def has_durability(record):
    """Whether the item can be reinforced (the wiki lists reinforcement materials for it)"""
    return bool(record.get('reinforce'))


def find_internal_id(name):
    """Internal id of an equipment item from its display name"""
    for internal_id, record in wiki_data()['equipment'].items():
        if record.get('name') == name:
            return internal_id
    return None


def make_item(internal_id, level, consider_for=None):
    """Item or Weapon for an equipment item at a level (unreinforced), or None if the solver can't use it"""
    record = wiki_data()['equipment'][internal_id]
    attributes, _ = item_attributes(internal_id, level)
    item_set = record.get('set')
    if record['type'] == 'ThrowingWeapon': # Grenades: an explosion every throw (a fixed rate)
        if not record.get('explosiveDamage') or not record.get('cooldown'):
            return None
        return Weapon(name=record['name'], min_damage=0, max_damage=0, attacks_per_second=round(1 / record['cooldown'], 4), damage_type='Explosives',
                      consider_for=consider_for or 'Explosives', set=item_set, attributes=attributes, has_durability=False, level=level,
                      explosive_damage=value_at_level(record['explosiveDamage'], level))
    if record['type'] == 'SummoningWeapon':
        minion = record.get('minion') or {}
        seconds = MINION_ATTACK_SECONDS.get(minion.get('type'))
        if seconds is None or not minion.get('damage'):
            return None
        damage = value_at_level(minion['damage'], level)
        aura = sum(c['value'] / MINION_AURAS[c['id']] for c in wiki_data().get('minions', {}).get(minion['type'], {}).get('conditions') or []
                   if isinstance(c, dict) and c.get('id') in MINION_AURAS)
        return Weapon(name=record['name'], min_damage=round(damage * 0.9), max_damage=round(damage * 1.1), attacks_per_second=round(1 / seconds, 4),
                      damage_type='Summoning', consider_for=consider_for or 'Summoning', set=item_set, attributes=attributes,
                      has_durability=has_durability(record), level=level, delivery='Minion',
                      mana_cost=value_at_level(record['mana'], level) if record.get('mana') else 0, aura_damage=round(aura, 4))
    if record['type'] in WEAPON_TYPES:
        damage_key = next((k for k in WEAPON_DAMAGE_TYPES if record.get(k)), None)
        if damage_key is None or not record.get('cooldown'):
            return None
        damage_type = WEAPON_DAMAGE_TYPES[damage_key]
        damage = value_at_level(record[damage_key], level)
        # Physical weapons hit the way their damage type says; magic staffs, scepters and beams hit at range, magic swords in melee
        delivery = damage_type if damage_type != 'Magic' else ('Melee' if record['type'] == 'MeleeWeapon' else 'Range')
        mana_cost = value_at_level(record['mana'], level) if damage_type == 'Magic' and record.get('mana') is not None else 0
        return Weapon(name=record['name'], min_damage=round(damage * 0.9), max_damage=round(damage * 1.1),
                      attacks_per_second=round(1 / record['cooldown'], 4), damage_type=damage_type,
                      consider_for=consider_for or damage_type, set=item_set, attributes=attributes, has_durability=has_durability(record), level=level,
                      delivery=delivery, mana_cost=mana_cost,
                      # Mortars and zookas explode too (a magic staff's bouncing explosion rarely hits: not counted)
                      explosive_damage=value_at_level(record['explosiveDamage'], level) if record.get('explosiveDamage') and damage_type != 'Magic' else 0,
                      curses=any(c['id'] == 'ApplyTakeMoreDamageFromMinions' for c in (record.get('equipped') or {}).get('conditions', [])))
    category = ITEM_CATEGORIES.get(record['type'])
    if category is None:
        return None
    return Item(name=record['name'], item_category=category, consider_for=consider_for or infer_consider_for(attributes),
                set=item_set, attributes=attributes, has_durability=has_durability(record), level=level)
