"""The app's choices: loaded from and saved to gui_config.json and presets.json (in the repository, or the user folder
of a packaged app)."""
import json
import os

from ck_dps_solver import defaults, paths
from ck_dps_solver.app import theme

CONFIG_PATH = paths.user_file('gui_config.json')
PRESETS_PATH = paths.user_file('presets.json')


def load_config():
    """Defaults from defaults.py, overridden by the last saved choices"""
    config = defaults.default_config()
    if os.path.exists(CONFIG_PATH):
        with open(CONFIG_PATH, encoding='utf8') as f:
            saved = json.load(f)
        for key, value in saved.items():
            if isinstance(value, dict) and isinstance(config.get(key), dict):
                config[key].update(value)
            elif key in config or key in ('save_folder', 'show_names', 'theme', 'consumables_from_ticks', 'consumables_owned_only', 'permanent_health_foods', 'stats_by_mode'):
                config[key] = value
    if config.get('theme') not in [theme.DYNAMIC] + list(theme.THEMES): # None saved yet (or a removed theme): follow the damage type
        config['theme'] = theme.DYNAMIC
    return config


def save_config(config):
    with open(CONFIG_PATH, 'w', encoding='utf8') as f:
        json.dump(config, f, indent=1)


def load_presets():
    if os.path.exists(PRESETS_PATH):
        with open(PRESETS_PATH, encoding='utf8') as f:
            return json.load(f)
    return {}


def save_presets(presets):
    with open(PRESETS_PATH, 'w', encoding='utf8') as f:
        json.dump(presets, f, indent=1)
