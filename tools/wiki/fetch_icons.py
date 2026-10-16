"""Download the skill and talent icons from the Core Keeper Fandom wiki (CC BY-SA) into data/icons/.

Usage: python -m tools.wiki.fetch_icons [--force]

The skill navigation box on any skill page shows every skill's icon and every talent's icon, so one page lists them all.
Their URLs come from batched imageinfo queries; the files themselves come from the wiki's image CDN, a few at a time
with a pause between, and are only downloaded again with --force. data/icons/manifest.json maps each skill (in the
solver's naming) to its icon file and its talents' icon files in talent tree order.
"""
import json
import os
import re
import sys
import time
import urllib.request

from .fetch import USER_AGENT, _get

from tools import PACKAGE_DIR

ICON_DIR = os.path.join(PACKAGE_DIR, 'data', 'icons')
NAVBOX_PAGE = 'Melee combat' # Any skill page: its navbox has every skill and talent icon
# The wiki spells one talent both ways; its icon file uses the other spelling
SPELLINGS = {'Archaeologist': ['Archaeologist', 'Archeologist']}


def _key(name):
    return re.sub(r'[^a-z0-9]', '', name.lower())


def _skills():
    """[(skill, page title, [talent names in tree order])] in the solver's naming"""
    from ck_dps_solver.model.item_stats import wiki_data
    from ck_dps_solver.app.tabs.character import perk_names
    names = perk_names()
    return [(skill, wiki_data()['skills'][skill]['displayName'], names[skill]) for skill in names]


def _image_urls(files):
    """{file name: URL} from batched imageinfo queries (50 titles per request, the API's limit)"""
    urls = {}
    for i in range(0, len(files), 50):
        batch = files[i:i + 50]
        data = _get({'action': 'query', 'prop': 'imageinfo', 'iiprop': 'url', 'titles': '|'.join('File:' + f for f in batch)})
        for page in data['query']['pages']:
            info = page.get('imageinfo')
            if info:
                urls[page['title'][len('File:'):].replace(' ', '_')] = info[0]['url']
        time.sleep(1)
    return urls


def main(force=False):
    os.makedirs(ICON_DIR, exist_ok=True)
    images = _get({'action': 'parse', 'page': NAVBOX_PAGE, 'prop': 'images'})['parse']['images']
    by_key = {_key(os.path.splitext(f)[0]): f for f in images}
    manifest, wanted, missing = {}, {}, []
    def find(name):
        for spelling in SPELLINGS.get(name, [name]):
            if _key(spelling) in by_key:
                return by_key[_key(spelling)]
        return None
    for skill, title, talents in _skills():
        entry = {'name': title, 'icon': None, 'talents': []}
        for label, slot in [(title, 'icon')] + [(t, None) for t in talents]:
            file = find(label)
            local = f'{_key(label)}.png' if file else None
            if file:
                wanted[local] = file
            else:
                missing.append(f'{skill}: {label}')
            if slot == 'icon':
                entry['icon'] = local
            else:
                entry['talents'].append({'name': label, 'icon': local})
        manifest[skill] = entry
    todo = {local: file for local, file in wanted.items() if force or not os.path.exists(os.path.join(ICON_DIR, local))}
    urls = _image_urls(sorted(set(todo.values()))) if todo else {}
    for n, (local, file) in enumerate(sorted(todo.items())):
        url = urls.get(file)
        if url is None:
            missing.append(f'{file} (no URL)')
            continue
        request = urllib.request.Request(url, headers={'User-Agent': USER_AGENT})
        with urllib.request.urlopen(request, timeout=60) as response, open(os.path.join(ICON_DIR, local), 'wb') as f:
            f.write(response.read())
        if n % 10 == 9:
            time.sleep(1) # A pause every few files
    manifest = {'source': f'Core Keeper Fandom wiki (https://core-keeper.fandom.com), CC BY-SA; navbox of "{NAVBOX_PAGE}"', 'skills': manifest}
    with open(os.path.join(ICON_DIR, 'manifest.json'), 'w', encoding='utf8') as f:
        json.dump(manifest, f, indent=1)
    print(f'{len(todo)} icons downloaded ({len(wanted) - len(todo)} already there) into {ICON_DIR}')
    if missing:
        print('Not found:', ', '.join(missing))


if __name__ == '__main__':
    main(force='--force' in sys.argv)
