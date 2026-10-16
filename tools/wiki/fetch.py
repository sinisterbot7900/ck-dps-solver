"""Fetch pages and Lua data modules from the Core Keeper Fandom wiki through its MediaWiki API.

Fandom content is CC BY-SA. Keep request volume low: modules are fetched in one batched request,
and responses are cached under tools/wiki/cache/ so repeated runs don't hit the wiki.
"""
import json
import os
import re
import time
import urllib.parse
import urllib.request

API = 'https://core-keeper.fandom.com/api.php'
USER_AGENT = 'ck-dps-solver/0.2 (personal DPS calculator; https://github.com/sinisterbot7900/ck-dps-solver)'
CACHE_DIR = os.path.join(os.path.dirname(__file__), 'cache')

# Data modules the solver is built from
DATA_MODULES = [
    'Module:ObjectInfo/data',
    'Module:SetBonusInfo/data',
    'Module:ConditionInfo/data',
    'Module:SkillInfo/data',
    'Module:PetInfo/data',
    'Module:VersionInfo/data',
    'Module:Obtaining/data',
]


def _get(params):
    url = API + '?' + urllib.parse.urlencode({**params, 'format': 'json', 'formatversion': 2})
    request = urllib.request.Request(url, headers={'User-Agent': USER_AGENT})
    with urllib.request.urlopen(request, timeout=60) as response:
        return json.loads(response.read().decode('utf8'))


def _cache_path(title):
    return os.path.join(CACHE_DIR, re.sub(r'[^\w.-]+', '_', title) + '.json')


def fetch_pages(titles, use_cache=True):
    """Wikitext/Lua source of pages: {title: {'content', 'timestamp'}}. Missing pages map to None."""
    os.makedirs(CACHE_DIR, exist_ok=True)
    results, missing = {}, []
    for title in titles:
        path = _cache_path(title)
        if use_cache and os.path.exists(path):
            with open(path, encoding='utf8') as f:
                results[title] = json.load(f)
        else:
            missing.append(title)
    for i in range(0, len(missing), 10):  # the API allows up to 50 titles; stay well below
        batch = missing[i:i + 10]
        data = _get({'action': 'query', 'prop': 'revisions', 'rvprop': 'content|timestamp', 'rvslots': 'main', 'titles': '|'.join(batch)})
        normalized = {n['to']: n['from'] for n in data['query'].get('normalized', [])}
        for page in data['query']['pages']:
            title = normalized.get(page['title'], page['title'])
            if 'revisions' not in page:
                results[title] = None
                continue
            revision = page['revisions'][0]
            results[title] = {'content': revision['slots']['main']['content'], 'timestamp': revision['timestamp']}
            with open(_cache_path(title), 'w', encoding='utf8') as f:
                json.dump(results[title], f)
        time.sleep(1)
    return results


def latest_revision_timestamps(titles):
    """Revision timestamps only (cheap): used to check what changed since the last scan"""
    data = _get({'action': 'query', 'prop': 'revisions', 'rvprop': 'timestamp', 'titles': '|'.join(titles)})
    normalized = {n['to']: n['from'] for n in data['query'].get('normalized', [])}
    return {normalized.get(p['title'], p['title']): (p['revisions'][0]['timestamp'] if 'revisions' in p else None) for p in data['query']['pages']}


def module_game_version(content):
    """Game version a data module was generated from, from its first-line comment (e.g. '-- 1.2.0.7')"""
    match = re.match(r'\s*--\s*([\d.]+\S*)', content or '')
    return match.group(1) if match else None


def clear_cache():
    if os.path.isdir(CACHE_DIR):
        for name in os.listdir(CACHE_DIR):
            os.remove(os.path.join(CACHE_DIR, name))
