"""A loadout's stats as the game's character screen shows them (display only: health, armor, damage per hit, attack
speed, crit, boss damage reduction, mining, fishing...).

Stats the DPS formula uses come from Character (the same numbers as the search); defensive and utility stats it doesn't
use (armor, dodge, movement speed, health regen, life on hit, damage reduction from bosses) come from the wiki data of
each item at its level, reinforced items +15%.
"""
import copy
import math

from ck_dps_solver.engine.batch_search import loadout_items
from ck_dps_solver.model import Character
from ck_dps_solver.model.character import count_set_pieces
from ck_dps_solver.model.consumables import DEFAULT_DISH_RARITY, DISH_RARITIES, GOLDEN_PAIR_MULTIPLIER, cooked_conditions
from ck_dps_solver.model.item_stats import find_internal_id, scale_condition, value_at_level, wiki_data

# Display-only wiki conditions -> sheet stat
DISPLAY_CONDITIONS = {
    'ArmorIncrease': 'armor', 'ArmorPercentageIncrease': 'armor_pct', 'DodgeChance': 'dodge', 'MovementSpeedIncrease': 'movement',
    'MovementSpeedDecrease': 'movement', 'LifeOnHit': 'life_on_hit', 'HealOverTime': 'regen', 'ReducedDamageFromBosses': 'boss_reduction',
    'IncreasedHealthRegenEffectiveness': 'regen_effectiveness',
}


# Set armor the wiki doesn't list, read in game: set -> (pieces, armor, name). Witch Doctor set (level 3, reinforced):
# pieces 3 / 5 / 4, any two add up exactly (8, 9, 7), all three show 13.
HIDDEN_SET_ARMOR = {'SummonerLowSet': (3, 1, 'Witch Doctor set (3 pieces)')}


def _item_display(item):
    """Display-only stats of an equipped item from the wiki data (at its level; +15% if reinforced)"""
    internal_id = find_internal_id(item.name.split(' (')[0])
    record = wiki_data()['equipment'].get(internal_id) if internal_id else None
    if not record:
        return {}
    conditions = record.get('conditions', []) if record.get('type') == 'Pet' else (record.get('equipped') or {}).get('conditions', [])
    level = item.level or 20
    found = {}
    for condition in conditions:
        stat = DISPLAY_CONDITIONS.get(condition['id'])
        if stat is None:
            continue
        value = scale_condition(condition['id'], value_at_level(condition['value'], level))
        if getattr(item, 'reinforced', False):
            # Reinforced flat armor rounds up, as the game shows each piece (Witch Doctor set at level 3: 2, 4, 3 -> 3, 5, 4)
            value = math.ceil(value * 1.15 - 1e-9) if stat == 'armor' else value * 1.15
        found[stat] = found.get(stat, 0) + value
    return found


def _food_display(keys, dish_rarity, golden):
    """Display-only stats from the chosen food and potions (strongest per effect, like their other effects)"""
    best = {}
    for key in keys:
        kind, internal_id = key.split(':', 1)
        record = wiki_data().get('consumables', {}).get(internal_id)
        if kind == 'cooked': # An owned dish: its own ingredients and rarity
            conditions, multiplier = cooked_conditions(key)
        elif record is None:
            continue
        elif kind == 'dish':
            conditions = record['cooked']
            multiplier = 1.0 if not golden else DISH_RARITIES[dish_rarity] * (GOLDEN_PAIR_MULTIPLIER if record['rareIngredient'] else 1.0)
        else:
            conditions, multiplier = record['conditions'], 1.0
        for condition in conditions:
            if condition['id'] in DISPLAY_CONDITIONS and condition.get('duration', 1) and condition['id'] != 'HealOverTime':
                value = scale_condition(condition['id'], condition['value']) * multiplier
                best[condition['id']] = max(best.get(condition['id'], 0), value)
    found = {}
    for condition_id, value in best.items():
        stat = DISPLAY_CONDITIONS[condition_id]
        found[stat] = found.get(stat, 0) + value
    return found


def defense_parts(loadout, fixed, character_kwargs, consumable_keys=(), dish_rarity=DEFAULT_DISH_RARITY, golden=True):
    """Where the sheet's display-only stats come from: {stat: [(source, value)]} (stat: 'armor', 'dodge', 'movement',
    'regen', 'life_on_hit', 'boss_reduction', ...), the same values as the sheet"""
    return sheet(loadout, fixed, character_kwargs, consumable_keys, dish_rarity, golden, want_parts=True)


def sheet(loadout, fixed, character_kwargs, consumable_keys=(), dish_rarity=DEFAULT_DISH_RARITY, golden=True, want_parts=False):
    """[(group, label, value text)] for a search result loadout (want_parts: see defense_parts)"""
    items = [copy.deepcopy(item) for item in loadout_items(loadout, fixed) if item.name != 'None']
    for item in items: item.reinforce()
    character = Character(**character_kwargs)
    for item in items: character.equip(item)
    effects, set_keywords = character.get_active_effects()
    e = {k: sum(v.values()) for k, v in effects.items()}
    settings, perks, levels = character.settings, character.perks, character.skill_levels
    weapon = character.items['Weapon']

    display, parts = {}, {} # parts: stat -> [(source, value)] for "where stats come from"
    def add(stat, source, value):
        if value:
            display[stat] = display.get(stat, 0) + value
            parts.setdefault(stat, []).append((source, value))
    shown_items = list(items)
    if getattr(weapon, 'scepter', None) is not None: # Summoners hold the scepter
        shown_items = [weapon.scepter] + [i for i in items if i is not weapon]
    for item in shown_items:
        for stat, value in _item_display(item).items():
            add(stat, f'(Item) {item.name}', value)
    if settings.get('Consumables active', True):
        for stat, value in _food_display(consumable_keys, dish_rarity, golden).items():
            add(stat, '(Food and potions)', value)
    vitality = perks['Vitality']
    add('boss_reduction', '(Vitality Perk) Protection of the Ancients', vitality['Protection of the Ancients'] * 0.03)
    add('dodge', '(Fishing Perk) Studied patterns', perks['Fishing']['Studied patterns'] * 0.02)
    add('regen_effectiveness', '(Vitality Perk) Healing potency', vitality['Healing potency'] * 0.06)
    pieces = count_set_pieces(set_keywords)
    for set_id, (needed, armor, label) in HIDDEN_SET_ARMOR.items():
        if pieces.get(set_id, 0) >= needed:
            add('armor', f'(Set) {label}', armor)
    if want_parts:
        return parts

    # Max health: flat sources, then percentages (checked against a save)
    item_health = sum(item.attributes.get('+_max_health', 0) for item in shown_items)
    food_health = sum(v for k, v in effects['+_max_health'].items() if k.startswith(('(Dish Effect)', '(Potion Effect)', '(Food Effect)')))
    flat = 100 + levels.get('Vitality', 0) + round(vitality['Maxed out!'] * 0.06 * sum(levels.values())) + settings.get('Permanent max health', 0) + item_health + food_health
    percent = sum(item.attributes.get('%_max_health', 0) for item in shown_items) + (0.1 if settings.get('Druidra soul') else 0)
    if settings.get('Well fed'):
        percent += (1 + perks['Cooking']['Healthy diet'] * 0.2) * 0.05
    max_health = math.floor(flat * (1 + percent) + 0.5) # Rounded to the nearest, as the game shows it (196 x 1.05 -> 206)

    pct = lambda v: f'{v * 100:.1f}%'
    rows = [('Health', 'Max health', f'{max_health:,}'),
            ('Health', 'Health regeneration', f"{display.get('regen', 0):.1f}/s" + (f" (+{pct(display['regen_effectiveness'])} effectiveness)" if display.get('regen_effectiveness') else '')),
            ('Health', 'Life on melee hit', f"{display.get('life_on_hit', 0):g}"),
            ('Defense', 'Armor', f"{display.get('armor', 0) * (1 + display.get('armor_pct', 0)):.0f}"),
            ('Defense', 'Dodge chance', pct(display.get('dodge', 0))),
            ('Defense', 'Damage taken from bosses', f"-{pct(display.get('boss_reduction', 0))}"),
            ('Defense', 'Movement speed', f"+{pct(display.get('movement', 0))}")]

    # Damage per hit before crits: the weapon's damage with its always-on bonuses (not procs or uptimes)
    if weapon.damage_type == 'Summoning':
        multiplier = 1 + e['%_minion_damage'] + e['%_magic_to_minion_damage'] * e['%_magic_damage']
        rows.append(('Damage', 'Minion damage per hit', f'{math.ceil(weapon.min_damage * multiplier):,} - {math.floor(weapon.max_damage * multiplier):,}'))
        rows.append(('Damage', 'Minion attack speed', f"+{pct(e['%_minion_attack_speed'])}"))
        rows.append(('Damage', 'Minion crit chance', pct(min(e['%_minion_critical_hit_chance'], 1))))
        rows.append(('Damage', 'Max minions', f"{1 + e['+_max_minions']:g}"))
    elif weapon.damage_type == 'Explosives':
        rows.append(('Damage', 'Explosion damage', f"{weapon.explosive_damage * (1 + e['%_explosives_damage']):,.0f}"))
    if weapon.damage_type in ('Melee', 'Range', 'Magic') or getattr(weapon, 'scepter', None) is not None:
        scepter = getattr(weapon, 'scepter', None)
        attacker = scepter or weapon
        is_range = attacker.delivery == 'Range'
        low_base, high_base, rate = ((weapon.scepter_min_damage, weapon.scepter_max_damage, weapon.scepter_attacks_per_second) if scepter is not None
                                     else (weapon.min_damage, weapon.max_damage, weapon.attacks_per_second))
        if attacker.damage_type == 'Magic':
            typed = e['%_magic_damage']
        else:
            typed = e['%_physical_range_damage'] if is_range else e['%_physical_melee_damage']
        multiplier = 1 + e['%_damage'] + typed + (e['%_range_damage'] if is_range else e['%_melee_damage'])
        thorns = e['+_thorns_damage'] if any(i.set == 'ScarabSet' for i in items) and sum(i.set == 'ScarabSet' for i in items) >= 3 else 0
        low = math.ceil((low_base + thorns * 0.9) * multiplier)
        high = math.floor((high_base + thorns * 1.1) * multiplier)
        label = 'Scepter damage per hit' if attacker is not weapon else 'Damage per hit'
        rows.append(('Damage', label, f'{low:,} - {high:,}' + (' (with thorns)' if thorns else '')))
        if weapon.explosive_damage:
            rows.append(('Damage', 'Explosion damage', f"{weapon.explosive_damage * (1 + e['%_explosives_damage']):,.0f}"))
        speed = (e['%_range_attack_speed'] if is_range else e['%_melee_attack_speed']) + e['%_melee_and_range_attack_speed']
        rows.append(('Damage', f"{'Range' if is_range else 'Melee'} attack speed", f'+{pct(speed)} ({rate * (1 + speed):.2f} attacks/s)'))
        rows.append(('Damage', 'Critical hit chance', pct(min(e['%_critical_hit_chance'], 1))))
        rows.append(('Damage', 'Critical hit damage', f"+{pct(e['%_critical_hit_damage'])}"))
        rows.append(('Damage', 'Damage', f"+{pct(e['%_damage'])}"))
    rows.append(('Damage', 'Damage against bosses', f"+{pct(e['%_damage_against_bosses'])}"))
    rows.append(('Damage', 'Thorns damage', f"{e['+_thorns_damage']:.0f}"))
    if e['+_max_mana']:
        rows.append(('Magic', 'Max mana', f"{e['+_max_mana']:.0f}"))
        rows.append(('Magic', 'Mana regeneration', f"{e['+_mana_regen']:.1f}/s"))
        rows.append(('Magic', 'Magic barrier', f"{e['+_magic_barrier']:.0f}"))
    # Mining and fishing apply whatever you hold (the DPS formula only counts them for melee and range weapons)
    gear = lambda attribute: sum(item.attributes.get(attribute, 0) for item in shown_items) + sum(effects[attribute][k] for k in effects[attribute] if k.startswith(('(Dish Effect)', '(Potion Effect)', '(Food Effect)')))
    mining_pct = gear('%_mining_damage') + perks['Mining']['Efficient excavation'] * 0.02
    mining = (20 + levels.get('Mining', 0) + gear('+_mining_damage')) * (1 + mining_pct)
    rows.append(('Other', 'Mining damage', f'{mining:,.0f}' + (f' (+{pct(mining_pct)})' if mining_pct else '')))
    rows.append(('Other', 'Fishing', f"{levels.get('Fishing', 0) + gear('+_fishing'):.0f}"))
    return rows
