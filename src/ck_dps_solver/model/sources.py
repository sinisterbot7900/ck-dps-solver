"""Where an item comes from, in words, from the wiki's obtaining data (Module:Obtaining/data).

Chances are per kill, chest or catch. Drops that also have a "guaranteed" roll (one item picked from a pool) show
the combined chance of getting at least one.
"""
import re

from ck_dps_solver.model.item_stats import find_internal_id, wiki_data
from ck_dps_solver.model.progression import _BIOME_OF_AREA

# Fishing water types that aren't biome areas
LIQUIDS = {'Mold': 'mold water', 'Sea': 'sea water', 'Lava': 'lava', 'Slime': 'slime'}


def _name(object_id):
    return wiki_data()['objects'].get(object_id, {}).get('name', object_id)


def _scene_name(scene):
    """Structure names are internal ids (e.g. 'SMCityArchive'); split them into words"""
    return re.sub(r'(?<=[a-z0-9])(?=[A-Z])|(?<=[A-Z])(?=[A-Z][a-z])', ' ', scene)


def _percent(chance):
    return f'{chance * 100:.2g}%' if chance < 0.1 else f'{chance * 100:.0f}%'


def _at_least_one(source):
    chance = source.get('chanceAtLeastOne', source.get('chance', 0)) or 0
    guaranteed = source.get('guaranteedChanceAtLeastOne', source.get('guaranteedChance', 0)) or 0
    return 1 - (1 - chance) * (1 - guaranteed)


def _best_by_name(sources, limit):
    """(name, lowest chance, highest chance) per entity name, most likely first: variations of one chest or crate are
    merged, and their chances can differ (e.g. the common Wooden Crate 0.83%, other variants 2%)"""
    found = {}
    for source in sources:
        name = _name((source.get('entity') or {}).get('id'))
        chance = _at_least_one(source)
        low, high = found.get(name, (chance, chance))
        found[name] = (min(low, chance), max(high, chance))
    return sorted(((name, low, high) for name, (low, high) in found.items()), key=lambda row: -row[2])[:limit]


def _chance_range(low, high):
    return _percent(high) if _percent(low) == _percent(high) else f'{_percent(low)}–{_percent(high)}'


def sources(internal_id, limit=3):
    """Ways to get an item, most reliable first, e.g. ['Crafted at Scarlet Workbench', 'Dropped by Floracada (34%)']"""
    record = wiki_data()['equipment'].get(internal_id) or wiki_data().get('consumables', {}).get(internal_id, {}) # Gear, or food and potions
    obtaining = record.get('obtaining') or {}
    lines = []
    for source in obtaining.get('crafting', []):
        materials = ', '.join(f"{m['amount']} {_name(m['id'])}" for m in record.get('materials', []))
        lines.append(f"Crafted at {_name(source['station'])}" + (f' ({materials})' if materials else ''))
    for source in obtaining.get('polishing', []):
        lines.append(f"Polish a {_name(source['id'])} (Jewelry crafter talent)")
    for kind, verb in [('merchant', 'Sold by'), ('vendor', 'Sold by'), ('trading', 'Traded by')]:
        for source in obtaining.get(kind, []):
            lines.append(f"{verb} {_name(source.get('id') or source.get('station'))}")
    for source in obtaining.get('backgroundPerks', []):
        lines.append(f"Starting item for the {source['background']} background")
    for source in obtaining.get('recipe', []):
        lines.append(f"Made from {_name(source['item'])}")
    drops = _best_by_name(obtaining.get('drop', []), limit)
    if drops:
        lines.append('Dropped by ' + ', '.join(f'{name} ({_chance_range(low, high)})' for name, low, high in drops))
    chests = _best_by_name(obtaining.get('loot', []), limit)
    if chests:
        lines.append('Found in ' + ', '.join(f'{name} ({_chance_range(low, high)})' for name, low, high in chests))
    for kind in ('lootScene', 'dropScene'):
        for source in obtaining.get(kind, [])[:limit]:
            scenes = [_scene_name(s) for s in source.get('scenes') or []] + [f'{_scene_name(d)} dungeon' for d in source.get('dungeons') or []]
            where = ', '.join(scenes[:3]) + (f' (+{len(scenes) - 3} more)' if len(scenes) > 3 else '') or 'structures'
            lines.append(f"{_name((source.get('entity') or {}).get('id'))} in {where} ({_percent(_at_least_one(source))})")
    for source in obtaining.get('fishing', []):
        places = [_BIOME_OF_AREA.get(b, b) for b in source.get('biomes') or []] + [LIQUIDS.get(l, l) for l in source.get('liquids') or []]
        lines.append(f"Fishing in {' / '.join(places) or 'any water'} ({_percent(source.get('chance', 0))} of loot catches)")
    for source in obtaining.get('salvage', []):
        lines.append(f"Salvaged from {_name(source['id'])}")
    if obtaining.get('naturalSpawn'):
        lines.insert(0, 'Grows or spawns naturally in the world')
    lines = lines or ['Unknown (not in the wiki data)']
    categories = wiki_data()['objects'].get(internal_id, {}).get('categories', [])
    if 'Seasonal' in categories:
        season = next((c for c in categories if c not in ('Seasonal', 'Equipment') and c != record.get('type')), None)
        lines.insert(0, f"Seasonal: {season + ' event' if season else 'event'} only")
    return lines


def is_seasonal(name):
    internal_id = find_internal_id(name.split(' (')[0])
    return internal_id is not None and 'Seasonal' in wiki_data()['objects'].get(internal_id, {}).get('categories', [])


def where_to_get(name, limit=3):
    """sources() for an item by display name (e.g. 'Lily Pad Hat'), joined into one line"""
    internal_id = find_internal_id(name.split(' (')[0])
    return '; '.join(sources(internal_id, limit)) if internal_id else 'Unknown (not in the wiki data)'
