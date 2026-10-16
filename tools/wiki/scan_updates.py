"""Check the wiki for game updates since the last scan and report what changed for the solver.

Usage:
  python -m tools.wiki.scan_updates            check, rebuild data if the wiki changed, write tools/wiki/update_report.md
  python -m tools.wiki.scan_updates --force    rebuild and report even if nothing changed
  python -m tools.wiki.scan_updates --mark-scanned   record the current wiki state as scanned (after implementing)

State is kept in tools/wiki/wiki_state.json: the last scanned game version and the module revisions it was built from.
"""
import datetime
import json
import os
import re
import sys

from .build_data import OUTPUT as DATA_PATH, build
from .fetch import DATA_MODULES, fetch_pages, latest_revision_timestamps

HERE = os.path.dirname(os.path.abspath(__file__))
STATE_PATH = os.path.join(HERE, 'wiki_state.json') # The last scan (game version, module revisions)
REPORT_PATH = os.path.join(HERE, 'update_report.md') # Written by each scan (not in git)
WIKI_PAGE = 'https://core-keeper.fandom.com/wiki/'


def load_json(path, default=None):
    if not os.path.exists(path):
        return default
    with open(path, encoding='utf8') as f:
        return json.load(f)


def version_key(version):
    return tuple(int(p) if p.isdigit() else 0 for p in re.split(r'[.\-]', version))


def changed_records(old, new):
    """(added, removed, changed) keys between two dicts"""
    added = sorted(set(new) - set(old))
    removed = sorted(set(old) - set(new))
    changed = sorted(k for k in set(old) & set(new) if old[k] != new[k])
    return added, removed, changed


def describe_item_change(old, new):
    parts = []
    for field in sorted(set(old) | set(new)):
        if old.get(field) != new.get(field):
            if field == 'equipped':
                oc = {c['id']: c['value'] for c in (old.get('equipped') or {}).get('conditions', [])}
                nc = {c['id']: c['value'] for c in (new.get('equipped') or {}).get('conditions', [])}
                a, r, ch = changed_records(oc, nc)
                parts += [f'+{c}' for c in a] + [f'-{c}' for c in r] + [f'{c} values' for c in ch]
            else:
                parts.append(field)
    return ', '.join(parts)


def solver_gaps(data):
    """Things in the wiki data the solver doesn't use yet"""
    from ck_dps_solver import catalogue as I
    from ck_dps_solver.model.character import SET_BONUSES
    from ck_dps_solver.model.item_stats import CONDITION_ATTRIBUTES, IGNORED_CONDITIONS, item_attributes, make_item

    catalogue = {name for d in [I.WEAPONS, I.HELMS, I.BREAST_ARMORS, I.PANTS_ARMORS, I.NECKLACES, I.RINGS, I.OFFHANDS, I.BAGS, I.LANTERNS, I.PETS] for name in d}
    missing, unmodeled_conditions = [], {}
    for internal_id, record in data['equipment'].items():
        if record.get('type') == 'Pet':
            continue
        attributes, unmodeled = item_attributes(internal_id, 20)
        item = make_item(internal_id, 20)
        if item is not None and record['name'] not in catalogue and (attributes or item.item_category == 'Weapon' or record.get('set')):
            missing.append(f"{record['name']} ({internal_id}, {record['type']}): {attributes}")
        for c in unmodeled:
            if c not in IGNORED_CONDITIONS:
                unmodeled_conditions.setdefault(c, []).append(record['name'])
    modeled_sets = {s for _, _, _, required, _ in SET_BONUSES for s in required}
    sets = []
    for set_id, info in sorted(data['sets'].items()):
        bonuses = [(b['requiredPieces'], b['condition']['id'], b['condition']['value'], data['conditions'].get(b['condition']['id'], {}).get('description', ''))
                   for b in info['bonuses']]
        sets.append((set_id, set_id in modeled_sets, info['availablePieces'], bonuses))
    return missing, unmodeled_conditions, sets, CONDITION_ATTRIBUTES


def write_report(old_data, new_data, new_versions, patch_pages):
    lines = [f"# Wiki update report ({datetime.date.today().isoformat()})", '',
             f"Latest game version on the wiki: **{new_data['meta']['latest_game_version']}**", '',
             '## Data module versions', '', '| Module | Game version | Revised |', '|---|---|---|']
    for title, m in new_data['meta']['modules'].items():
        lines.append(f"| {title} | {m['game_version']} | {m['revision']} |")

    lines += ['', '## Game versions since the last scan', '']
    if not new_versions:
        lines.append('None.')
    for v in new_versions:
        lines.append(f"### {v['version']}{' (hotfix)' if v.get('hotfix') else ''}{' - ' + v['name'] if v.get('name') else ''} ({v.get('release')})")
        page = patch_pages.get(v['version'])
        if page:
            notes = re.sub(r'\{\{[^}]*\}\}', '', page['content']).strip()
            lines += ['', f"Patch notes ({WIKI_PAGE}{v['version']}):", '', '```', notes[:6000], '```', '']
        else:
            lines += ['', f"No patch notes page. Highlights: {v.get('highlights', '-')}", '']

    if old_data is not None:
        lines += ['## Data changes since the last build', '']
        for section, label in [('equipment', 'Equipment'), ('sets', 'Sets'), ('conditions', 'Conditions'), ('talents', 'Talents')]:
            added, removed, changed = changed_records(old_data.get(section, {}), new_data.get(section, {}))
            lines.append(f'### {label}: {len(added)} added, {len(removed)} removed, {len(changed)} changed')
            for k in added: lines.append(f"- added `{k}` {new_data[section][k].get('name', '') if isinstance(new_data[section][k], dict) else ''}")
            for k in removed: lines.append(f'- removed `{k}`')
            for k in changed:
                detail = describe_item_change(old_data[section][k], new_data[section][k]) if section == 'equipment' else ''
                lines.append(f'- changed `{k}` {detail}')
            lines.append('')

    missing, unmodeled_conditions, sets, _ = solver_gaps(new_data)
    lines += ['## Usable items not in catalogue.py', '']
    lines += [f'- {m}' for m in missing] or ['None.']
    lines += ['', '## Item conditions the solver ignores (condition: items)', '']
    for c, names in sorted(unmodeled_conditions.items(), key=lambda kv: -len(kv[1])):
        desc = new_data['conditions'].get(c, {}).get('description', '')
        lines.append(f"- `{c}` \"{desc}\": {', '.join(sorted(set(names))[:8])}{' ...' if len(set(names)) > 8 else ''}")
    lines += ['', '## Set bonuses (modeled = referenced in model/character.py SET_BONUSES)', '']
    for set_id, modeled, pieces, bonuses in sets:
        bonus_text = '; '.join(f'{n}pc {cid}={value} "{desc}"' for n, cid, value, desc in bonuses)
        lines.append(f"- {'[modeled] ' if modeled else ''}`{set_id}` ({', '.join(pieces)}): {bonus_text}")
    with open(REPORT_PATH, 'w', encoding='utf8') as f:
        f.write('\n'.join(lines) + '\n')


def main(args):
    state = load_json(STATE_PATH, {})
    if '--mark-scanned' in args:
        data = load_json(DATA_PATH)
        state = {'last_scanned_game_version': data['meta']['latest_game_version'],
                 'module_revisions': {t: m['revision'] for t, m in data['meta']['modules'].items()},
                 'scanned_at': datetime.datetime.now(datetime.timezone.utc).isoformat(timespec='seconds')}
        with open(STATE_PATH, 'w', encoding='utf8') as f:
            json.dump(state, f, indent=1)
        print('marked as scanned:', state)
        return

    revisions = latest_revision_timestamps(DATA_MODULES)
    known = state.get('module_revisions', {})
    changed_modules = [t for t, r in revisions.items() if known.get(t) != r]
    if not changed_modules and state and '--force' not in args:
        print('No wiki changes since the last scan', f"(game version {state.get('last_scanned_game_version')}).")
        return

    old_data = load_json(DATA_PATH)
    new_data = build(refresh=bool(changed_modules) or '--force' in args)
    last = state.get('last_scanned_game_version')
    new_versions = [v for v in new_data['versions'] if last is None or version_key(v['version']) > version_key(last)]
    if last is None:
        new_versions = new_versions[:5] # First scan: show the most recent versions only
    patch_pages = fetch_pages([v['version'] for v in new_versions])
    write_report(old_data, new_data, new_versions, patch_pages)
    print(f'Modules changed: {changed_modules or "none (forced)"}')
    print(f'Game versions since last scan ({last}): {[v["version"] for v in new_versions]}')
    print(f'Report: {REPORT_PATH}')


if __name__ == '__main__':
    main(sys.argv[1:])
