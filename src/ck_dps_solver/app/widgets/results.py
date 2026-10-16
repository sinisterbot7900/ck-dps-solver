"""Results tables: sortable (click a header), filterable, right-click (or Ctrl+C) to copy a row."""
import html

from PySide6.QtCore import QAbstractTableModel, QModelIndex, QSortFilterProxyModel, Qt, Signal
from PySide6.QtGui import QAction, QKeySequence
from PySide6.QtWidgets import QAbstractItemView, QApplication, QHeaderView, QMenu, QTableView

NUMERIC = {'DPS', 'Gain', 'Gain %', 'Alone %', 'Can cook'}
PERCENT = {'Gain %', 'Alone %'} # Shown as they are (two decimals), not as whole numbers


def expanded(value):
    """A cell's full text for hover: entries of '|' / '||' lists on their own lines"""
    text = html.escape(f'{value:,}' if isinstance(value, int) else str(value))
    long = len(text) > 80
    text = text.replace(' || ', '<br><br>').replace(' | ', '<br>').replace('; ', '<br>') # One entry (or source) per line
    return f'<table width="520"><tr><td>{text}</td></tr></table>' if long else text # Long text: wider than Qt's default


class RowsModel(QAbstractTableModel):
    """Rows of values (one per column); each row carries an id (e.g. its index among the search's best loadouts)"""
    def __init__(self, columns):
        super().__init__()
        self.columns = list(columns)
        self.rows = [] # (row id, [values])
        self.tooltip = None # Optional: (row id, column name) -> hover text
        self.expand = False # Without one: hovering shows the whole cell (one entry per line for lists)

    def set_rows(self, rows):
        self.beginResetModel()
        self.rows = list(rows)
        self.endResetModel()

    def rowCount(self, parent=QModelIndex()):
        return 0 if parent.isValid() else len(self.rows)

    def columnCount(self, parent=QModelIndex()):
        return len(self.columns)

    def data(self, index, role=Qt.DisplayRole):
        if not index.isValid():
            return None
        value = self.rows[index.row()][1][index.column()]
        column = self.columns[index.column()]
        if column in NUMERIC and isinstance(value, float) and value != value: # Missing (NaN), e.g. a new weapon's gain %
            value = None
        if role == Qt.DisplayRole:
            if value is None and column == 'Gain %':
                return 'new' # Nothing to compare with (no loadout before it)
            if column in NUMERIC and isinstance(value, (int, float)) and column not in PERCENT:
                return f'{value:,.0f}'
            return '' if value is None else str(value)
        if role == Qt.UserRole: # Sorting: numbers as numbers (a missing gain % sorts as the biggest: a new weapon)
            if column in NUMERIC:
                return float('inf') if value is None else float(value) if isinstance(value, (int, float)) else 0.0
            return str(value).lower()
        if role == Qt.ToolTipRole:
            if self.tooltip is not None:
                return self.tooltip(self.rows[index.row()][0], column)
            if self.expand and value not in (None, ''):
                return expanded(value)
        if role == Qt.TextAlignmentRole and column in NUMERIC:
            return int(Qt.AlignRight | Qt.AlignVCenter)
        return None

    def headerData(self, section, orientation, role=Qt.DisplayRole):
        if role == Qt.DisplayRole and orientation == Qt.Horizontal:
            return self.columns[section]
        return None

    def row_id(self, row):
        return self.rows[row][0]


class WordFilter(QSortFilterProxyModel):
    """Rows with every typed word somewhere in their item names"""
    def __init__(self):
        super().__init__()
        self.words = []
        self.setSortRole(Qt.UserRole)

    def set_text(self, text):
        self.words = text.lower().split()
        self.invalidateFilter()

    def filterAcceptsRow(self, row, parent):
        if not self.words:
            return True
        values = [str(v).lower() for v in self.sourceModel().rows[row][1][1:]]
        return all(any(word in v for v in values) for word in self.words)


class ResultsTable(QTableView):
    row_selected = Signal(object) # The selected row's id (None when nothing is selected)

    def __init__(self, columns, widths=None):
        super().__init__()
        self.source = RowsModel(columns)
        self.proxy = WordFilter()
        self.proxy.setSourceModel(self.source)
        self.setModel(self.proxy)
        self.setSortingEnabled(True)
        self.setAlternatingRowColors(True)
        self.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.setSelectionMode(QAbstractItemView.SingleSelection)
        self.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.verticalHeader().setVisible(False)
        header = self.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.Interactive)
        header.setSectionsMovable(True)
        for i, column in enumerate(columns):
            self.setColumnWidth(i, (widths or {}).get(column, 70 if column in NUMERIC else 160))
        self.selectionModel().selectionChanged.connect(lambda *a: self.row_selected.emit(self.selected_id()))
        self.menu_actions = None # Optional: row id -> [(text, callback)] added to the right-click menu
        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self.context_menu)
        copy = QAction(self)
        copy.setShortcut(QKeySequence.Copy)
        copy.triggered.connect(lambda: self.copy_row(readable=True))
        self.addAction(copy)
        self._freeze_first_column()

    # ------------------------------------------------------------ the first column stays put when scrolling sideways

    def _freeze_first_column(self):
        """A second view over the left edge showing only the first column (DPS, Gain %), sharing the model and the
        selection; it scrolls up and down with the table (Qt's frozen column example)"""
        frozen = self.frozen = QTableView(self)
        frozen.setObjectName('FrozenColumn')
        frozen.setModel(self.model())
        frozen.setSelectionModel(self.selectionModel())
        frozen.setFocusPolicy(Qt.NoFocus)
        frozen.verticalHeader().hide()
        frozen.horizontalHeader().setSectionResizeMode(QHeaderView.Fixed)
        frozen.setSelectionBehavior(QAbstractItemView.SelectRows)
        frozen.setEditTriggers(QAbstractItemView.NoEditTriggers)
        frozen.setAlternatingRowColors(True)
        frozen.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        frozen.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        frozen.setVerticalScrollMode(QAbstractItemView.ScrollPerPixel)
        self.setVerticalScrollMode(QAbstractItemView.ScrollPerPixel)
        frozen.setSortingEnabled(True)
        for column in range(1, self.model().columnCount()):
            frozen.setColumnHidden(column, True)
        frozen.setColumnWidth(0, self.columnWidth(0))
        self.viewport().stackUnder(frozen)
        frozen.verticalScrollBar().valueChanged.connect(self.verticalScrollBar().setValue)
        self.verticalScrollBar().valueChanged.connect(frozen.verticalScrollBar().setValue)
        self.horizontalHeader().sectionResized.connect(self._section_resized)
        frozen.setContextMenuPolicy(Qt.CustomContextMenu)
        frozen.customContextMenuRequested.connect(self.context_menu) # Same position: both viewports start at the same point
        # One sort indicator for both headers
        frozen.horizontalHeader().sortIndicatorChanged.connect(self._sync_sort_indicator)
        self.horizontalHeader().sortIndicatorChanged.connect(self._sync_sort_indicator)
        frozen.show()
        self._place_frozen()

    def _sync_sort_indicator(self, section, order):
        for header in (self.horizontalHeader(), self.frozen.horizontalHeader()):
            if (header.sortIndicatorSection(), header.sortIndicatorOrder()) != (section, order):
                header.blockSignals(True); header.setSortIndicator(section, order); header.blockSignals(False)
                header.viewport().update()

    def _section_resized(self, index, old, new):
        if index == 0:
            self.frozen.setColumnWidth(0, new)
            self._place_frozen()

    def _place_frozen(self):
        self.frozen.setGeometry(self.verticalHeader().width() + self.frameWidth(), self.frameWidth(),
                                self.columnWidth(0), self.viewport().height() + self.horizontalHeader().height())

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self._place_frozen()

    def moveCursor(self, action, modifiers):
        current = super().moveCursor(action, modifiers)
        # Keyboard moves to the left: keep the cell clear of the frozen column
        if action == QAbstractItemView.MoveLeft and current.column() > 0 and self.visualRect(current).topLeft().x() < self.frozen.columnWidth(0):
            value = self.horizontalScrollBar().value() + self.visualRect(current).topLeft().x() - self.frozen.columnWidth(0)
            self.horizontalScrollBar().setValue(value)
        return current

    def scrollTo(self, index, hint=QAbstractItemView.EnsureVisible):
        if index.column() > 0:
            super().scrollTo(index, hint)

    def set_rows(self, rows):
        self.source.set_rows(rows)
        for column in range(1, self.model().columnCount()): # A reset can forget hidden columns
            self.frozen.setColumnHidden(column, True)
        self.frozen.setColumnWidth(0, self.columnWidth(0))

    def selected_id(self):
        rows = self.selectionModel().selectedRows()
        return self.source.row_id(self.proxy.mapToSource(rows[0]).row()) if rows else None

    def selected_source_row(self):
        rows = self.selectionModel().selectedRows()
        return self.proxy.mapToSource(rows[0]).row() if rows else None

    def context_menu(self, position):
        index = self.indexAt(position)
        if not index.isValid():
            return
        self.selectRow(index.row())
        menu = QMenu(self)
        menu.addAction('Copy loadout', lambda: self.copy_row(readable=True))
        menu.addAction('Copy row (tab-separated, for spreadsheets)', lambda: self.copy_row(readable=False))
        if self.menu_actions is not None:
            actions = self.menu_actions(self.selected_id())
            if actions:
                menu.addSeparator()
            for text, callback in actions:
                menu.addAction(text, callback)
        menu.exec(self.viewport().mapToGlobal(position))

    def copy_row(self, readable=True):
        row = self.selected_source_row()
        if row is None:
            return
        columns = self.source.columns
        shown = [self.source.data(self.source.index(row, i)) for i in range(len(columns))]
        if readable:
            parts = [f'{c} {v}' for c, v in zip(columns[1:], shown[1:]) if v not in ('', 'None')]
            text = (f'{shown[0]} {columns[0]}: ' if columns[0] == 'DPS' else f'{columns[0]} {shown[0]} | ') + ' | '.join(parts)
        else:
            text = '\t'.join(shown)
        QApplication.clipboard().setText(text)
        window = self.window()
        if hasattr(window, 'statusBar'):
            window.statusBar().showMessage('Copied to the clipboard', 3000)
