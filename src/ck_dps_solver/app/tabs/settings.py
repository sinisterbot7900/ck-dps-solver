"""Settings tab: the theme, then the situations the DPS is calculated for (a switch or number per setting, hover text
for each), and the permanent max health foods (a switch each; Load on the Items tab sets them from a save)."""
import html
import itertools

from PySide6.QtWidgets import QButtonGroup, QGridLayout, QHBoxLayout, QLabel, QPushButton, QVBoxLayout, QWidget

from ck_dps_solver import defaults
from ck_dps_solver.model.progression import BIOME_NAMES, consumable_biome
from ck_dps_solver.model.sources import sources
from ck_dps_solver.saves.save_reader import permanent_health_food_ids, permanent_health_foods

from ck_dps_solver.app import labels, theme
from ck_dps_solver.app.widgets import bind
from ck_dps_solver.app.widgets.collapse import Collapsible

LABEL_WIDTH = 170
COLUMN_WIDTH = 300 # Setting columns, the same in every grid so they line up
# Settings only set bonuses use (settings a talent also uses, e.g. Max health or Range stacks, stay with the others)
SET_ONLY_SETTINGS = ('Not hit', 'Kill stacks', 'Recently dodged', 'Recently mined', 'Adjacent to water', 'Burning')
PERMANENT = 'Permanent max health'


def switch(text, on_change, label_width=LABEL_WIDTH):
    """A label and an On | Off switch not tied to one store value: (widget, set_on(bool), label)"""
    widget = QWidget()
    row = QHBoxLayout(widget)
    row.setContentsMargins(0, 0, 0, 0)
    row.setSpacing(0)
    label = QLabel(text)
    label.setFixedWidth(label_width)
    row.addWidget(label)
    row.addSpacing(8)
    on, off = QPushButton('On'), QPushButton('Off')
    group = QButtonGroup(widget)
    for button, side in ((on, 'left'), (off, 'right')):
        button.setCheckable(True)
        button.setProperty('segment', side)
        group.addButton(button)
        row.addWidget(button)
    on.toggled.connect(lambda checked: on_change(bool(checked)))
    def set_on(value): # Both buttons quiet: checking one unchecks the other, which would signal a change
        on.blockSignals(True); off.blockSignals(True)
        (on if value else off).setChecked(True)
        on.blockSignals(False); off.blockSignals(False)
    return widget, set_on, label


class SettingsTab(QWidget):
    def __init__(self, store):
        super().__init__()
        self.store = store
        layout = QVBoxLayout(self)
        look = QHBoxLayout()
        look.addWidget(QLabel('Theme'))
        look.addWidget(bind.combo(store, 'theme', [theme.DYNAMIC] + list(theme.THEMES),
                                  "Dynamic: each damage type's colors, fading into them when you change the damage type"))
        look.addStretch()
        layout.addLayout(look)
        intro = QLabel('Situations the DPS is calculated for. Several set bonuses and talents only count when their setting is on. '
                       'Hover over one to see what it affects.')
        intro.setWordWrap(True)
        layout.addWidget(intro)
        grid = QGridLayout()
        grid.setHorizontalSpacing(40)
        grid.setVerticalSpacing(8)
        names = [n for n in defaults.default_config()['settings'] if n != PERMANENT and n not in SET_ONLY_SETTINGS]
        for i, name in enumerate(names):
            grid.addWidget(bind.setting(store, name, labels.SETTING_HELP.get(name, ''), label_width=LABEL_WIDTH), i // 3, i % 3) # Switches line up in columns
        grid.setColumnStretch(3, 1)
        for column in range(3): grid.setColumnMinimumWidth(column, COLUMN_WIDTH) # Lines up with the set settings below
        layout.addLayout(grid)

        # Situations only a set bonus uses: under a toggle (settings talents also use stay above)
        sets_header = QHBoxLayout()
        sets_title = QLabel('Set bonus situations')
        sets_title.setFixedWidth(LABEL_WIDTH)
        sets_title.setToolTip('Situations only set bonuses use (Pandorium, Scarlet, Assassin, Carapace, Swamp Mage and Welder sets)')
        sets_header.addWidget(sets_title)
        self.sets_button = QPushButton('Show set settings')
        self.sets_button.setCheckable(True)
        self.sets_button.setProperty('toggle', True)
        self.sets_button.toggled.connect(self.show_sets)
        sets_header.addWidget(self.sets_button)
        sets_header.addStretch()
        layout.addSpacing(8)
        layout.addLayout(sets_header)
        self.sets_panel = QWidget()
        sets_grid = QGridLayout(self.sets_panel)
        sets_grid.setContentsMargins(0, 4, 0, 0)
        sets_grid.setHorizontalSpacing(40)
        sets_grid.setVerticalSpacing(8)
        for i, name in enumerate(n for n in defaults.default_config()['settings'] if n in SET_ONLY_SETTINGS):
            sets_grid.addWidget(bind.setting(store, name, labels.SETTING_HELP.get(name, ''), label_width=LABEL_WIDTH), i // 3, i % 3)
        sets_grid.setColumnStretch(3, 1)
        for column in range(3): sets_grid.setColumnMinimumWidth(column, COLUMN_WIDTH)
        layout.addWidget(self.sets_panel)
        self.sets_slide = Collapsible(self.sets_panel, self)
        self.sets_slide.set_open(False, animate=False)

        # Permanent max health: the total, and (opened) a switch per food, earliest biome first
        self.food_ids = permanent_health_food_ids()
        self.food_biomes = {c: consumable_biome(i) for c, i in self.food_ids.items()}
        tier = lambda c: BIOME_NAMES.index(self.food_biomes[c]) if self.food_biomes.get(c) in BIOME_NAMES else len(BIOME_NAMES)
        self.foods = sorted(permanent_health_foods(), key=lambda f: (tier(f[0]), -f[2], f[1])) # [(condition, name, max health)]
        header = QHBoxLayout()
        title = QLabel(PERMANENT)
        title.setFixedWidth(LABEL_WIDTH)
        title.setToolTip(labels.SETTING_HELP.get(PERMANENT, ''))
        header.addWidget(title)
        self.total = QLabel()
        font = self.total.font(); font.setBold(True); self.total.setFont(font)
        header.addWidget(self.total)
        header.addSpacing(16)
        self.foods_button = QPushButton('Show foods')
        self.foods_button.setCheckable(True)
        self.foods_button.setProperty('toggle', True)
        self.foods_button.toggled.connect(self.show_foods)
        header.addWidget(self.foods_button)
        header.addStretch()
        layout.addSpacing(8)
        layout.addLayout(header)
        self.foods_panel = QWidget()
        panel = QGridLayout(self.foods_panel)
        panel.setContentsMargins(0, 4, 0, 0)
        panel.setHorizontalSpacing(40)
        panel.setVerticalSpacing(8)
        widget, self.set_all, _ = switch('All', self.all_changed, label_width=290)
        widget.setToolTip('Every permanent food on, or (off) none')
        panel.addWidget(widget, 0, 0)
        self.food_switches, self.food_rows = {}, {}
        for n, (condition, name, value) in enumerate(self.foods):
            widget, set_on, label = switch(f'{name} (+{value})', lambda on, c=condition: self.food_changed(c, on), label_width=290)
            self.food_switches[condition] = set_on
            self.food_rows[condition] = (widget, label, name, value)
            panel.addWidget(widget, 1 + n // 3, n % 3)
        panel.setColumnStretch(3, 1)
        layout.addWidget(self.foods_panel)
        self.foods_slide = Collapsible(self.foods_panel, self)
        self.foods_slide.set_open(False, animate=False)
        layout.addStretch()

        if store.get('permanent_health_foods') is None: # Older configs: the foods that add up to the saved total
            store.set('permanent_health_foods', self.foods_for(store.get(f'settings.{PERMANENT}') or 0))
        store.changed.connect(lambda path: self.refresh_foods() if path in ('', 'permanent_health_foods', f'settings.{PERMANENT}', 'biomes') else None)
        self.refresh_foods()

    # ------------------------------------------------------------ permanent max health

    def where_to_get(self, condition, later):
        """Hover text for a food: what it gives, its biome, and where to get it (the wiki's obtaining data)"""
        _, _, name, value = self.food_rows[condition]
        internal_id = self.food_ids.get(condition)
        biome = self.food_biomes.get(condition) or 'unknown biome'
        lines = sources(internal_id, limit=4) if internal_id else ['Unknown (not in the wiki data)']
        progression = f'<br><i>After your progression: needs {html.escape(biome)}</i>' if later else ''
        return (f'<b>{html.escape(name)}</b><br>+{value} max health for good, once eaten<br>{html.escape(biome)}{progression}<br><br>'
                + '<br>'.join(html.escape(line) for line in lines))

    def is_later(self, condition):
        """From a biome after the progression set on the Items tab"""
        biomes = self.store.get('biomes')
        biome = self.food_biomes.get(condition)
        return biomes is not None and biome is not None and biome not in biomes

    def foods_for(self, total):
        """The fewest foods whose max health adds up to a total (none if no combination does)"""
        for size in range(len(self.foods) + 1):
            for combo in itertools.combinations(self.foods, size):
                if sum(v for *_, v in combo) == total:
                    return sorted(c for c, *_ in combo)
        return []

    def chosen(self):
        return set(self.store.get('permanent_health_foods') or [])

    def set_foods(self, foods):
        foods = sorted(foods)
        self.store.set('permanent_health_foods', foods)
        self.store.set(f'settings.{PERMANENT}', float(sum(v for c, _, v in self.foods if c in foods)))

    def food_changed(self, condition, on):
        foods = self.chosen()
        (foods.add if on else foods.discard)(condition)
        self.set_foods(foods)

    def all_changed(self, on):
        self.set_foods({c for c, *_ in self.foods} if on else set())

    def refresh_foods(self):
        foods = self.chosen()
        muted = theme.color('text_muted').name()
        for condition, set_on in self.food_switches.items():
            set_on(condition in foods)
            widget, label, name, value = self.food_rows[condition]
            later = self.is_later(condition)
            label.setText(f'{name} (+{value})' + (' (later biome)' if later else ''))
            label.setStyleSheet(f'color: {muted};' if later else '')
            widget.setToolTip(self.where_to_get(condition, later))
        self.set_all(len(foods) == len(self.foods))
        self.total.setText(f"{sum(v for c, _, v in self.foods if c in foods)} max health")

    def show_sets(self, on):
        self.sets_slide.set_open(on)
        self.sets_button.setText('Hide set settings' if on else 'Show set settings')

    def show_foods(self, on):
        self.foods_slide.set_open(on)
        self.foods_button.setText('Hide foods' if on else 'Show foods')
