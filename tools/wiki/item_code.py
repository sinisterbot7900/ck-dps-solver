"""Write catalogue.py entries from wiki data (used by the update agent and when adding items by hand).

Usage:
  python -m tools.wiki.item_code --level 20 <internal id> [...]           print entries
  python -m tools.wiki.item_code --level 20 --insert <internal id> [...]  add them to catalogue.py
  python -m tools.wiki.item_code --level 20 --sync [--dry]                 update existing catalogue.py entries from the data
"""
import os
import re
import sys

from ck_dps_solver.model.item_stats import item_attributes, make_item, wiki_data, IGNORED_CONDITIONS

from tools import PACKAGE_DIR

ITEMS_PATH = os.path.join(PACKAGE_DIR, 'catalogue.py')
# Item.item_category / weapon -> dictionary in catalogue.py
DICTIONARIES = {'Weapon': 'WEAPONS', 'Helm': 'HELMS', 'Breast armor': 'BREAST_ARMORS', 'Pants armor': 'PANTS_ARMORS', 'Necklace': 'NECKLACES',
                'Ring': 'RINGS', 'Offhand': 'OFFHANDS', 'Bag': 'BAGS', 'Lantern': 'LANTERNS', 'Pet': 'PETS'}


def quote(s):
    return "'" + s.replace("\\", "\\\\").replace("'", "\\'") + "'"


def entry_source(internal_id, level):
    """catalogue.py source for one item, or None if the solver can't use it"""
    item = make_item(internal_id, level)
    if item is None:
        return None
    _, unmodeled = item_attributes(internal_id, level)
    unmodeled = [c for c in unmodeled if c not in IGNORED_CONDITIONS]
    lines = [f"    # Not modeled: {', '.join(unmodeled)}"] if unmodeled else []
    lines += [f"    {quote(item.name)}: {'Weapon' if item.item_category == 'Weapon' else 'Item'}(", f"        name={quote(item.name)},"]
    if item.item_category == 'Weapon':
        lines += [f"        min_damage={item.min_damage},", f"        max_damage={item.max_damage},", f"        attacks_per_second={item.attacks_per_second},",
                  f"        damage_type={quote(item.damage_type)},"]
        if item.damage_type in ('Magic', 'Summoning'):
            lines += [f"        delivery={quote(item.delivery)},", f"        mana_cost={item.mana_cost},"]
        if item.aura_damage:
            lines.append(f"        aura_damage={item.aura_damage},")
        if item.curses:
            lines.append("        curses=True,")
        if item.explosive_damage:
            lines.append(f"        explosive_damage={item.explosive_damage},")
    else:
        lines.append(f"        item_category={quote(item.item_category)},")
    if item.set:
        lines.append(f"        set={quote(item.set)},")
    lines.append(f"        consider_for={quote(item.consider_for)},")
    attributes = {k: v for k, v in item.attributes.items() if v}
    if attributes:
        lines.append('        attributes={')
        lines += [f"            {quote(k)}: {float(v) if k.startswith('+') else v}," for k, v in attributes.items()]
        lines.append('        },')
    # Armor always has durability (Item sets it); weapons default to having it; other items default to not
    if item.item_category == 'Weapon' and not item.has_durability:
        lines.append('        has_durability=False,')
    elif item.item_category in ('Helm', 'Breast armor', 'Pants armor') and not item.has_durability:
        lines.append('        has_durability=False,') # Armor that can't be reinforced
    elif item.item_category not in ('Weapon', 'Helm', 'Breast armor', 'Pants armor') and item.has_durability:
        lines.append('        has_durability=True,')
    lines.append('    ),')
    return item, '\n'.join(lines)


def insert(entries):
    """Append (item, source) entries to their dictionaries in catalogue.py; skips names already present"""
    with open(ITEMS_PATH, encoding='utf8') as f:
        src = f.read()
    added = []
    for item, source in entries:
        if re.search(rf"^    {re.escape(quote(item.name))}: ", src, re.M):
            continue
        name = DICTIONARIES[item.item_category]
        match = re.search(rf'^{name} = \{{\n.*?\n\}}\n', src, re.S | re.M)
        if match is None:
            raise ValueError(f'{name} not found in catalogue.py')
        body = match.group(0)
        src = src.replace(body, body[:-2] + source + '\n}\n')
        added.append(item.name)
    with open(ITEMS_PATH, 'w', encoding='utf8') as f:
        f.write(src)
    return added


BLOCK = re.compile(r"^(?:    # Not modeled: [^\n]*\n)?    '((?:\\'|[^'])*)': (Item|Weapon)\(\n(.*?)^    \),\n", re.S | re.M)


def sync(level, dry_run=False):
    """Regenerate every catalogue.py entry that exists in the wiki data at `level`, keeping each entry's consider_for.
    Returns [(name, old source, new source)] for entries that changed."""
    from ck_dps_solver.model.item_stats import find_internal_id
    with open(ITEMS_PATH, encoding='utf8') as f:
        src = f.read()
    changes = []

    def replace(match):
        name = match.group(1).replace("\\'", "'")
        internal_id = find_internal_id(name)
        if internal_id is None:
            return match.group(0)
        result = entry_source(internal_id, level)
        if result is None or result[0].item_category == 'Pet': # Pets are configured by hand (their talents vary)
            return match.group(0)
        consider_for = re.search(r"^        consider_for='(\w+)',", match.group(0), re.M)
        new = result[1] + '\n'
        if consider_for:
            new = re.sub(r"^        consider_for='\w+',", f"        consider_for='{consider_for.group(1)}',", new, flags=re.M)
        if new != match.group(0):
            changes.append((name, match.group(0), new))
        return new

    new_src = BLOCK.sub(replace, src)
    if not dry_run:
        with open(ITEMS_PATH, 'w', encoding='utf8') as f:
            f.write(new_src)
    return changes


if __name__ == '__main__':
    args = sys.argv[1:]
    if '--sync' in args:
        level = int(args[args.index('--level') + 1]) if '--level' in args else 20
        changes = sync(level, dry_run='--dry' in args)
        for name, old, new in changes:
            print(f'--- {name}\n{old}+++\n{new}')
        print(f"{len(changes)} entries {'would change' if '--dry' in args else 'updated'}")
        sys.exit()
    level = int(args[args.index('--level') + 1]) if '--level' in args else 20
    ids = [a for i, a in enumerate(args) if not a.startswith('--') and (i == 0 or args[i - 1] != '--level')]
    entries = []
    for internal_id in ids:
        if internal_id not in wiki_data()['equipment']:
            print(f'# {internal_id}: not an equipment item in data/wiki_data.json')
            continue
        result = entry_source(internal_id, level)
        if result is None:
            print(f'# {internal_id}: not usable by the solver (no supported damage type or item category)')
            continue
        entries.append(result)
        print(result[1])
    if '--insert' in args:
        print('added:', insert(entries))
