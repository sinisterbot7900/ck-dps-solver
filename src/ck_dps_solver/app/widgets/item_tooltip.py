"""Hover text for an item in a loadout: the stats the DPS calculation used (reinforced as in the search)."""
import copy
import html
import re

from ck_dps_solver.engine.dominance import unused_attributes
from ck_dps_solver.model import Weapon
from ck_dps_solver.model.weapon import SummonerKit

from ck_dps_solver.app import theme


def _effect(attribute, value):
    label = attribute[2:].replace('_', ' ')
    sign = '+' if value > 0 else '-'
    return f'{sign}{abs(value) * 100:.3g}% {label}' if attribute.startswith('%_') else f'{sign}{abs(value):g} {label}'


def _set_name(set_id):
    """'SwampMageSet' -> 'Swamp Mage set'"""
    name = re.sub(r'Set$', '', str(set_id))
    return re.sub(r'(?<=[a-z])(?=[A-Z])', ' ', name) + ' set'


def _weapon_lines(weapon):
    lines = []
    if isinstance(weapon, SummonerKit):
        lines.append(f'Tome: {weapon.min_damage:g}–{weapon.max_damage:g} minion damage')
        if weapon.scepter is not None:
            lines.append(f'Scepter: {weapon.scepter_min_damage:g}–{weapon.scepter_max_damage:g} damage, {weapon.scepter_attacks_per_second:.3g} attacks/s'
                         + (f', {weapon.scepter_mana_cost:g} mana per attack' if weapon.scepter_mana_cost else '')
                         + (', curses targets' if weapon.curses else ''))
        return lines
    lines.append(f'{weapon.min_damage:g}–{weapon.max_damage:g} damage, {weapon.attacks_per_second:.3g} attacks/s ({weapon.damage_type.lower()})')
    if weapon.mana_cost:
        lines.append(f'{weapon.mana_cost:g} mana per attack')
    if getattr(weapon, 'aura_damage', 0):
        lines.append(f'Aura: {weapon.aura_damage:g} damage')
    if getattr(weapon, 'explosive_damage', 0):
        lines.append(f'Explosion: {weapon.explosive_damage:g} damage')
    return lines


def item_tooltip(item, damage_type):
    """Rich text for an item (None or the empty item: no text)"""
    if item is None or item.name == 'None':
        return None
    shown = copy.deepcopy(item)
    shown.reinforce() # As in the search (no change for items that can't be reinforced)
    muted = theme.color('text_muted').name()
    unused = set(unused_attributes(damage_type))
    details = [f'level {item.level}' if item.level is not None else None, 'reinforced' if shown.reinforced else None,
               _set_name(shown.set) if shown.set else None]
    parts = [f'<b>{html.escape(item.name)}</b>']
    if any(details):
        parts.append(f'<span style="color:{muted}">' + ', '.join(d for d in details if d) + '</span>')
    if isinstance(shown, Weapon):
        parts += [html.escape(line) for line in _weapon_lines(shown)]
    stats = [(attribute, value) for attribute, value in shown.attributes.items() if value]
    for attribute, value in stats:
        text = html.escape(_effect(attribute, value))
        parts.append(f'<span style="color:{muted}">{text} (not used by {damage_type.lower()})</span>' if attribute in unused else text)
    if not stats and not isinstance(shown, Weapon):
        parts.append(f'<span style="color:{muted}">No stats the calculation uses</span>')
    return '<br>'.join(parts)
