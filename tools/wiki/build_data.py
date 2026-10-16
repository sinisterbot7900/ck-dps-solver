"""Build data/wiki_data.json from the wiki's Lua data modules.

Usage: python -m tools.wiki.build_data [--refresh]
  --refresh  ignore the local cache and download the modules again
"""
import datetime
import json
import os
import sys

from .fetch import DATA_MODULES, fetch_pages, module_game_version
from .lua_table import parse

from tools import PACKAGE_DIR, REPO  # noqa: F401 (REPO: used by the other wiki tools)

OUTPUT = os.path.join(PACKAGE_DIR, 'data', 'wiki_data.json')

# Object types kept with full detail (anything a character can equip)
EQUIPMENT_TYPES = {'Helm', 'BreastArmor', 'PantsArmor', 'Necklace', 'Ring', 'Offhand', 'Bag', 'Lantern', 'Pet', 'BeamWeapon', 'MiningPick',
                   'MeleeWeapon', 'RangeWeapon', 'MagicWeapon', 'SummoningWeapon', 'ThrowingWeapon'}
EQUIPMENT_FIELDS = ['id', 'name', 'type', 'rarity', 'level', 'durability', 'cooldown', 'meleeDamage', 'rangeDamage', 'magicDamage',
                    'summonDamage', 'equipped', 'pet', 'conditions', 'categories', 'tags', 'reinforce', 'area', 'mana', 'materials', 'minion']
CONDITION_FIELDS = ['id', 'description', 'descriptionIsAPercentage', 'showDecimal', 'effect', 'isAdditiveWithSelf', 'isUnique', 'isPermanent']


def base_record(record):
    return record.get(0) if isinstance(record, dict) else None


def build(refresh=False):
    pages = fetch_pages(DATA_MODULES, use_cache=not refresh)
    missing = [t for t, p in pages.items() if p is None]
    if missing:
        raise RuntimeError(f'Missing wiki modules: {missing}')
    parsed = {title: parse(page['content']) for title, page in pages.items()}

    objects, equipment = {}, {}
    for internal_id, record in parsed['Module:ObjectInfo/data'].items():
        b0 = base_record(record)
        if not isinstance(b0, dict) or 'id' not in b0:
            continue
        objects[internal_id] = {'id': b0['id'], 'name': b0.get('name', internal_id), 'type': b0.get('type'), 'categories': b0.get('categories', [])}
        if b0.get('type') in EQUIPMENT_TYPES:
            equipment[internal_id] = {k: b0[k] for k in EQUIPMENT_FIELDS if k in b0}
            # Explosion damage of the weapon's projectile (grenades, mortars, zookas...), by level
            projectile = base_record(parsed['Module:ObjectInfo/data'].get(b0.get('projectile'))) if b0.get('projectile') else None
            if isinstance(projectile, dict) and isinstance(projectile.get('explosiveDamage'), dict):
                equipment[internal_id]['explosiveDamage'] = projectile['explosiveDamage']

    set_data = parsed['Module:SetBonusInfo/data']
    for internal_id, set_id in set_data.get('associatedSetBonuses', {}).items():
        if internal_id in equipment:
            equipment[internal_id]['set'] = set_id

    # Where each item comes from (drops, chests, crafting, fishing, merchants...): see model/sources.py
    # Objects that only drop from enemies: [(entity, chance of at least one)] (used to detect beaten bosses from saves)
    drop_only = {}
    for internal_id, record in parsed['Module:Obtaining/data'].items():
        b0 = base_record(record)
        if not isinstance(b0, dict):
            continue
        if internal_id in equipment:
            equipment[internal_id]['obtaining'] = b0
        if isinstance(internal_id, str) and set(b0) == {'drop'}:
            drop_only[internal_id] = [[(d.get('entity') or {}).get('id'), max(d.get('chanceAtLeastOne') or 0, d.get('guaranteedChanceAtLeastOne') or 0)]
                                      for d in b0['drop']]

    conditions = {cid: {k: c[k] for k in CONDITION_FIELDS if k in c} for cid, c in parsed['Module:ConditionInfo/data'].items()}
    minions = {}
    for internal_id, record in parsed['Module:ObjectInfo/data'].items():
        b0 = base_record(record)
        if isinstance(b0, dict) and 'Minion' in (b0.get('categories') or []):
            minions[internal_id] = {k: b0[k] for k in ('name', 'conditions', 'meleeAttackState', 'rangeAttackState') if k in b0}

    # Food and potions: effects when eaten/drunk (conditions) and an ingredient's effects in a cooked dish (cookedConditions)
    consumables = {}
    for internal_id, record in parsed['Module:ObjectInfo/data'].items():
        b0 = base_record(record)
        if isinstance(b0, dict) and b0.get('type') == 'Eatable' and isinstance(b0.get('consumed'), dict):
            consumed = b0['consumed']
            consumables[internal_id] = {'name': b0.get('name', internal_id), 'categories': b0.get('categories', []), 'area': b0.get('area'),
                                        'rareIngredient': bool(consumed.get('rareIngredient')), 'conditions': consumed.get('conditions', []),
                                        'cooked': consumed.get('cookedConditions', [])}
            obtaining = base_record(parsed['Module:Obtaining/data'].get(internal_id, {}))
            if isinstance(obtaining, dict) and obtaining:
                consumables[internal_id]['obtaining'] = obtaining # Where to get it (model/sources.py)

    # Skills: id, experience curve, and talent display names in talent tree order (the order of points in saves)
    skill_data = parsed['Module:SkillInfo/data']
    raw_talents = skill_data.get('talents', {})
    skills = {}
    for name, info in skill_data.get('skills', {}).items():
        order = info.get('talents', {})
        names = [raw_talents.get(order.get(i, order.get(str(i))), {}).get('displayName') for i in range(len(order))]
        skills[name] = {'id': info['id'], 'displayName': info.get('displayName', name), 'mulFactor': info.get('mulFactor'),
                        'baseFactor': info.get('baseFactor'), 'maxLevel': info.get('maxLevel'), 'talents': names, 'iconColor': info.get('iconColor')}

    talents = {}
    def walk(node):
        if isinstance(node, dict):
            if 'displayName' in node and 'condition' in node and 'skill' in node:
                talents[node['displayName']] = {k: node[k] for k in ('skill', 'tier', 'condition', 'conditionValuePerPoint') if k in node}
            for v in node.values(): walk(v)
        elif isinstance(node, list):
            for v in node: walk(v)
    walk(parsed['Module:SkillInfo/data'])

    versions = [{k: v[k] for k in ('version', 'group', 'name', 'hotfix', 'highlights') if k in v} | {'release': (v.get('release') or {}).get('windows')}
                for v in parsed['Module:VersionInfo/data'] if isinstance(v, dict) and 'version' in v]

    data = {
        'meta': {
            'built_at': datetime.datetime.now(datetime.timezone.utc).isoformat(timespec='seconds'),
            'source': 'https://core-keeper.fandom.com (CC BY-SA)',
            'modules': {title: {'game_version': module_game_version(page['content']), 'revision': page['timestamp']} for title, page in pages.items()},
            'latest_game_version': versions[0]['version'] if versions else None,
        },
        'objects': objects,
        'equipment': equipment,
        'sets': set_data['setBonuses'],
        'conditions': conditions,
        'consumables': consumables,
        'minions': minions,
        'drop_only': drop_only,
        'talents': talents,
        'skills': skills,
        'pets': parsed['Module:PetInfo/data'],
        'versions': versions,
    }
    os.makedirs(os.path.dirname(OUTPUT), exist_ok=True)
    with open(OUTPUT, 'w', encoding='utf8') as f:
        json.dump(data, f, indent=1, ensure_ascii=False, sort_keys=True)
    return data


if __name__ == '__main__':
    d = build(refresh='--refresh' in sys.argv)
    print(f"wrote {OUTPUT}: {len(d['objects'])} objects, {len(d['equipment'])} equipment, {len(d['sets'])} sets, "
          f"{len(d['conditions'])} conditions, {len(d['talents'])} talents")
    for title, m in d['meta']['modules'].items():
        print(f"   {title}: game version {m['game_version']}, revised {m['revision']}")
    print('latest game version on the wiki:', d['meta']['latest_game_version'])
