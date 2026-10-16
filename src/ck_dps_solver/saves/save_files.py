"""Find Core Keeper characters and worlds on this computer, with their in-game names."""
from dataclasses import dataclass
import glob
import json
import os

DEFAULT_ROOT = os.path.join(os.path.expanduser('~'), 'AppData', 'LocalLow', 'Pugstorm', 'Core Keeper', 'Steam')


@dataclass
class SaveFile:
    path: str
    name: str      # In-game name ('' if the file has none)
    kind: str      # 'character' or 'world'

    def label(self, show_names=True):
        """Text shown for this save: the in-game name (with the file name), or just the file name"""
        file_name = os.path.basename(self.path)
        if show_names and self.name:
            return f'{self.name}  ({file_name})'
        return file_name


def _decode_name(name):
    """Text of a save's fixed-size name field: {'utf8LengthInBytes': n, 'bytes': {... 'byte0000': ...}}"""
    flat = {}
    def walk(node):
        for key, value in node.items():
            if isinstance(value, dict): walk(value)
            else: flat[key] = value
    walk(name.get('bytes', {}))
    raw = bytes(flat.get(f'byte{i:04d}', 0) for i in range(name.get('utf8LengthInBytes', 0)))
    return raw.decode('utf8', errors='replace')


def _character_name(path):
    """Newer characters keep their name only in characterCustomizationNew; older ones in both"""
    with open(path, encoding='utf-8-sig') as f:
        save = json.load(f)
    for key in ('characterCustomizationNew', 'characterCustomization'):
        name = _decode_name(save.get(key, {}).get('name', {}))
        if name:
            return name
    return ''


def _world_name(world_path):
    """Name from worldinfos/<n>.worldinfo next to worlds/<n>.world.gzip"""
    index = os.path.basename(world_path).split('.')[0]
    info = os.path.join(os.path.dirname(os.path.dirname(world_path)), 'worldinfos', f'{index}.worldinfo')
    if not os.path.exists(info):
        return ''
    with open(info, encoding='utf-8-sig') as f:
        return json.load(f).get('name', '')


def save_folders(root=DEFAULT_ROOT):
    """Save folders (one per Steam account) under the Core Keeper data folder"""
    return sorted(p for p in glob.glob(os.path.join(root, '*')) if os.path.isdir(os.path.join(p, 'saves')) or os.path.isdir(os.path.join(p, 'worlds')))


def list_saves(folder):
    """(characters, worlds) in a save folder"""
    characters, worlds = [], []
    for path in sorted(glob.glob(os.path.join(folder, 'saves', '*.json')), key=_index):
        try:
            name = _character_name(path)
        except (OSError, ValueError, KeyError):
            name = ''
        characters.append(SaveFile(path, name, 'character'))
    for path in sorted(glob.glob(os.path.join(folder, 'worlds', '*.world.gzip')), key=_index):
        try:
            name = _world_name(path)
        except (OSError, ValueError):
            name = ''
        worlds.append(SaveFile(path, name, 'world'))
    return characters, worlds


def _index(path):
    head = os.path.basename(path).split('.')[0]
    return (0, int(head)) if head.isdigit() else (1, head)
