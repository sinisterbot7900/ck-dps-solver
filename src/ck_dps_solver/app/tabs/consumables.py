"""Consumables tab: food and potions as checkboxes, chosen separately for each damage type (the one at the top), with the
resulting totals. Changing the damage type, progression, dish options or the talents that make mining, fishing,
poison or thorns stats count ticks the strongest per effect.

Pick from: everything available up to your progression, or (owned items) only the food and potions in your saves:
your potions, your cooked dishes (exact, by their ingredients and rarity) and the dishes you can cook from ingredients
you have.

What to cook (the cooking planner, below): every dish your saves' ingredients make, ranked by the DPS it adds to the
loadout selected on the Search tab (model/cooking.py)."""
from PySide6.QtCore import Qt
from PySide6.QtGui import QBrush
from PySide6.QtWidgets import (QApplication, QButtonGroup, QGroupBox, QHBoxLayout, QHeaderView, QLabel, QPushButton, QSplitter, QTreeWidget,
                               QTreeWidgetItem, QVBoxLayout, QWidget)

from ck_dps_solver import defaults

from ck_dps_solver.engine import solver
from ck_dps_solver.engine.dominance import unused_attributes
from ck_dps_solver.model.character import ACTIVE_EFFECTS_DICT
from ck_dps_solver.model.consumables import DISH_RARITIES, combine as combine_consumables, format_effect, lookup, sources as consumable_sources
from ck_dps_solver.model.cooking import owned_ingredients, plan as plan_cooking
from ck_dps_solver.model.item_stats import wiki_data
from ck_dps_solver.model.progression import BIOME_NAMES
from ck_dps_solver.model.sources import sources as item_sources
from ck_dps_solver.saves.save_reader import owned_consumables

from ck_dps_solver.app import theme
from ck_dps_solver.app.widgets import bind
from ck_dps_solver.app.widgets.results import ResultsTable, expanded

KINDS = [('Potion', 'Potions'), ('Dish', 'Dishes (rare: x1.25; golden ingredients cooked with another golden: x1.44)'), ('Food', 'Eaten raw')]
OWNED_KINDS = [('Potion', 'Potions'), ('Dish', 'Dishes (yours, and ones you can cook from your ingredients)'), ('Food', 'Eaten raw')]
TALENT_SKILLS = ('Mining', 'Fishing', 'Gardening') # Talents that make mining, fishing, poison or thorns stats count
# Store values that decide which food and potions you own
OWNED_PATHS = ('save_filter', 'save_filter.enabled', 'save_filter.player_files', 'save_filter.world_files', 'save_filter.radius',
               'save_filter.center', 'consumables_owned_only')


class ConsumablesTab(QWidget):
    def __init__(self, store):
        super().__init__()
        self.store = store
        self.owned, self.owned_for = {}, None # {key: amount} from the saves, and the save choices it was read for
        self.items, self.pool = {}, None
        layout = QVBoxLayout(self)
        top = QHBoxLayout()
        top.addWidget(QLabel('Food and potions for'))
        self.type_label = QLabel()
        font = self.type_label.font(); font.setBold(True); self.type_label.setFont(font)
        top.addWidget(self.type_label)
        top.addSpacing(12)
        top.addWidget(QLabel('Dishes'))
        self.rarity_box = bind.combo(store, 'dish_rarity', list(DISH_RARITIES))
        top.addWidget(self.rarity_box)
        self.golden_box = bind.checkbox(store, 'golden_ingredients', 'Golden ingredients (Expert gardener; without them dishes are common)')
        top.addWidget(self.golden_box)
        reset = QPushButton('Defaults')
        reset.clicked.connect(self.reset)
        clear = QPushButton('Clear')
        clear.clicked.connect(lambda: self.set_keys(set()))
        top.addWidget(reset)
        top.addWidget(clear)
        top.addStretch()
        # Pick from everything available, or only what your saves hold (owned items only)
        self.pick_from = QWidget()
        pick = QHBoxLayout(self.pick_from)
        pick.setContentsMargins(0, 0, 0, 0)
        pick.setSpacing(0)
        pick.addWidget(QLabel('Pick from'))
        pick.addSpacing(8)
        self.pick_all, self.pick_owned = QPushButton('Everything available'), QPushButton('What I own')
        self.pick_owned.setToolTip('Only the food and potions in the selected characters and the chests of the selected worlds, '
                                   'and the dishes you can cook from the ingredients there')
        group = QButtonGroup(self)
        for button, side in ((self.pick_all, 'left'), (self.pick_owned, 'right')):
            button.setCheckable(True)
            button.setProperty('segment', side)
            group.addButton(button)
            pick.addWidget(button)
        self.pick_owned.toggled.connect(lambda on: store.set('consumables_owned_only', bool(on)))
        top.addWidget(self.pick_from)
        layout.addLayout(top)
        help_text = QLabel('Used when "Consumables active" is on. The same effect from two sources only counts once (the strongest). '
                           'Changing the damage type or progression ticks the strongest per effect (Defaults does too).')
        help_text.setProperty('muted', True)
        help_text.setWordWrap(True)
        layout.addWidget(help_text)

        self.choices = QTreeWidget()
        self.choices.setHeaderHidden(True)
        self.choices.setUniformRowHeights(True)
        self.choices.itemChanged.connect(self.item_changed)

        # Totals (not editable)
        totals_box = QGroupBox('Totals')
        totals_layout = QVBoxLayout(totals_box)
        self.totals = QTreeWidget()
        self.totals.setHeaderLabels(['Stat', 'Total', 'From'])
        self.totals.setRootIsDecorated(False)
        self.totals.setColumnWidth(0, 230)
        self.totals.setColumnWidth(1, 80)
        self.totals.header().setSectionResizeMode(2, QHeaderView.Stretch)
        totals_layout.addWidget(self.totals)
        splitter = QSplitter()
        splitter.addWidget(self.choices)
        splitter.addWidget(totals_box)
        splitter.setSizes([640, 640])
        self.planner = CookingPlanner(store)
        rows = QSplitter(Qt.Vertical)
        rows.addWidget(splitter)
        rows.addWidget(self.planner)
        rows.setSizes([520, 300])
        layout.addWidget(rows, 1)

        self.talents = self.talent_snapshot()
        store.changed.connect(self.on_changed)
        self.update_pick_from()
        self.read_owned()
        self.show_choices()

    # ------------------------------------------------------------ what you own

    def owned_mode(self):
        """Only food and potions from the saves: owned items searched, and "What I own" chosen"""
        return bool(self.store.get('save_filter.enabled')) and bool(self.store.get('consumables_owned_only'))

    def golden(self):
        """Golden ingredients usable: the setting, or with "What I own", the golden ingredients you have"""
        return True if self.owned_mode() else bool(self.store.get('golden_ingredients', True))

    def update_pick_from(self):
        self.pick_from.setVisible(bool(self.store.get('save_filter.enabled'))) # Only with saves to read
        self.golden_box.setVisible(not self.owned_mode()) # Owned: the golden ingredients you have count
        owned = bool(self.store.get('consumables_owned_only'))
        for button, checked in ((self.pick_owned, owned), (self.pick_all, not owned)):
            button.blockSignals(True); button.setChecked(checked); button.blockSignals(False)

    def read_owned(self):
        """Read the saves' food and potions (again only when the save choices changed)"""
        if not self.owned_mode():
            return
        f = self.store.get('save_filter') or {}
        center = tuple(f['center']) if f.get('center') and len(f['center']) == 2 else None
        wanted = (tuple(f.get('player_files') or []), tuple(f.get('world_files') or []), center, f.get('radius'))
        if wanted == self.owned_for:
            return
        try:
            self.owned = owned_consumables(wanted[0], wanted[1], center=center, radius=wanted[3])
        except (OSError, ValueError, KeyError):
            self.owned = {}
        self.owned_for = wanted

    def pool_signature(self):
        return ('owned', tuple(sorted(self.owned))) if self.owned_mode() else ('all',)

    # ------------------------------------------------------------ what triggers the auto-pick

    def talent_snapshot(self):
        return {skill: list(self.store.get(f'perk_trees.{skill}') or []) for skill in TALENT_SKILLS}

    def on_changed(self, path):
        if path in OWNED_PATHS:
            self.update_pick_from()
            self.read_owned()
            if self.pool_signature() != self.pool: # The list shown is for another pool: pick from the new one
                self.reset()
        elif path in ('damage_type', 'biomes', 'dish_rarity', 'golden_ingredients'):
            self.reset()
        elif path.startswith('perk_trees'):
            talents = self.talent_snapshot()
            if talents != self.talents:
                self.talents = talents
                self.reset()
        elif path in ('', 'consumables') or path.startswith('consumables.'):
            if path == '':
                self.update_pick_from()
                self.read_owned()
            self.talents = self.talent_snapshot()
            self.show_choices()

    # ------------------------------------------------------------ choices

    def damage_type(self):
        return self.store.get('damage_type')

    def chosen(self):
        saved = self.store.get(f'consumables.{self.damage_type()}')
        return set(saved if saved is not None else defaults.CONSUMABLES.get(self.damage_type(), []))

    def set_keys(self, keys):
        self.store.set(f'consumables.{self.damage_type()}', sorted(keys))
        self.show_choices()

    def reset(self):
        """Tick the best food and potions for the damage type, progression and talents (owned: from what you have)"""
        self.set_keys(solver.best_consumables(self.damage_type(), self.store.get('skill_levels'), self.store.get('perk_trees'), self.store.get('biomes'),
                                                  self.store.get('dish_rarity', 'Rare'), self.golden(),
                                                  only=list(self.owned) if self.owned_mode() else None))

    def item_changed(self, item, column):
        key = item.data(0, Qt.UserRole)
        if key is None:
            return
        keys = self.chosen()
        if item.checkState(0) == Qt.Checked:
            keys.add(key)
        else:
            keys.discard(key)
        self.store.set(f'consumables.{self.damage_type()}', sorted(keys))
        self.show_totals()

    def build_list(self):
        """The checkboxes for the pool: every source (by biome tier), or the ones you own"""
        signature = self.pool_signature()
        if signature == self.pool:
            return
        self.pool = signature
        self.choices.blockSignals(True)
        self.choices.clear()
        self.items = {}
        if self.owned_mode():
            pool = {key: lookup(key) for key in self.owned}
            pool = {key: source for key, source in pool.items() if source is not None}
            order = lambda kv: kv[1].name
            kinds = OWNED_KINDS
        else:
            pool = consumable_sources()
            tier = lambda source: BIOME_NAMES.index(source.biome) if source.biome in BIOME_NAMES else len(BIOME_NAMES)
            order = lambda kv: (tier(kv[1]), kv[1].name)
            kinds = KINDS
        for kind, title in kinds:
            entries = sorted(((k, s) for k, s in pool.items() if s.kind == kind), key=order)
            if not entries:
                continue
            group = QTreeWidgetItem(self.choices, [title])
            group.setFlags(Qt.ItemIsEnabled)
            bold = group.font(0); bold.setBold(True); group.setFont(0, bold)
            for key, source in entries:
                item = QTreeWidgetItem(group, [source.name])
                item.setData(0, Qt.UserRole, key)
                self.items[key] = item
        if not self.items:
            empty = QTreeWidgetItem(self.choices, ['No food or potions the solver uses in the selected saves' if self.owned_mode() else 'No food or potions'])
            empty.setFlags(Qt.ItemIsEnabled)
        self.choices.expandAll()
        self.choices.blockSignals(False)

    def show_choices(self):
        self.build_list()
        damage_type = self.damage_type()
        self.type_label.setText(damage_type)
        chosen = self.chosen()
        golden = self.golden()
        self.rarity_box.setEnabled(golden)
        rarity = self.store.get('dish_rarity', 'Rare')
        all_sources = consumable_sources()
        biomes = self.store.get('biomes')
        owned_mode = self.owned_mode()
        muted = QBrush(theme.color('text_muted'))
        self.choices.blockSignals(True)
        for key, item in self.items.items():
            item.setCheckState(0, Qt.Checked if key in chosen else Qt.Unchecked)
            source = lookup(key, rarity, golden)
            if source is None: # A golden ingredient, with golden ingredients off
                item.setText(0, f'[{all_sources[key].biome or "?"}] {all_sources[key].name}: needs golden ingredients')
                enabled = False
            elif owned_mode:
                amount = self.owned.get(key, 0)
                have = f'cook from {amount} owned' if key.startswith('dish:') else f'x{amount}'
                item.setText(0, f'{source.name} ({have}): {source.describe()}')
                enabled = True
            else:
                later = biomes is not None and source.biome is not None and source.biome not in biomes
                item.setText(0, f'[{source.biome or "?"}] {source.name}: {source.describe()}' + (' (later biome)' if later else ''))
                enabled = not later
            item.setFlags(Qt.ItemIsUserCheckable | Qt.ItemIsEnabled if enabled else Qt.ItemIsUserCheckable)
            item.setForeground(0, QBrush() if enabled else muted)
        self.choices.blockSignals(False)
        self.show_totals()

    def show_totals(self):
        self.totals.clear()
        damage_type = self.damage_type()
        _, rows = combine_consumables(sorted(self.chosen()), self.store.get('dish_rarity', 'Rare'), self.golden())
        unused = set(unused_attributes(damage_type))
        muted = QBrush(theme.color('text_muted'))
        by_stat = {}
        for attribute, name, value, counted, note in rows:
            by_stat.setdefault(attribute, []).append((name, value, counted, note))
        for attribute in [a for a in ACTIVE_EFFECTS_DICT if a in by_stat]:
            entries = by_stat[attribute]
            total = sum(value for _, value, counted, _ in entries if counted)
            sources = ', '.join(f'{name} {format_effect(attribute, value).split(" ")[0]}' for name, value, counted, _ in entries if counted)
            label = attribute + (f' (not used by {damage_type.lower()})' if attribute in unused else '')
            shown = f'{total * 100:.3g}%' if attribute.startswith('%_') else f'{total:g}'
            row = QTreeWidgetItem(self.totals, [label, shown, sources])
            row.setTextAlignment(1, Qt.AlignRight | Qt.AlignVCenter)
            if attribute in unused:
                for column in range(3): row.setForeground(column, muted)
            for name, value, counted, note in entries:
                if not counted:
                    skipped = QTreeWidgetItem(self.totals, ['', '', f'  not counted: {name} ({note})'])
                    skipped.setForeground(2, muted)

    def apply_theme(self):
        self.show_choices()


PLAN_COLUMNS = ['Gain %', 'Dish', 'Alone %', 'DPS', 'Gain', 'Can cook', 'Effects', 'Ingredients']


class CookingPlanner(QGroupBox):
    """What to cook: the dishes your ingredients make, ranked by the DPS they add to a search loadout"""
    def __init__(self, store):
        super().__init__('What to cook')
        self.store = store
        self.search = None
        self.loadout, self.info = None, None # The loadout selected on the Search tab (else the best is used)
        self.rows = []
        layout = QVBoxLayout(self)
        top = QHBoxLayout()
        self.plan_button = QPushButton('Plan')
        self.plan_button.setToolTip('Score every dish the ingredients in your saves make (the saves chosen on the Items tab)')
        self.plan_button.clicked.connect(self.run)
        top.addWidget(self.plan_button)
        self.status = QLabel()
        self.status.setProperty('muted', True)
        self.status.setWordWrap(True)
        top.addWidget(self.status, 1)
        layout.addLayout(top)
        self.table = ResultsTable(PLAN_COLUMNS, {'Dish': 330, 'Alone %': 70, 'Can cook': 70, 'Effects': 480, 'Ingredients': 330})
        self.table.source.tooltip = self.tooltip
        layout.addWidget(self.table, 1)
        self.table.setVisible(False)
        store.changed.connect(lambda path: self.show_status() if path == '' or path.startswith('save_filter') else None)
        self.show_status()

    def use_search(self, search):
        self.search = search
        search.loadout_selected.connect(self.loadout_changed)

    def loadout_changed(self, loadout, info):
        self.loadout, self.info = loadout, info
        self.show_status()

    def has_saves(self):
        return bool(self.store.get('save_filter.enabled')) and bool(self.store.get('save_filter.player_files'))

    def target(self):
        """(loadout, run info) to score on: the selected one, else the latest search's best"""
        info = self.search.info if self.search is not None else None
        if info is None or not info.get('best_loadouts'):
            return None, None
        if self.info is info and self.loadout is not None:
            return self.loadout, info
        return info['best_loadouts'][0], info

    def describe_target(self):
        loadout, info = self.target()
        if not self.has_saves():
            return 'Turn on "Only items I own" on the Items tab and choose a character: the ingredients come from your saves.'
        if loadout is None:
            return 'Run a search first: dishes are scored on the loadout selected on the Search tab (or the best one).'
        self.status.setToolTip('Gain %: the dish added to the food and potions that search used (the same effect only counts once). '
                               'Alone %: the dish with no other food or potions. Food always counts here, whatever "Consumables active" says.')
        return (f"Scored on {info.get('damage_type') or loadout[1].damage_type}: {solver.display_name(loadout[1])} ({loadout[0]:,} DPS). "
                "Gain %: on top of that search's food. Alone %: no other food.")

    def show_status(self, extra=''):
        self.status.setText(self.describe_target() + extra)

    def ingredients(self):
        f = self.store.get('save_filter') or {}
        center = tuple(f['center']) if f.get('center') and len(f['center']) == 2 else None
        return owned_ingredients(owned_consumables(tuple(f.get('player_files') or []), tuple(f.get('world_files') or []),
                                                   center=center, radius=f.get('radius')))

    def run(self):
        loadout, info = self.target()
        if loadout is None or not self.has_saves():
            self.show_status()
            return
        QApplication.setOverrideCursor(Qt.WaitCursor)
        try:
            ingredients = self.ingredients()
            items = solver.loadout_items(loadout, info['fixed_items'])
            self.rows, _ = plan_cooking(ingredients, items, info['character_kwargs'], info.get('consumable_keys') or [], solver.loadout_dps)
        except (OSError, ValueError, KeyError) as error:
            self.rows, ingredients = [], None
            self.status.setText(f"Couldn't read the ingredients from your saves: {error}")
        finally:
            QApplication.restoreOverrideCursor()
        if ingredients is None:
            return
        self.table.set_rows([(i, [row[c] for c in PLAN_COLUMNS]) for i, row in enumerate(self.rows)])
        self.table.sortByColumn(0, Qt.DescendingOrder)
        self.table.setVisible(bool(self.rows))
        if not ingredients:
            self.status.setText('No cooking ingredients in the selected characters or the chests of the selected worlds.')
        elif not self.rows:
            self.status.setText('None of your ingredients make a dish with an effect the solver uses.')
        else:
            self.show_status(f'  {len(ingredients)} ingredients, {len(self.rows)} dishes.')

    def tooltip(self, row_id, column):
        row = self.rows[row_id]
        if column == 'Ingredients':
            records = wiki_data().get('consumables', {})
            return expanded(' || '.join(f"{records[i]['name']}: {'; '.join(item_sources(i))}" for i in row['ingredient_ids']))
        if column == 'Gain %':
            return f"+{row['Gain']:,} DPS on top of the search's food and potions"
        value = row.get(column)
        return expanded(value) if column in ('Dish', 'Effects') and value else None
