"""Search tab: options, presets, results tables, the log, and (below the results) the clicked loadout's details. The run
button and progress bar are built here but shown in the window's header (run_bar)."""
import copy
import datetime
import os

from PySide6.QtCore import QPointF, QRect, QRectF, QSize, Qt, Signal
from PySide6.QtGui import QIcon, QKeySequence, QPainter, QPixmap, QPolygonF, QShortcut
from PySide6.QtWidgets import (QCheckBox, QComboBox, QGridLayout, QHBoxLayout, QInputDialog, QLabel, QLineEdit, QMessageBox, QPlainTextEdit,
                               QProgressBar, QPushButton, QSplitter, QTabWidget, QVBoxLayout, QWidget)

from ck_dps_solver import defaults
from ck_dps_solver.app import labels, state, theme
from ck_dps_solver.app.widgets import bind
from ck_dps_solver.app.widgets.collapse import Collapsible
from ck_dps_solver.app.widgets.details import LoadoutDetails
from ck_dps_solver.app.widgets.item_tooltip import item_tooltip
from ck_dps_solver.app.widgets.results import ResultsTable
from ck_dps_solver.app.worker import start_search
from ck_dps_solver.engine import solver


HISTORY_SIZE = 5 # Earlier runs kept for this session


RUN_BUTTON_SIZE = 34 # Run button (square) and the run bar's height
RUN_ICON_SIZE = 16
RUN_BAR_WIDTH = 460


def run_icon(stop=False):
    """A right-pointing run arrow, or a stop square, in the accent button's text color"""
    size = RUN_ICON_SIZE * 2 # Drawn at twice the size: sharp on high-DPI screens
    pixmap = QPixmap(size, size)
    pixmap.setDevicePixelRatio(2)
    pixmap.fill(Qt.transparent)
    painter = QPainter(pixmap)
    painter.setRenderHint(QPainter.Antialiasing)
    painter.setPen(Qt.NoPen)
    painter.setBrush(theme.color('accent_text'))
    s = RUN_ICON_SIZE
    if stop:
        painter.drawRoundedRect(QRectF(s * 0.2, s * 0.2, s * 0.6, s * 0.6), 2, 2)
    else:
        painter.drawPolygon(QPolygonF([QPointF(s * 0.25, s * 0.12), QPointF(s * 0.88, s * 0.5), QPointF(s * 0.25, s * 0.88)]))
    painter.end()
    return QIcon(pixmap)


class RunBar(QProgressBar):
    """The progress bar with the search's status written on it: the text over the filled part takes a color that reads
    on the fill, the rest the normal text color"""
    def __init__(self):
        super().__init__()
        self.setTextVisible(False) # Drawn below
        self.label = ''

    def setText(self, text):
        self.label = text
        self.update()

    def text(self):
        return self.label

    def paintEvent(self, event):
        super().paintEvent(event)
        span = self.maximum() - self.minimum()
        filled = 0 if span <= 0 else round(self.width() * (self.value() - self.minimum()) / span) # Busy: no fill
        painter = QPainter(self)
        for clip, color in ((QRect(0, 0, filled, self.height()), theme.readable_on(theme.progress_color())),
                            (QRect(filled, 0, self.width() - filled, self.height()), theme.color('text'))):
            painter.setClipRect(clip)
            painter.setPen(color)
            painter.drawText(self.rect(), Qt.AlignCenter, self.label)
        painter.end()


class SearchTab(QWidget):
    loadout_selected = Signal(object, object) # Search result loadout, run info (for the details panels)

    def __init__(self, store, window):
        super().__init__()
        self.store, self.main_window = store, window
        self.thread = self.worker = None
        self.info = None
        self.all_rows = []
        layout = QVBoxLayout(self)

        # Options
        options = QHBoxLayout()
        options.addWidget(QLabel('Output CSV'))
        output = bind.line(store, 'output', '{damage_type} is replaced by the damage type')
        output.setMinimumWidth(420)
        options.addWidget(output)
        hint = QLabel('{damage_type} is replaced by the damage type')
        hint.setProperty('muted', True)
        options.addWidget(hint)
        options.addStretch()
        self.advanced_button = QPushButton('Advanced settings')
        self.advanced_button.setCheckable(True)
        self.advanced_button.setProperty('toggle', True)
        self.advanced_button.setToolTip('Loadouts to keep, skipping dominated items')
        self.advanced_button.toggled.connect(self.show_advanced)
        options.addWidget(self.advanced_button)
        layout.addLayout(options)

        self.advanced = QWidget()
        advanced = QHBoxLayout(self.advanced)
        advanced.setContentsMargins(0, 0, 0, 0)
        advanced.addWidget(QLabel('Loadouts to keep (top N)'))
        advanced.addWidget(bind.spin(store, 'top_n', 1, 10_000_000, 1000, width=110))
        advanced.addSpacing(16)
        advanced.addWidget(bind.checkbox(store, 'drop_dominated', 'Skip dominated items (faster; best loadout unchanged)'))
        advanced.addStretch()
        layout.addWidget(self.advanced)
        self.advanced_slide = Collapsible(self.advanced, self)
        self.advanced_slide.set_open(False, animate=False)

        # Presets: every choice in the window
        presets = QHBoxLayout()
        presets.addWidget(QLabel('Preset'))
        self.presets = state.load_presets()
        self.preset_box = QComboBox()
        self.preset_box.setMinimumWidth(240)
        self.preset_box.addItems(sorted(self.presets))
        self.preset_box.setCurrentIndex(-1)
        presets.addWidget(self.preset_box)
        for text, action in (('Load', self.load_preset), ('Save as...', self.save_preset), ('Delete', self.delete_preset)):
            button = QPushButton(text)
            button.clicked.connect(action)
            presets.addWidget(button)
        presets.addStretch()
        # Earlier runs (this session): switch back without searching again
        self.history = [] # Newest first: {label, info, rows, upgrades}
        self.history_box = QComboBox()
        self.history_box.setMinimumWidth(320)
        self.history_box.setToolTip(f'Your last {HISTORY_SIZE} searches; pick one to show its results again')
        self.history_box.currentIndexChanged.connect(self.show_history)
        self.history_box.hide()
        presets.addWidget(self.history_box)
        layout.addLayout(presets)

        # Run bar (shown in the window's header, on every tab): one button that runs, and stops while running, and
        # the progress bar, which also shows the status
        self.running = False
        self.run_bar = QWidget()
        run = QHBoxLayout(self.run_bar)
        run.setContentsMargins(0, 0, 0, 0)
        run.setSpacing(8)
        self.run_button = QPushButton()
        self.run_button.setProperty('accent', True)
        self.run_button.setFixedSize(RUN_BUTTON_SIZE, RUN_BUTTON_SIZE)
        self.run_button.setIconSize(QSize(RUN_ICON_SIZE, RUN_ICON_SIZE))
        self.run_button.clicked.connect(lambda: self.stop() if self.running else self.run())
        QShortcut(QKeySequence('Ctrl+R'), window, activated=lambda: None if self.running else self.run())
        QShortcut(QKeySequence('Esc'), window, activated=lambda: self.stop() if self.running else None)
        self.progress = RunBar()
        self.progress.setFixedSize(RUN_BAR_WIDTH, RUN_BUTTON_SIZE)
        self.status = self.progress # The status is written on the bar
        self.status.setText('Ready')
        run.addWidget(self.run_button)
        run.addWidget(self.progress)
        self.set_running(False)

        # Filter (in the results tab bar's top right corner, beside the Loadouts / Upgrades tabs)
        corner = QWidget()
        filters = QHBoxLayout(corner)
        filters.setContentsMargins(0, 0, 0, 4)
        open_csv = QPushButton('Open CSV')
        open_csv.setToolTip('Open the search\'s loadouts file')
        open_csv.clicked.connect(self.open_csv)
        filters.addWidget(open_csv)
        self.filter_box = QLineEdit()
        self.filter_box.setPlaceholderText('Filter loadouts, e.g. scarab titan')
        self.filter_box.setToolTip('Only loadouts with all these words in some item name')
        self.filter_box.setFixedWidth(260)
        filters.addWidget(self.filter_box)
        self.per_weapon = QCheckBox('Best loadout per weapon')
        self.per_weapon.toggled.connect(self.show_rows)
        filters.addWidget(self.per_weapon)
        self.count = QLabel('')
        self.count.setProperty('muted', True)
        self.count.ensurePolished() # The theme's font, so the width below fits
        self.count.setMinimumWidth(self.count.fontMetrics().horizontalAdvance('100,000 of 100,000 kept loadouts') + 8) # Stays put when it fills in
        filters.addWidget(self.count)

        # Results, details, log: resizable
        self.results = QTabWidget()
        self.loadouts = ResultsTable(labels.RESULT_COLUMNS)
        self.upgrades = ResultsTable(labels.UPGRADE_COLUMNS, {'Upgrade': 220, 'Slot': 90, 'Biome': 140, 'Uses': 420, 'Where to get': 700})
        self.results.addTab(self.loadouts, 'Loadouts')
        self.results.addTab(self.upgrades, 'Upgrades (owned items + biomes)')
        self.results.setCornerWidget(corner, Qt.TopRightCorner)
        self.results.currentChanged.connect(lambda index: corner.setVisible(index == 0)) # The filter is for loadouts
        for table in (self.loadouts, self.upgrades):
            table.horizontalHeader().setToolTip('Click a header to sort; right-click a row to copy it')
        self.filter_box.textChanged.connect(lambda text: (self.loadouts.proxy.set_text(text), self.update_count()))
        self.loadouts.row_selected.connect(self.on_selected)
        self.loadouts.source.tooltip = self.item_hover
        self.loadouts.menu_actions = self.loadout_menu
        self.upgrades.source.expand = True # Hover shows a cell's whole text (where to get, uses)
        self.hover_cache = {}
        store.changed.connect(lambda path: self.update_upgrades_tab() if path in ('', 'save_filter', 'save_filter.enabled') else None)
        self.update_upgrades_tab()

        self.details = LoadoutDetails() # The clicked loadout: DPS curve, character sheet, where stats come from
        self.log_box = QPlainTextEdit()
        self.log_box.setReadOnly(True)
        splitter = QSplitter(Qt.Vertical)
        splitter.addWidget(self.results)
        splitter.addWidget(self.details)
        splitter.addWidget(self.log_box)
        splitter.setSizes([400, 280, 90])
        layout.addWidget(splitter, 1)

    # ------------------------------------------------------------ presets

    def show_advanced(self, on):
        self.advanced_slide.set_open(on)
        self.advanced_button.setText('Hide advanced settings' if on else 'Advanced settings')

    def preset_config(self):
        """What a preset keeps: the search config, plus the save folder and name display"""
        config = self.store.search_config()
        config['save_folder'] = self.store.get('save_folder', '')
        config['show_names'] = bool(self.store.get('show_names', True))
        return config

    def write_presets(self):
        state.save_presets(self.presets)
        self.preset_box.blockSignals(True)
        self.preset_box.clear()
        self.preset_box.addItems(sorted(self.presets))
        self.preset_box.setCurrentIndex(-1)
        self.preset_box.blockSignals(False)

    def save_preset(self):
        name, ok = QInputDialog.getText(self, 'Save preset', 'Preset name:', text=self.preset_box.currentText())
        name = name.strip()
        if not ok or not name:
            return
        self.presets[name] = self.preset_config()
        self.write_presets()
        self.preset_box.setCurrentText(name)
        self.log(f'Saved preset "{name}"')

    def load_preset(self):
        name = self.preset_box.currentText()
        if name not in self.presets:
            QMessageBox.information(self, 'No preset', 'Choose a preset first.')
            return
        from ck_dps_solver.app.tabs.items import biome_label, biomes_for
        base = defaults.default_config()
        config = dict(base, **copy.deepcopy(self.presets[name]))
        config['settings'] = dict(base['settings'], **config.get('settings', {}))
        config['biomes'] = biomes_for(biome_label(config.get('biomes'))) # As the dropdown shows it (older names dropped)
        config['theme'] = self.store.get('theme') # Presets don't change the look
        self.store.replace(config)
        self.log(f'Loaded preset "{name}"')

    def delete_preset(self):
        name = self.preset_box.currentText()
        if name in self.presets and QMessageBox.question(self, 'Delete preset', f'Delete preset "{name}"?') == QMessageBox.Yes:
            del self.presets[name]
            self.write_presets()
            self.log(f'Deleted preset "{name}"')

    # ------------------------------------------------------------ results tabs

    def update_upgrades_tab(self):
        """Upgrade suggestions only come from owned-item runs"""
        self.results.setTabVisible(1, bool(self.store.get('save_filter.enabled')))

    # ------------------------------------------------------------ run

    def run(self):
        config = self.store.search_config()
        save_filter = config['save_filter']
        if save_filter['enabled'] and not save_filter['player_files']:
            QMessageBox.warning(self, 'No character selected', 'Pick at least one character on the Items tab, or search every item.')
            return
        if save_filter.get('center') is not None and len(save_filter['center']) != 2:
            QMessageBox.warning(self, 'Invalid center', 'Center must be "x, z" or blank.')
            return
        self.store.save()
        biomes = config.get('biomes')
        self.run_label = (f"{config['damage_type']}, {'owned items' if config['save_filter']['enabled'] else 'every item'}, "
                          f"{'up to ' + biomes[-1] if biomes else 'all biomes'}")
        self.loadouts.set_rows([])
        self.upgrades.set_rows([])
        self.all_rows, self.info = [], None
        self.hover_cache = {}
        self.details.clear()
        self.update_count()
        self.log_box.clear()
        self.set_running(True)
        self.progress.setRange(0, 0) # Busy until the first stage starts
        self.status.setText('Preparing items...')
        self.thread, self.worker = start_search(config)
        self.worker.stage.connect(self.on_stage)
        self.worker.progressed.connect(self.on_progress)
        self.worker.logged.connect(self.log)
        self.worker.finished.connect(self.on_finished)
        self.worker.failed.connect(self.on_failed)
        self.thread.start()

    def set_running(self, running):
        """The run button: a run arrow, or a stop square while a search runs"""
        self.running = running
        self.run_button.setIcon(run_icon(stop=running))
        self.run_button.setToolTip('Stop the search (Esc)' if running else 'Run the search (Ctrl+R)')

    def apply_theme(self):
        self.run_button.setIcon(run_icon(stop=self.running)) # Drawn in the theme's button text color

    def stop(self):
        if self.worker is not None:
            self.worker.stop_event.set()
            self.status.setText('Stopping...')

    def on_stage(self, total, description):
        self.progress.setRange(0, total)
        self.progress.setValue(0)
        self.status.setText(description)

    def on_progress(self, done, total, left):
        self.progress.setValue(done)
        eta = '' if left < 0 else (f' · ~{left / 60:.0f} min left' if left >= 90 else f' · ~{left:.0f}s left')
        self.status.setText(f'{done:,} / {total:,}{eta}')

    def on_finished(self, results, info):
        self.set_running(False)
        if not info['stopped']:
            self.progress.setValue(self.progress.maximum())
        self.status.setText(f"{'Stopped (best found so far)' if info['stopped'] else 'Done'} in {info['seconds']:.0f}s")
        self.info = info
        self.all_rows = [(i, [row[c] for c in labels.RESULT_COLUMNS]) for i, (_, row) in enumerate(results.head(labels.KEPT_RESULTS).iterrows())]
        self.show_rows()
        upgrades = info.get('upgrades')
        if upgrades is not None:
            self.upgrades.set_rows([(i, [row[c] for c in labels.UPGRADE_COLUMNS]) for i, (_, row) in enumerate(upgrades.iterrows())])
            self.upgrades.sortByColumn(labels.UPGRADE_COLUMNS.index('Gain %'), Qt.DescendingOrder) # Biggest gain first
            if len(upgrades) and self.store.get('save_filter.enabled'):
                self.results.setCurrentIndex(1)
        self.main_window.statusBar().showMessage(f"Saved {info['output']}", 8000)
        best = f"{self.all_rows[0][1][0]:,} DPS" if self.all_rows else 'no loadouts'
        self.history.insert(0, {'label': f"{datetime.datetime.now():%H:%M} {self.run_label}: {best}", 'info': info, 'rows': self.all_rows,
                                'upgrades': list(self.upgrades.source.rows), 'status': self.status.text()})
        del self.history[HISTORY_SIZE:]
        self.history_box.blockSignals(True)
        self.history_box.clear()
        self.history_box.addItems([entry['label'] for entry in self.history])
        self.history_box.setCurrentIndex(0)
        self.history_box.blockSignals(False)
        self.history_box.setVisible(len(self.history) > 1)

    def show_history(self, index):
        """Show an earlier run's results again"""
        if not 0 <= index < len(self.history) or self.running:
            return
        entry = self.history[index]
        self.info, self.all_rows = entry['info'], entry['rows']
        self.details.clear()
        self.show_rows()
        self.upgrades.set_rows(entry['upgrades'])
        self.upgrades.sortByColumn(labels.UPGRADE_COLUMNS.index('Gain %'), Qt.DescendingOrder)
        self.status.setText(entry['status'] if index == 0 else f"Showing an earlier run ({entry['label'].split(' ')[0]})")

    def loadout_menu(self, row_id):
        """Right-click actions for a loadout: pin it to compare others with it"""
        if row_id is None or self.info is None or row_id >= len(self.info.get('best_loadouts', [])):
            return []
        actions = [('Pin for comparison', lambda: self.details.pin(self.info['best_loadouts'][row_id], self.info))]
        if self.details.pinned is not None:
            actions.append(('Unpin', self.details.unpin))
        return actions

    def on_failed(self, message):
        self.set_running(False)
        self.progress.setRange(0, 1)
        self.status.setText('Error (see log)')
        self.log(message)

    def log(self, text):
        self.log_box.appendPlainText(text)

    # ------------------------------------------------------------ results

    def show_rows(self):
        rows = self.all_rows
        if self.per_weapon.isChecked():
            best = {}
            for row_id, values in rows:
                if values[1] not in best or values[0] > best[values[1]][1][0]:
                    best[values[1]] = (row_id, values)
            rows = list(best.values())
        self.loadouts.set_rows(rows)
        self.loadouts.sortByColumn(0, Qt.DescendingOrder)
        self.update_count()

    def update_count(self):
        shown = self.loadouts.proxy.rowCount()
        self.count.setText(f'{shown:,} of {len(self.all_rows):,} kept loadouts' if self.all_rows else '')

    def on_selected(self, row_id):
        if row_id is None or self.info is None or row_id >= len(self.info.get('best_loadouts', [])):
            return
        loadout = self.info['best_loadouts'][row_id]
        try:
            self.details.show_loadout(loadout, self.info)
        except Exception as e: # A details bug shouldn't break the results
            self.log(f'Could not show the loadout details: {type(e).__name__}: {e}')
        self.loadout_selected.emit(loadout, self.info)

    LOADOUT_SLOTS = {'Weapon': 1, 'Helm': 2, 'Breast armor': 3, 'Pants armor': 4, 'Necklace': 5, 'Ring1': 6, 'Ring2': 7, 'Offhand': 8}

    def item_hover(self, row_id, column):
        """Hover text for an item cell: its stats as the calculation used them"""
        if self.info is None or row_id >= len(self.info.get('best_loadouts', [])):
            return None
        if (row_id, column) not in self.hover_cache:
            loadout = self.info['best_loadouts'][row_id]
            if column in self.LOADOUT_SLOTS:
                item = loadout[self.LOADOUT_SLOTS[column]]
            else: # Lantern, Bag, Pet: the searched one (Try all, Best, owned pets), else the configured one
                worn = {i.item_category: i for i in solver.loadout_items(loadout, self.info['fixed_items'])}
                item = worn.get(column)
            damage_type = self.info.get('damage_type') or loadout[1].damage_type
            self.hover_cache[(row_id, column)] = item_tooltip(item, damage_type) if item is not None else None
        return self.hover_cache[(row_id, column)]

    def open_csv(self):
        path = (self.info or {}).get('output') or self.store.get('output', '').format(damage_type=self.store.get('damage_type', '').lower())
        if not os.path.isabs(path):
            path = os.path.abspath(path)
        if os.path.exists(path):
            os.startfile(path)
        else:
            QMessageBox.information(self, 'No results yet', f'{path} does not exist yet. Run a search first.')
