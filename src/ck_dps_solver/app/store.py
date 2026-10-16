"""The window's choices as one config dict (the format solver.run_search takes), with a signal when something
changes, so every widget showing a value (e.g. a setting on both the Search and Settings tabs) stays in sync."""
from PySide6.QtCore import QObject, Signal

from ck_dps_solver.app import state


class ConfigStore(QObject):
    changed = Signal(str) # Dotted path of the value that changed, e.g. 'settings.Fight length'

    def __init__(self):
        super().__init__()
        self.config = state.load_config()

    def get(self, path, default=None):
        node = self.config
        for key in path.split('.'):
            if not isinstance(node, dict) or key not in node:
                return default
            node = node[key]
        return node

    def set(self, path, value):
        keys = path.split('.')
        node = self.config
        for key in keys[:-1]:
            node = node.setdefault(key, {})
        if node.get(keys[-1]) != value:
            node[keys[-1]] = value
            self.changed.emit(path)

    def replace(self, config):
        """A whole new config (e.g. a preset): every widget refreshes"""
        self.config = config
        self.changed.emit('')

    def save(self):
        state.save_config(self.config)

    def search_config(self):
        """The config for solver.run_search (without the window-only keys), cleaned up: only known settings (typed
        like their defaults), only the window's damage types, ticked food used as is"""
        import copy
        from ck_dps_solver import defaults
        from ck_dps_solver.app.labels import DAMAGE_TYPES
        c = copy.deepcopy({k: v for k, v in self.config.items() if k not in ('save_folder', 'show_names', 'theme', 'consumables_owned_only', 'permanent_health_foods')})
        known = defaults.default_config()['settings']
        saved = c.get('settings', {})
        c['settings'] = {name: bool(saved.get(name, default)) if isinstance(default, bool) else float(saved.get(name, default))
                         for name, default in known.items()}
        c['skill_levels'] = {skill: int(level) for skill, level in c['skill_levels'].items()}
        c['perk_trees'] = {skill: [int(points) for points in tree] for skill, tree in c['perk_trees'].items()}
        consumables = c.get('consumables') or {}
        c['consumables'] = {dt: sorted(consumables.get(dt, defaults.CONSUMABLES[dt])) for dt in DAMAGE_TYPES}
        c['consumables_from_ticks'] = True # Biome runs use the ticked ones (picked for the progression), not their own picks
        c['fixed_items'] = {dt: list(c.get('fixed_items', {}).get(dt, [])) for dt in DAMAGE_TYPES}
        c.setdefault('dish_rarity', 'Rare')
        c.setdefault('golden_ingredients', True)
        c.pop('food_effects', None); c.pop('potion_effects', None)
        if c['save_filter'].get('enabled') and self.config.get('consumables_owned_only'):
            c['golden_ingredients'] = True # Food from your saves: the golden ingredients you have are usable
        return c
