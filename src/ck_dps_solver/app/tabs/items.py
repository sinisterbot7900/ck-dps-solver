"""Items tab: which items to search (every item or owned ones from save files), the progression limit, and the lantern,
bag and pet always equipped."""
import copy
import os

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (QAbstractItemView, QButtonGroup, QComboBox, QFileDialog, QFrame, QGridLayout, QGroupBox, QHBoxLayout, QLabel,
                               QLineEdit, QListWidget, QPushButton, QRadioButton, QSizePolicy, QStackedWidget, QVBoxLayout, QWidget)

from ck_dps_solver import defaults
from ck_dps_solver.catalogue import BAGS, LANTERNS, PETS
from ck_dps_solver.model.progression import BIOME_NAMES, BIOMES, biomes_up_to, progression_from_save
from ck_dps_solver.saves.save_files import DEFAULT_ROOT, list_saves, save_folders
from ck_dps_solver.saves.save_reader import permanent_health_eaten, permanent_health_foods, read_character_stats, soul_settings

from ck_dps_solver.app import labels
from ck_dps_solver.app.widgets import bind
from ck_dps_solver.app.widgets.collapse import Collapsible

ALL_BIOMES = 'All biomes (endgame, no progression limit)'
BIOME_LABELS = [ALL_BIOMES] + [f"{name} ({', '.join(bosses)})" if bosses else name for name, _, bosses in BIOMES]
LEVELS = {'actual': 'Actual (from save)', 'max': 'Max (20)'}
FIXED_CATEGORIES = [('Lantern', LANTERNS), ('Bag', BAGS), ('Pet', PETS)]
BEST = 'Best'
BEST_HELP = {category: f'The best {category.lower()} for your progression (or of the ones you own), picked by a quick search first'
             for category in ('Lantern', 'Bag', 'Pet')}
SEARCH_KEYS = {'Lantern': 'search_lanterns', 'Bag': 'search_bags', 'Pet': 'search_pets'}
TRY_ALL_NOTE = {'Lantern': 'Tries every lantern', 'Bag': 'Tries every bag', 'Pet': 'Tries every pet'} # Details: TRY_ALL_HELP (hover)
TRY_ALL_HELP = {
    'Lantern': 'Tries every lantern, and no lantern (owned items: the lanterns you own).',
    'Bag': 'Tries every bag, and no bag (owned items: the bags you own).',
    'Pet': 'Tries every pet (owned items: the pets you own, with their talents from the save).',
}


def biome_label(biomes):
    """The progression dropdown's label for a config's biomes (None = every biome)"""
    if not biomes:
        return ALL_BIOMES
    known = [BIOME_NAMES.index(b) for b in biomes if b in BIOME_NAMES] # Names from older versions may be gone (e.g. 'Starting gear')
    return BIOME_LABELS[1 + (max(known) if known else 0)]


def biomes_for(label):
    return None if label == ALL_BIOMES else biomes_up_to(BIOME_NAMES[BIOME_LABELS.index(label) - 1])


def _same(a, b):
    return os.path.normcase(os.path.abspath(a)) == os.path.normcase(os.path.abspath(b))


# Character stats each search mode keeps its own copy of (ItemsTab.mode_changed)
MODE_STATS = ('skill_levels', 'perk_trees', 'settings.Permanent max health', 'permanent_health_foods')

class ItemsTab(QWidget):
    def __init__(self, store, log):
        super().__init__()
        self.store, self.log = store, log
        self.saves = ([], [])
        layout = QVBoxLayout(self)

        # Every item or owned items
        mode = QGroupBox('Items to search')
        mode_layout = QVBoxLayout(mode)
        self.every = QRadioButton('Every item (level 20)')
        self.owned = QRadioButton('Only items I own (from save files, at their actual levels)')
        group = QButtonGroup(self)
        for button in (self.every, self.owned):
            group.addButton(button)
            mode_layout.addWidget(button)
        self.owned.toggled.connect(lambda on: store.set('save_filter.enabled', bool(on)))
        layout.addWidget(mode)

        # Progression
        progression = QGroupBox('Progression')
        row = QHBoxLayout(progression)
        row.addWidget(QLabel('Up to'))
        self.biome_box = QComboBox()
        self.biome_box.addItems(BIOME_LABELS)
        self.biome_box.setMinimumWidth(460)
        self.biome_box.currentTextChanged.connect(lambda label: store.set('biomes', biomes_for(label)))
        row.addWidget(self.biome_box)
        note = QLabel("Items from this biome and every one before it. Items only a boss gives count from the next biome (once it's beaten).")
        note.setProperty('muted', True)
        note.setWordWrap(True)
        row.addWidget(note, 1)
        layout.addWidget(progression)

        # Save files
        self.save_section = QGroupBox('Save files')
        saves = QVBoxLayout(self.save_section)
        top = QHBoxLayout()
        top.addWidget(QLabel('Save folder'))
        self.folder_box = QComboBox()
        self.folder_box.setEditable(True)
        self.folder_box.addItems(save_folders())
        self.folder_box.setMinimumWidth(520)
        self.folder_box.currentTextChanged.connect(self.folder_changed)
        top.addWidget(self.folder_box, 1)
        browse = QPushButton('Browse...')
        browse.clicked.connect(self.browse_folder)
        top.addWidget(browse)
        saves.addLayout(top)

        lists = QHBoxLayout()
        self.character_list = self._list(lists, 'Characters (equipped and inventory items)')
        self.world_list = self._list(lists, 'Worlds (items in chests near your character)')
        saves.addLayout(lists, 1)

        load_row = QHBoxLayout()
        load = QPushButton('Load')
        load.setProperty('accent', True)
        load.clicked.connect(self.load_save)
        load_row.addWidget(load)
        self.load_status = QLabel('')
        load_row.addWidget(self.load_status)
        hint = QLabel("Loads the first selected character's skills, talents, progression and permanent max health")
        hint.setProperty('muted', True)
        load_row.addWidget(hint)
        load_row.addStretch()
        self.advanced_button = QPushButton('Advanced settings')
        self.advanced_button.setCheckable(True)
        self.advanced_button.setProperty('toggle', True)
        self.advanced_button.setToolTip('Chest radius, reinforcement, item level, character stats and upgrade suggestions')
        self.advanced_button.toggled.connect(self.show_advanced)
        load_row.addWidget(self.advanced_button)
        saves.addLayout(load_row)

        self.advanced = QWidget()
        options = QGridLayout(self.advanced)
        options.setContentsMargins(0, 4, 0, 0)
        options.addWidget(QLabel('Chest radius (tiles, blank = whole world)'), 0, 0)
        self.radius = QLineEdit()
        self.radius.setFixedWidth(80)
        self.radius.textChanged.connect(self.radius_changed)
        options.addWidget(self.radius, 0, 1)
        options.addWidget(QLabel('Center x, z (blank = your character)'), 0, 2)
        self.center = QLineEdit()
        self.center.setFixedWidth(120)
        self.center.textChanged.connect(self.center_changed)
        options.addWidget(self.center, 0, 3)
        options.addWidget(QLabel('Reinforcement'), 0, 4)
        options.addWidget(bind.combo(store, 'save_filter.reinforcement', ['assume', 'detected']), 0, 5)
        options.addWidget(QLabel('Item level'), 0, 6)
        self.level_box = QComboBox()
        self.level_box.addItems(list(LEVELS.values()))
        self.level_box.currentTextChanged.connect(lambda text: store.set('save_filter.level', 'max' if text.startswith('Max') else 'actual'))
        options.addWidget(self.level_box, 0, 7)
        options.addWidget(bind.checkbox(store, 'save_filter.character_stats', 'Use skills and talents from the character (first one selected)'), 1, 0, 1, 6)
        options.addWidget(bind.checkbox(store, 'suggest_upgrades',
                                        "Suggest upgrades: items from the chosen progression you don't own, ranked by DPS gain, with where to get them"), 2, 0, 1, 8)
        options.setColumnStretch(8, 1)
        saves.addWidget(self.advanced)
        self.advanced_slide = Collapsible(self.advanced, self)
        self.show_advanced(False)
        layout.addWidget(self.save_section, 1)
        self.save_slide = Collapsible(self.save_section, self)

        # Always equipped: per category, choose one or try all (the choice of trying all applies to every damage type)
        fixed = QGroupBox('Always equipped')
        self.fixed_group = fixed
        cards = QHBoxLayout(fixed)
        self.fixed_boxes, self.try_all, self.fixed_stacks = {}, {}, {}
        for category, options_ in FIXED_CATEGORIES:
            card = QFrame()
            card.setObjectName('Card')
            column = QVBoxLayout(card)
            header = QHBoxLayout()
            title = QLabel(category)
            font = title.font(); font.setBold(True); title.setFont(font)
            header.addWidget(title)
            header.addStretch()
            choose, every = QPushButton('Choose'), QPushButton('Try all')
            group = QButtonGroup(self)
            for i, button in enumerate((choose, every)):
                button.setCheckable(True)
                button.setProperty('segment', 'left' if i == 0 else 'right')
                group.addButton(button)
                header.addWidget(button)
            header.setSpacing(0)
            every.setToolTip(TRY_ALL_HELP[category])
            key = SEARCH_KEYS[category]
            every.toggled.connect(lambda on, k=key: store.set(k, bool(on)))
            self.try_all[category] = (choose, every)
            column.addLayout(header)
            stack = QStackedWidget()
            boxes = QWidget()
            boxes_layout = QVBoxLayout(boxes)
            boxes_layout.setContentsMargins(0, 0, 0, 0)
            for damage_type in labels.DAMAGE_TYPES:
                box = QComboBox()
                box.addItems([BEST, 'None'] + list(options_))
                box.setItemData(0, BEST_HELP[category], Qt.ToolTipRole)
                box.currentTextChanged.connect(lambda _, dt=damage_type: self.fixed_changed(dt))
                self.fixed_boxes[(damage_type, category)] = box
                boxes_layout.addWidget(box)
            boxes_layout.addStretch()
            stack.addWidget(boxes)
            note = QLabel(TRY_ALL_NOTE[category]) # One line, so both states are the same height
            note.setProperty('muted', True)
            note.setToolTip(TRY_ALL_HELP[category])
            stack.addWidget(note)
            self.fixed_stacks[category] = stack
            stack.setFixedHeight(max(box.sizeHint().height(), note.sizeHint().height())) # Same height for Choose and Try all
            column.addWidget(stack)
            cards.addWidget(card, 1, Qt.AlignTop)
        fixed.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Maximum)
        layout.addWidget(fixed)
        layout.addStretch() # Keeps the boxes at the top when the save section is hidden

        store.changed.connect(self.refresh)
        self.using_save = bool(store.get('save_filter.enabled'))
        store.changed.connect(self.mode_changed)
        if not self.using_save: # Every item: the defaults, also when the app starts this way (e.g. after the defaults changed)
            self.apply_default_stats()
        self.folder_box.setCurrentText(store.get('save_folder') or (self.folder_box.itemText(0) if self.folder_box.count() else ''))
        self.refresh('')

    def _list(self, parent, title):
        box = QGroupBox(title)
        inner = QVBoxLayout(box)
        widget = QListWidget()
        widget.setSelectionMode(QAbstractItemView.ExtendedSelection)
        widget.itemSelectionChanged.connect(self.selection_changed)
        inner.addWidget(widget)
        parent.addWidget(box, 1)
        return widget

    # ------------------------------------------------------------ store -> widgets

    def refresh(self, path=''):
        """Show the store's values (path: what changed; '' = everything, e.g. a preset)"""
        def quietly(widget, apply):
            widget.blockSignals(True); apply(); widget.blockSignals(False)
        save_filter = self.store.get('save_filter') or {}
        if path in ('', 'save_filter', 'save_filter.enabled'):
            enabled = bool(save_filter.get('enabled'))
            quietly(self.owned, lambda: self.owned.setChecked(enabled))
            quietly(self.every, lambda: self.every.setChecked(not enabled))
            self.show_save_section(enabled, animate=path != '') # Save files only matter when searching owned items
        if path in ('', 'biomes'):
            label = biome_label(self.store.get('biomes'))
            quietly(self.biome_box, lambda: self.biome_box.setCurrentText(label))
            if self.store.get('biomes') != biomes_for(label): # Older configs' names (e.g. 'Starting gear'), as the dropdown means them
                self.store.set('biomes', biomes_for(label))
        if path in ('', 'save_filter', 'save_filter.level'):
            quietly(self.level_box, lambda: self.level_box.setCurrentText(LEVELS[save_filter.get('level', 'actual')]))
        if path in ('', 'save_filter', 'save_filter.radius'):
            radius = save_filter.get('radius')
            if self._number(self.radius.text()) != radius:
                quietly(self.radius, lambda: self.radius.setText('' if radius is None else f'{radius:g}'))
        if path in ('', 'save_filter', 'save_filter.center'):
            center = save_filter.get('center')
            if self._numbers(self.center.text()) != center and (center is None or len(center) == 2):
                quietly(self.center, lambda: self.center.setText('' if center is None else f'{center[0]:g}, {center[1]:g}'))
        if path in ('', 'save_folder'):
            folder = self.store.get('save_folder') or ''
            if folder and self.folder_box.currentText() != folder:
                quietly(self.folder_box, lambda: self.folder_box.setCurrentText(folder))
                self.refresh_saves()
        if path == '':
            self.refresh_saves() # Also selects the store's save files
        elif path in ('save_filter', 'save_filter.player_files', 'save_filter.world_files'):
            self.select_saved()
        if path in ('', 'fixed_items', 'best_fixed'):
            fixed = self.store.get('fixed_items') or {}
            best = self.store.get('best_fixed') or {}
            for (damage_type, category), box in self.fixed_boxes.items():
                options = dict(FIXED_CATEGORIES)[category]
                name = BEST if category in best.get(damage_type, []) else next((n for n in fixed.get(damage_type, []) if n in options), 'None')
                quietly(box, lambda b=box, n=name: b.setCurrentText(n))
        if path in ('', 'damage_type', 'search_lanterns', 'search_bags', 'search_pets'):
            damage_type = self.store.get('damage_type')
            self.fixed_group.setTitle(f'Always equipped for {damage_type}')
            for (box_type, _), box in self.fixed_boxes.items():
                box.setVisible(box_type == damage_type) # Only the Search tab's damage type
            for category, (choose, every) in self.try_all.items():
                on = bool(self.store.get(SEARCH_KEYS[category]))
                quietly(every, lambda b=every, v=on: b.setChecked(v))
                quietly(choose, lambda b=choose, v=on: b.setChecked(not v))
                self.fixed_stacks[category].setCurrentIndex(1 if on else 0)

    # ------------------------------------------------------------ widgets -> store

    @staticmethod
    def _number(text):
        try:
            return float(text) if text.strip() else None
        except ValueError:
            return None

    @staticmethod
    def _numbers(text):
        """'x, z' -> [x, z]; blank -> None; anything else -> [] (the Run button refuses it)"""
        if not text.strip():
            return None
        try:
            return [float(v) for v in text.replace(',', ' ').split()]
        except ValueError:
            return []

    def radius_changed(self, text):
        self.store.set('save_filter.radius', self._number(text))

    def center_changed(self, text):
        self.store.set('save_filter.center', self._numbers(text))

    def show_save_section(self, show, animate=True):
        """Show or hide the save files section; animated, it slides open or closed"""
        self.save_slide.set_open(show, animate)

    def show_advanced(self, on):
        self.advanced_slide.set_open(on)
        self.advanced_button.setText('Hide advanced settings' if on else 'Advanced settings')

    def fixed_changed(self, damage_type):
        chosen = {category: self.fixed_boxes[(damage_type, category)].currentText() for category, _ in FIXED_CATEGORIES}
        fixed = dict(self.store.get('fixed_items') or {})
        fixed[damage_type] = [name for name in chosen.values() if name not in ('None', BEST)]
        best = dict(self.store.get('best_fixed') or {})
        best[damage_type] = [category for category, name in chosen.items() if name == BEST]
        self.store.set('best_fixed', best)
        self.store.set('fixed_items', fixed)

    # ------------------------------------------------------------ saves

    def folder_changed(self, folder):
        self.store.set('save_folder', folder)
        self.refresh_saves()

    def browse_folder(self):
        folder = QFileDialog.getExistingDirectory(self, 'Core Keeper save folder (contains saves/ and worlds/)', self.folder_box.currentText() or DEFAULT_ROOT)
        if folder:
            self.folder_box.setCurrentText(os.path.normpath(folder))

    def refresh_saves(self):
        folder = self.folder_box.currentText()
        self.saves = list_saves(folder) if folder and os.path.isdir(folder) else ([], [])
        for widget, files in ((self.character_list, self.saves[0]), (self.world_list, self.saves[1])):
            widget.blockSignals(True)
            widget.clear()
            widget.addItems([save.label(True) for save in files]) # In-game name, file name in parentheses
            widget.blockSignals(False)
        self.select_saved()

    def select_saved(self):
        """Select the store's save files in the lists"""
        for widget, files, key in ((self.character_list, self.saves[0], 'player_files'), (self.world_list, self.saves[1], 'world_files')):
            chosen = self.store.get(f'save_filter.{key}') or []
            widget.blockSignals(True)
            for i, save in enumerate(files):
                widget.item(i).setSelected(any(_same(save.path, path) for path in chosen))
            widget.blockSignals(False)

    def selected_paths(self, widget, files):
        return [files[i].path for i in sorted(index.row() for index in widget.selectedIndexes()) if i < len(files)]

    def selection_changed(self):
        self.store.set('save_filter.player_files', self.selected_paths(self.character_list, self.saves[0]))
        self.store.set('save_filter.world_files', self.selected_paths(self.world_list, self.saves[1]))
        self.set_load_status('') # The selection no longer matches what was loaded

    def set_load_status(self, text, good=True):
        self.load_status.setText(text)
        self.load_status.setProperty('status', 'good' if good else 'bad')
        self.load_status.style().unpolish(self.load_status)
        self.load_status.style().polish(self.load_status)

    def mode_changed(self, path):
        """Character stats (skills, talents, permanent foods) follow the search mode. Every item: the defaults (level 100,
        the damage type's best talents for the mana strategy, all permanent foods). Your own items: the selected
        character's, read from its save (without a character selected, the ones you had there)."""
        using = bool(self.store.get('save_filter.enabled'))
        if path != 'save_filter.enabled' or using == self.using_save:
            self.using_save = using # A preset or a reload: take it as it is
            return
        self.using_save = using
        if not using:
            self.store.set('stats_by_mode.owned', {key: copy.deepcopy(self.store.get(key)) for key in MODE_STATS})
            self.apply_default_stats()
        elif self.selected_paths(self.character_list, self.saves[0]):
            self.load_save() # Your character's stats, from its save
        else:
            for key, value in (self.store.get('stats_by_mode.owned') or {}).items():
                self.store.set(key, copy.deepcopy(value))

    def apply_default_stats(self):
        """Every item: default skills and talents, all permanent foods"""
        self.store.set('skill_levels', dict(defaults.skill_levels))
        self.store.set('perk_trees', defaults.perk_trees_for(self.store.get('damage_type'), bool(self.store.get('settings.Burst at full mana', True))))
        foods = permanent_health_foods()
        self.store.set('permanent_health_foods', sorted(code for code, _, _ in foods))
        self.store.set('settings.Permanent max health', float(sum(value for _, _, value in foods)))
        self.log('Every item: default skills and talents (level 100, the best talents for the damage type and mana strategy) '
                 'and all permanent foods')

    def load_save(self):
        """Load button: the first selected character's skills and talents, progression and permanent max health"""
        paths = self.selected_paths(self.character_list, self.saves[0])
        if not paths:
            self.set_load_status('Pick a character first', good=False)
            return
        path = paths[0]
        try:
            skills = list(self.store.get('skill_levels'))
            levels, talents = read_character_stats(path, skills)
            trees = self.store.get('perk_trees')
            self.store.set('skill_levels', {skill: levels[skill] for skill in skills})
            self.store.set('perk_trees', {skill: [talents[skill][i] if skill in talents and i < len(talents[skill]) else points
                                                  for i, points in enumerate(tree)] for skill, tree in trees.items()})
            self.log(f'Loaded skills and talents from {os.path.basename(path)}')
            biome, evidence = progression_from_save(path)
            self.store.set('biomes', biomes_up_to(biome))
            if evidence:
                items = list(evidence.values())[-1]
                self.log(f'Progression from {os.path.basename(path)}: up to {biome} (unlocked by: {", ".join(items)})')
            else:
                self.log(f'Progression from {os.path.basename(path)}: no bosses beaten yet, up to {biome}')
            eaten = sorted(permanent_health_eaten(path))
            self.store.set('permanent_health_foods', eaten) # The Settings tab's switches; the total follows
            self.store.set('settings.Permanent max health', float(sum(v for c, _, v in permanent_health_foods() if c in eaten)))
            for setting, on in soul_settings(path).items(): # Souls collected and not disabled
                self.store.set(f'settings.{setting}', on)
            self.log(f"Souls: {', '.join(s + (' on' if on else ' off') for s, on in soul_settings(path).items())}"
                     f" | permanent foods eaten: {', '.join(n for c, n, _ in permanent_health_foods() if c in eaten) or 'none'}")
        except (OSError, ValueError, KeyError) as e:
            self.set_load_status(f'Could not load: {e}', good=False)
            return
        row = sorted(index.row() for index in self.character_list.selectedIndexes())[0]
        self.set_load_status(f'Loaded {self.character_list.item(row).text()}')
