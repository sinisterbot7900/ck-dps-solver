"""The clicked loadout's details: DPS over a fight (chart), the in-game character sheet, and where each stat comes from."""
from PySide6.QtCharts import QChart, QChartView, QLineSeries, QValueAxis
from PySide6.QtCore import QMargins, QPointF, Qt
from PySide6.QtGui import QBrush, QFont, QPainter, QPen
from PySide6.QtWidgets import QHBoxLayout, QHeaderView, QLabel, QTabWidget, QTreeWidget, QTreeWidgetItem, QVBoxLayout, QWidget

from ck_dps_solver.engine import solver
from ck_dps_solver.engine.character_sheet import defense_parts, sheet as character_sheet
from ck_dps_solver.engine.dominance import unused_attributes

from ck_dps_solver.app import labels, theme

EMPTY_TEXT = 'Run a search, then click a loadout to see its DPS over a fight.'


class DpsChart(QWidget):
    """DPS at each moment of a fight, and the average for a fight that long (what the search ranks by)"""
    def __init__(self):
        super().__init__()
        self.data = None
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        self.chart = QChart()
        self.chart.setMargins(QMargins(4, 4, 4, 4))
        self.chart.legend().setAlignment(Qt.AlignBottom)
        self.chart.legend().setFont(QFont('Segoe UI', 9))
        self.chart.setTitleFont(QFont('Segoe UI', 10, QFont.DemiBold))
        self.moment = QLineSeries(name='DPS at that moment')
        self.average = QLineSeries(name='Average for a fight that long')
        self.pinned = QLineSeries(name='Pinned loadout: average') # Comparison (see LoadoutDetails.pin)
        self.pinned_points = None
        self.x_axis, self.y_axis = QValueAxis(), QValueAxis()
        self.x_axis.setLabelFormat('%ds')
        self.x_axis.setTickCount(7)
        self.y_axis.setLabelFormat("%'.0f")
        self.y_axis.setTickCount(5)
        self.chart.addAxis(self.x_axis, Qt.AlignBottom)
        self.chart.addAxis(self.y_axis, Qt.AlignLeft)
        for series in (self.moment, self.average, self.pinned):
            self.chart.addSeries(series)
            series.attachAxis(self.x_axis)
            series.attachAxis(self.y_axis)
        self.view = QChartView(self.chart)
        self.view.setRenderHint(QPainter.Antialiasing)
        self.view.setMinimumHeight(180)
        layout.addWidget(self.view, 1)
        self.notes = QLabel(EMPTY_TEXT)
        self.notes.setProperty('muted', True)
        self.notes.setWordWrap(True)
        self.notes.setFixedWidth(210)
        self.notes.setAlignment(Qt.AlignTop | Qt.AlignLeft)
        layout.addWidget(self.notes)
        self.apply_theme()
        self.show_curve(None)

    def apply_theme(self):
        c = theme.color
        self.chart.setBackgroundBrush(QBrush(c('panel')))
        self.chart.setTitleBrush(QBrush(c('text')))
        self.chart.legend().setLabelColor(c('text'))
        for axis in (self.x_axis, self.y_axis):
            axis.setLabelsFont(QFont('Segoe UI', 9))
            axis.setLabelsColor(c('text_muted'))
            axis.setGridLineColor(c('chart_grid'))
            axis.setLinePen(QPen(c('border')))
        self.moment.setPen(QPen(c('chart_moment'), 2))
        self.average.setPen(QPen(c('chart_average'), 2))
        self.pinned.setPen(QPen(c('text_muted'), 2, Qt.DashLine))
        self.view.setBackgroundBrush(QBrush(c('panel')))
        if hasattr(self, 'data'):
            self.show_curve(self.data) # Re-lays out the axes: labels are measured again with the new font

    def set_pinned(self, points):
        """[(time, average DPS)] of a pinned loadout to draw dashed, or None"""
        self.pinned_points = points
        self.show_curve(self.data)

    def show_curve(self, data):
        """data: (times, average, at_moment, title), or None to clear"""
        self.data = data
        self.pinned.setVisible(self.pinned_points is not None)
        if self.pinned_points is not None:
            self.pinned.replace([QPointF(t, v) for t, v in self.pinned_points])
        if data is None:
            self.moment.clear(); self.average.clear()
            self.chart.setTitle('')
            self.x_axis.setRange(0, labels.CURVE_SECONDS); self.y_axis.setRange(0, 1000)
            self.y_axis.setLabelsVisible(False) # No DPS numbers without a loadout
            self.notes.setText(EMPTY_TEXT)
            return
        times, average, at_moment, title = data
        self.y_axis.setLabelsVisible(True)
        self.moment.replace([QPointF(t, v) for t, v in zip(times, at_moment)])
        self.average.replace([QPointF(t, v) for t, v in zip(times, average)])
        self.chart.setTitle(title)
        self.x_axis.setRange(0, times[-1])
        pinned_top = max((v for _, v in self.pinned_points), default=0) if self.pinned_points else 0
        self.y_axis.setRange(0, max(max(average), max(at_moment), pinned_top) * 1.08 or 1)
        self.notes.setText(f'Start: {at_moment[0]:,.0f}\nAt {times[-1]:g}s: {at_moment[-1]:,.0f}\n'
                           f'{times[-1]:g}s fight average: {average[-1]:,.0f}\n\n'
                           'The average drops when mana runs out and rises once poison lands.')


def _tree(headers, widths):
    tree = QTreeWidget()
    tree.setHeaderLabels(headers)
    tree.setAlternatingRowColors(True)
    tree.setUniformRowHeights(True)
    header = tree.header()
    header.setStretchLastSection(False)
    header.setSectionResizeMode(0, QHeaderView.Stretch)
    for i, width in enumerate(widths[1:], 1): # Values as wide as they need (at least the given width)
        header.setSectionResizeMode(i, QHeaderView.ResizeToContents)
        header.setMinimumSectionSize(min(width, 90))
    tree.headerItem().setTextAlignment(1, Qt.AlignRight | Qt.AlignVCenter)
    return tree


class LoadoutDetails(QWidget):
    """Chart on the left; character sheet and stat sources on the right"""
    def __init__(self):
        super().__init__()
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        self.chart = DpsChart()
        layout.addWidget(self.chart, 3)
        self.tabs = QTabWidget()
        self.sheet = _tree(['Stat (click a loadout)', 'Value'], [230, 150])
        self.breakdown = _tree(['Stat / source', 'Value'], [300, 90])
        self.compare = _tree(['Pinned vs selected', 'Pinned', 'Selected', 'Difference'], [200, 150, 150, 90])
        self.tabs.addTab(self.sheet, 'Character sheet')
        self.tabs.addTab(self.breakdown, 'Where stats come from')
        self.tabs.addTab(self.compare, 'Compare')
        self.tabs.setTabVisible(2, False) # Shown once a loadout is pinned
        self.tabs.setMinimumWidth(420)
        layout.addWidget(self.tabs, 2)
        self.pinned = self.current = None # (loadout, info)

    def apply_theme(self):
        self.chart.apply_theme()
        for tree in (self.sheet, self.breakdown):
            for item in self._items(tree):
                if item.data(0, Qt.UserRole) == 'unused':
                    self._mute(item)

    def clear(self):
        self.chart.show_curve(None)
        self.sheet.clear()
        self.breakdown.clear()
        self.compare.clear()
        self.current = None

    # ------------------------------------------------------------ comparison

    def pin(self, loadout, info):
        """Compare every loadout shown from now on with this one"""
        self.pinned = (loadout, info)
        times, average, _ = solver.dps_over_time(loadout, info['fixed_items'], info['character_kwargs'], labels.CURVE_SECONDS)
        self.chart.set_pinned(list(zip(times, average)))
        self.tabs.setTabVisible(2, True)
        self.show_compare()

    def unpin(self):
        self.pinned = None
        self.chart.set_pinned(None)
        self.tabs.setTabVisible(2, False)
        self.compare.clear()

    @staticmethod
    def _slots(loadout, info):
        """{slot: item name} for a loadout, including the lantern, bag and pet"""
        names = dict(zip(['Weapon', 'Helm', 'Breast armor', 'Pants armor', 'Necklace', 'Ring1', 'Ring2', 'Offhand'],
                         (solver.display_name(i) for i in loadout[1:9])))
        for item in solver.loadout_items(loadout, info['fixed_items'])[8:]:
            names[item.item_category] = solver.display_name(item)
        return names

    def show_compare(self):
        tree = self.compare
        tree.clear()
        if self.pinned is None or self.current is None:
            if self.pinned is not None:
                QTreeWidgetItem(tree, ['Click a loadout to compare it with the pinned one']).setFirstColumnSpanned(True)
            return
        (a, info_a), (b, info_b) = self.pinned, self.current
        def row(parent, label, left, right, diff=''):
            item = QTreeWidgetItem(parent, [label, str(left), str(right), diff])
            for column in (1, 2, 3):
                item.setTextAlignment(column, Qt.AlignRight | Qt.AlignVCenter)
            return item
        row(tree, 'DPS', f'{a[0]:,}', f'{b[0]:,}', f'{b[0] - a[0]:+,}')
        slots_a, slots_b = self._slots(a, info_a), self._slots(b, info_b)
        items = QTreeWidgetItem(tree, ['Items']); items.setFirstColumnSpanned(True)
        for slot in ['Weapon', 'Helm', 'Breast armor', 'Pants armor', 'Necklace', 'Ring1', 'Ring2', 'Offhand', 'Lantern', 'Bag', 'Pet']:
            left, right = slots_a.get(slot, 'None'), slots_b.get(slot, 'None')
            entry = row(items, slot, left, right, '' if left == right else 'changed')
            if left == right: # Unchanged: dimmed
                for column in range(4):
                    entry.setForeground(column, QBrush(theme.color('text_muted')))
        stats = QTreeWidgetItem(tree, ['Stats']); stats.setFirstColumnSpanned(True)
        totals = lambda loadout, info: {attribute: total for attribute, total, _ in solver.loadout_breakdown(loadout, info['fixed_items'], info['character_kwargs'])[0]}
        ta, tb = totals(a, info_a), totals(b, info_b)
        show = lambda attribute, value: f'{value * 100:.3g}%' if attribute.startswith('%_') else f'{value:g}'
        for attribute in [k for k in dict.fromkeys(list(ta) + list(tb))]:
            left, right = ta.get(attribute, 0), tb.get(attribute, 0)
            if abs(left - right) > 1e-9:
                diff = right - left
                row(stats, attribute, show(attribute, left), show(attribute, right), ('+' if diff > 0 else '-') + show(attribute, abs(diff)))
        tree.expandAll()

    def show_loadout(self, loadout, info):
        self.current = (loadout, info)
        times, average, at_moment = solver.dps_over_time(loadout, info['fixed_items'], info['character_kwargs'], labels.CURVE_SECONDS)
        self.chart.show_curve((times, average, at_moment, f'{solver.display_name(loadout[1])}: {loadout[0]:,} DPS in the search'))
        self.show_sheet(loadout, info)
        self.show_breakdown(loadout, info)
        self.show_compare()

    def show_sheet(self, loadout, info):
        """The loadout's stats as the game's character screen shows them"""
        self.sheet.clear()
        rows = character_sheet(loadout, info['fixed_items'], info['character_kwargs'], info.get('consumable_keys', ()),
                               info.get('dish_rarity', 'Rare'), info.get('golden_ingredients', True))
        groups = {}
        for group, label, value in rows:
            if group not in groups:
                groups[group] = QTreeWidgetItem(self.sheet, [group])
                groups[group].setFirstColumnSpanned(True)
                font = groups[group].font(0); font.setBold(True); groups[group].setFont(0, font)
            item = QTreeWidgetItem(groups[group], [label, str(value)])
            item.setTextAlignment(1, Qt.AlignRight | Qt.AlignVCenter)
        self.sheet.expandAll()

    def show_breakdown(self, loadout, info):
        """Each stat with its sources (items, sets, talents, food) as child rows; stats this weapon doesn't use are grayed"""
        self.breakdown.clear()
        rows, set_counts = solver.loadout_breakdown(loadout, info['fixed_items'], info['character_kwargs'])
        unused = set(unused_attributes(loadout[1].damage_type))
        show = lambda attribute, value: f'{value * 100:.3g}%' if attribute.startswith('%_') else f'{value:g}'
        for attribute, total, sources in rows:
            parent = QTreeWidgetItem(self.breakdown, [attribute + (' (not used by this weapon)' if attribute in unused else ''), show(attribute, total)])
            parent.setTextAlignment(1, Qt.AlignRight | Qt.AlignVCenter)
            for source, value in sources:
                child = QTreeWidgetItem(parent, [source, show(attribute, value)])
                child.setTextAlignment(1, Qt.AlignRight | Qt.AlignVCenter)
            if attribute in unused:
                for item in (parent, *(parent.child(i) for i in range(parent.childCount()))):
                    item.setData(0, Qt.UserRole, 'unused')
                    self._mute(item)
        # Stats only the character sheet shows (armor, dodge...): from the items' wiki data, not the DPS formula
        labels_ = {'armor': 'Armor', 'armor_pct': 'Armor %', 'dodge': 'Dodge chance', 'movement': 'Movement speed', 'regen': 'Health regeneration /s',
                   'life_on_hit': 'Life on melee hit', 'boss_reduction': 'Damage taken from bosses (reduction)', 'regen_effectiveness': 'Health regeneration effectiveness'}
        percent = {'armor_pct', 'dodge', 'movement', 'boss_reduction', 'regen_effectiveness'}
        parts = defense_parts(loadout, info['fixed_items'], info['character_kwargs'], info.get('consumable_keys', ()),
                              info.get('dish_rarity', 'Rare'), info.get('golden_ingredients', True))
        for stat, entries in parts.items():
            fmt = (lambda v: f'{v * 100:.3g}%') if stat in percent else (lambda v: f'{v:.3g}')
            parent = QTreeWidgetItem(self.breakdown, [labels_.get(stat, stat), fmt(sum(v for _, v in entries))])
            parent.setTextAlignment(1, Qt.AlignRight | Qt.AlignVCenter)
            for source, value in entries:
                child = QTreeWidgetItem(parent, [source, fmt(value)])
                child.setTextAlignment(1, Qt.AlignRight | Qt.AlignVCenter)
        sets = ', '.join(f'{name} {n}' for name, n in sorted(set_counts.items()))
        if sets:
            QTreeWidgetItem(self.breakdown, [f'Set pieces: {sets}', '']).setFirstColumnSpanned(True)

    @staticmethod
    def _mute(item):
        for column in (0, 1):
            item.setForeground(column, QBrush(theme.color('text_muted')))

    @staticmethod
    def _items(tree):
        stack = [tree.topLevelItem(i) for i in range(tree.topLevelItemCount())]
        while stack:
            item = stack.pop()
            yield item
            stack.extend(item.child(i) for i in range(item.childCount()))
