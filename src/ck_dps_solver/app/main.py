"""The main window. The search logic is in engine/ and model/; this is only the window."""
import multiprocessing
import os
import sys

from PySide6.QtCore import QEasingCurve, QParallelAnimationGroup, QPoint, QPropertyAnimation, QSettings, Qt
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import (QApplication, QFrame, QGraphicsOpacityEffect, QHBoxLayout, QLabel, QMainWindow, QTabWidget,
                               QVBoxLayout, QWidget)

from ck_dps_solver import __version__, paths
from ck_dps_solver.app import crash_log, labels, state, theme
from ck_dps_solver.app.store import ConfigStore
from ck_dps_solver.app.tabs.character import CharacterTab
from ck_dps_solver.app.tabs.consumables import ConsumablesTab
from ck_dps_solver.app.tabs.items import ItemsTab
from ck_dps_solver.app.tabs.search import SearchTab
from ck_dps_solver.app.tabs.settings import SettingsTab
from ck_dps_solver.app.widgets import bind

TABS = ['Search', 'Items', 'Settings', 'Character', 'Consumables']
FADE_MS = 450 # Cross-fade between themes
SLIDE_MS = 350 # Sliding from one tab to another


# Store values that decide the theme
THEME_PATHS = ('', 'theme', 'damage_type')


class MainWindow(QMainWindow):
    def __init__(self, app):
        super().__init__()
        self.app = app
        self.store = ConfigStore()
        self.config = self.store.config
        self.setWindowTitle(f'Core Keeper DPS Solver {__version__}')
        app.setWindowIcon(QIcon(paths.resource('data', 'app_icon.png'))) # tools/make_icon.py
        self.resize(1280, 900)

        central = QWidget()
        layout = QVBoxLayout(central)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        layout.addWidget(self.build_header())
        self.tabs = QTabWidget()
        self.tabs.setDocumentMode(True)
        self.pages = {}
        self.search = SearchTab(self.store, self)
        self.items = ItemsTab(self.store, self.search.log)
        self.settings_tab = SettingsTab(self.store)
        self.character = CharacterTab(self.store, self.search.log)
        self.consumables = ConsumablesTab(self.store) # Last: it re-picks food when the other tabs change the progression or talents
        self.consumables.planner.use_search(self.search) # The cooking planner scores dishes on the search's loadouts
        self.pages = dict(zip(TABS, [self.search, self.items, self.settings_tab, self.character, self.consumables]))
        for name, page in self.pages.items():
            self.tabs.addTab(page, name)
        self.slide = None
        self.slide_from = None
        self.tabs.tabBar().tabBarClicked.connect(self.before_tab_change) # Before the switch: snapshot the page being left
        self.tabs.currentChanged.connect(self.slide_to_tab)
        body = QWidget()
        body_layout = QVBoxLayout(body)
        body_layout.setContentsMargins(10, 10, 10, 10)
        body_layout.addWidget(self.tabs)
        layout.addWidget(body)
        self.setCentralWidget(central)
        self.statusBar().showMessage('Ready')

        self.settings = QSettings(paths.user_file('qt_window.ini'), QSettings.IniFormat)
        if self.settings.value('geometry'):
            self.restoreGeometry(self.settings.value('geometry'))
        self.fade = None
        self.applied_theme = None
        self.apply_theme(self.wanted_theme())
        self.store.changed.connect(lambda path: self.fade_to(self.wanted_theme()) if path in THEME_PATHS else None)

    def build_header(self):
        header = QFrame()
        header.setObjectName('Header')
        row = QHBoxLayout(header)
        row.setContentsMargins(16, 10, 16, 10)
        title = QLabel('Core Keeper DPS Solver')
        title.setObjectName('Title')
        row.addWidget(title)
        row.addStretch()
        label = QLabel('Damage type')
        label.setObjectName('Subtitle')
        row.addWidget(label)
        self.damage_type_box = bind.combo(self.store, 'damage_type', labels.DAMAGE_TYPES)
        self.damage_type_box.setMinimumWidth(140)
        row.addWidget(self.damage_type_box)
        return header

    def wanted_theme(self):
        """The theme chosen on the Settings tab; for Dynamic, the damage type's theme"""
        chosen = self.store.get('theme')
        if chosen == theme.DYNAMIC:
            return self.store.get('damage_type') if self.store.get('damage_type') in theme.THEMES else theme.DEFAULT_THEME
        return chosen if chosen in theme.THEMES else theme.DEFAULT_THEME

    def apply_theme(self, name):
        theme.apply(self.app, name)
        self.applied_theme = name
        self.search.details.apply_theme() # The chart draws itself, so it isn't styled by the stylesheet
        self.consumables.apply_theme()
        self.character.apply_theme()
        self.settings_tab.refresh_foods() # Dimmed later-biome foods use the theme's muted color

    def set_theme(self, name):
        """Choose a theme (as the Settings tab's Theme box does)"""
        self.store.set('theme', name)
        self.fade_to(self.wanted_theme())

    def fade_to(self, name):
        """Cross-fade into a theme: a snapshot of the window in the old colors fades out over the restyled window"""
        if name == self.applied_theme:
            return
        if not self.isVisible():
            self.apply_theme(name)
            return
        if self.fade is not None: # Changed again mid-fade: start from what's on screen now
            self.fade[1].stop()
            self.fade[0].deleteLater()
        snapshot = QLabel(self)
        snapshot.setPixmap(self.grab())
        snapshot.setGeometry(self.rect())
        snapshot.setAttribute(Qt.WA_TransparentForMouseEvents) # Clicks go through to the window during the fade
        snapshot.show()
        snapshot.raise_()
        self.apply_theme(name)
        effect = QGraphicsOpacityEffect(snapshot)
        snapshot.setGraphicsEffect(effect)
        animation = QPropertyAnimation(effect, b'opacity', self)
        animation.setDuration(FADE_MS)
        animation.setStartValue(1.0)
        animation.setEndValue(0.0)
        animation.setEasingCurve(QEasingCurve.InOutQuad)
        def done():
            snapshot.deleteLater()
            if self.fade is not None and self.fade[0] is snapshot:
                self.fade = None
        animation.finished.connect(done)
        self.fade = (snapshot, animation)
        animation.start()

    def before_tab_change(self, index):
        if index != self.tabs.currentIndex() and index >= 0:
            self.slide_from = (self.tabs.currentIndex(), self.tabs.currentWidget().grab())

    def slide_to_tab(self, index):
        """Clicked a tab: the old page slides off one side while the new one slides in from the other"""
        start = self.slide_from
        self.slide_from = None
        if start is None or not self.isVisible():
            return
        old_index, old_picture = start
        if self.slide is not None: # Clicked again mid-slide: finish the last one at once
            self.slide[0].stop()
            for label in self.slide[1]: label.deleteLater()
            self.slide = None
        page = self.tabs.currentWidget()
        stack = page.parentWidget() # The tab widget's page area
        page.layout().activate()
        new_picture = page.grab()
        width = stack.width()
        direction = 1 if index > old_index else -1 # Moving right: content slides left
        group = QParallelAnimationGroup(self)
        labels_ = []
        for picture, begin, end in ((old_picture, 0, -direction * width), (new_picture, direction * width, 0)):
            label = QLabel(stack)
            label.setPixmap(picture)
            label.setGeometry(page.geometry())
            label.move(begin, page.y())
            label.setAttribute(Qt.WA_TransparentForMouseEvents)
            label.show()
            label.raise_()
            animation = QPropertyAnimation(label, b'pos', group)
            animation.setDuration(SLIDE_MS)
            animation.setStartValue(QPoint(begin, page.y()))
            animation.setEndValue(QPoint(end, page.y()))
            animation.setEasingCurve(QEasingCurve.OutCubic)
            group.addAnimation(animation)
            labels_.append(label)
        def done():
            for label in labels_: label.deleteLater()
            if self.slide is not None and self.slide[0] is group:
                self.slide = None
        group.finished.connect(done)
        self.slide = (group, labels_)
        group.start()

    def closeEvent(self, event):
        search = self.search
        if search.thread is not None and search.thread.isRunning():
            # Stop the search first, then close (waiting here would block the search thread from seeing the stop)
            search.stop()
            self.statusBar().showMessage('Stopping the search, then closing...')
            if not getattr(self, '_close_when_stopped', False):
                self._close_when_stopped = True
                search.thread.finished.connect(self.close)
            event.ignore()
            return
        self.settings.setValue('geometry', self.saveGeometry())
        self.store.save()
        super().closeEvent(event)


def main(self_test=False):
    """Open the window (self_test: check the build without a screen instead; see run_self_test)"""
    multiprocessing.freeze_support() # A packaged exe must not relaunch the window in each search worker
    crash_log.install() # Errors go to crash.log (the exe has no console)
    os.chdir(paths.USER_DIR) # Relative paths (outputs/) are in the user folder
    if self_test:
        return run_self_test()
    app = QApplication(sys.argv[:1])
    window = MainWindow(app)
    window.show()
    return app.exec()


def run_self_test():
    """Check a build without a screen ("CK DPS Solver.exe" --self-test): the window loads, a small search runs (numba
    compiles), and the cooking planner scores; the report goes to self_test.log in the user folder. Exit code 0 = passed."""
    import time
    import traceback
    from ck_dps_solver import defaults
    from ck_dps_solver.engine import solver
    from ck_dps_solver.model.cooking import plan
    from ck_dps_solver.model.item_stats import wiki_data
    os.environ['QT_QPA_PLATFORM'] = 'offscreen'
    report, ok = [], True
    try:
        app = QApplication(sys.argv[:1])
        window = MainWindow(app)
        window.store.save = lambda: None # Leave the user's settings alone
        report.append(f'version {__version__}; window: {len(window.pages)} tabs, theme {window.wanted_theme()}')
        import numba
        report.append(f"numba cache: {numba.config.CACHE_DIR or '(next to the sources, else the user-wide folder)'}")
        config = defaults.default_config()
        config.update(damage_type='Magic', top_n=3, suggest_upgrades=False, search_pets=False, search_lanterns=False, search_bags=False,
                      best_fixed={}, biomes=['Dirt'], output=paths.user_file('outputs', 'self_test_{damage_type}.csv'))
        config['save_filter'] = dict(config['save_filter'], enabled=False)
        start = time.time()
        quiet = type('Progress', (), {'start': lambda self, total, description: None, 'update': lambda self, n: None})() # As the window's
        _, info = solver.run_search(config, progress=quiet, log=lambda message: None)
        best = info['best_loadouts'][0]
        report.append(f'search: {info["loadouts"]:,} loadouts in {time.time() - start:.1f}s; best {best[0]:,} DPS with {solver.display_name(best[1])}')
        records = [i for i, r in wiki_data()['consumables'].items() if r['cooked']][:6]
        rows, _ = plan({i: 2 for i in records}, solver.loadout_items(best, info['fixed_items']), info['character_kwargs'],
                       info['consumable_keys'], solver.loadout_dps)
        report.append(f'cooking planner: {len(rows)} dishes')
        ok = best[0] > 0 and len(rows) > 0
    except Exception:
        ok = False
        report.append(traceback.format_exc())
    report.append('PASSED' if ok else 'FAILED')
    with open(paths.user_file('self_test.log'), 'w', encoding='utf8') as file:
        file.write('\n'.join(report) + '\n')
    return 0 if ok else 1
