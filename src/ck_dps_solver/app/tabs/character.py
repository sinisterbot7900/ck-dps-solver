"""Character tab: a card per skill (icon, level, a tiny view of its talent tree); clicking one shows its talent tree
below, where points are spent by the game's rules (model/talents.py). The Load button on the Items tab fills these
from a save."""
import json
import os

from PySide6.QtCore import QPointF, QRectF, QSize, Qt, Signal
from PySide6.QtGui import QColor, QFont, QPainter, QPen, QPixmap
from PySide6.QtWidgets import QFrame, QGridLayout, QHBoxLayout, QLabel, QPushButton, QSizePolicy, QSpinBox, QVBoxLayout, QWidget

from ck_dps_solver import defaults, paths
from ck_dps_solver.model import Character, talents
from ck_dps_solver.model.item_stats import wiki_data

from ck_dps_solver.app import theme

DAMAGE_TYPE_SKILL = {'Melee': 'Melee', 'Range': 'Range', 'Magic': 'Magic', 'Summoning': 'Summoning'}


def perk_names():
    """Talent names per skill, in talent tree order (as used by Character)"""
    character = Character(defaults.skill_levels, defaults.perk_trees)
    return {skill: list(perks) for skill, perks in character.perks.items()}


def _manifest():
    path = paths.resource('data', 'icons', 'manifest.json')
    if not os.path.exists(path):
        return {}
    with open(path, encoding='utf8') as f:
        return json.load(f)['skills']


def _icon(file, size):
    """A pixel art icon scaled without smoothing (stays crisp)"""
    if not file:
        return QPixmap()
    pixmap = QPixmap(paths.resource('data', 'icons', file))
    return pixmap.scaled(size, size, Qt.KeepAspectRatio, Qt.FastTransformation) if not pixmap.isNull() else pixmap


def skill_color(skill):
    return QColor(wiki_data()['skills'][skill].get('iconColor') or theme.color('primary').name())


class MiniTree(QWidget):
    """A skill's talent tree in miniature: a dot per talent (tiers 1/2/3/2), filled by its points"""
    def __init__(self, skill):
        super().__init__()
        self.skill, self.points = skill, [0] * 8
        self.tiers = talents.tree(skill)
        self.setFixedSize(64, 46)

    def set_points(self, points):
        self.points = list(points)
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        color, empty = skill_color(self.skill), theme.color('border')
        rows = len(self.tiers)
        for t, tier in enumerate(self.tiers):
            y = 6 + t * (self.height() - 12) / max(rows - 1, 1)
            for k, (i, _) in enumerate(tier):
                x = self.width() / 2 + (k - (len(tier) - 1) / 2) * 17
                points = self.points[i] if i < len(self.points) else 0
                painter.setPen(QPen(color if points else empty, 1.4))
                painter.setBrush(Qt.NoBrush)
                painter.drawEllipse(QPointF(x, y), 5, 5)
                if points:
                    painter.setPen(Qt.NoPen)
                    painter.setBrush(color)
                    if points >= talents.MAX_POINTS:
                        painter.drawEllipse(QPointF(x, y), 5, 5)
                    else: # A pie slice: the share of 5 points
                        painter.drawPie(QRectF(x - 5, y - 5, 10, 10), 90 * 16, -int(360 * 16 * points / talents.MAX_POINTS))


class SkillCard(QFrame):
    clicked = Signal(str)

    def __init__(self, skill, name, icon):
        super().__init__()
        self.skill = skill
        self.setObjectName('Card')
        self.setCursor(Qt.PointingHandCursor)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        row = QHBoxLayout(self)
        row.setContentsMargins(10, 8, 10, 8)
        picture = QLabel()
        picture.setPixmap(_icon(icon, 32))
        picture.setFixedSize(34, 34)
        row.addWidget(picture)
        text = QVBoxLayout()
        text.setSpacing(0)
        self.name = QLabel(name)
        font = self.name.font(); font.setBold(True); self.name.setFont(font)
        self.level = QLabel()
        self.level.setProperty('muted', True)
        text.addWidget(self.name)
        text.addWidget(self.level)
        row.addLayout(text, 1)
        self.mini = MiniTree(skill)
        row.addWidget(self.mini)
        self.set_selected(False)

    def set_selected(self, selected):
        width = 2 if selected else 1
        color = skill_color(self.skill).name() if selected else theme.color('border').name()
        self.setStyleSheet(f'QFrame#Card {{ border: {width}px solid {color}; }}')

    def mousePressEvent(self, event):
        self.clicked.emit(self.skill)


class TalentNode(QWidget):
    """A talent: its icon and points; left click adds a point, right click removes one"""
    add = Signal(int)
    remove = Signal(int)
    SIZE = 64

    def __init__(self, skill, index, name, icon):
        super().__init__()
        self.skill, self.index, self.name = skill, index, name
        self.pixmap = _icon(icon, 48)
        self.points, self.can_add, self.locked = 0, True, False
        self.setFixedSize(QSize(150, self.SIZE + 40))
        self.setCursor(Qt.PointingHandCursor)

    def set_state(self, points, add_reason, locked):
        self.points, self.can_add, self.locked = points, add_reason is None, locked
        tip = f'<b>{self.name}</b><br>{points} / {talents.MAX_POINTS} points<br>Left click: add a point · right click: remove one'
        if add_reason and points < talents.MAX_POINTS:
            tip += f'<br><span style="color:{theme.color("text_muted").name()}">{add_reason}</span>'
        self.setToolTip(tip)
        self.update()

    def box(self):
        return QRectF((self.width() - self.SIZE) / 2, 2, self.SIZE, self.SIZE)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        color = skill_color(self.skill)
        box = self.box()
        if self.locked:
            painter.setOpacity(0.35)
        painter.setPen(QPen(color if self.points else theme.color('border'), 2 if self.points >= talents.MAX_POINTS else 1.2))
        painter.setBrush(theme.color('panel_alt'))
        painter.drawRoundedRect(box, 8, 8)
        if not self.pixmap.isNull():
            painter.drawPixmap(int(box.center().x() - self.pixmap.width() / 2), int(box.center().y() - self.pixmap.height() / 2), self.pixmap)
        # Points: five pips under the icon
        for k in range(talents.MAX_POINTS):
            x = box.center().x() + (k - 2) * 11
            painter.setPen(Qt.NoPen)
            painter.setBrush(color if k < self.points else theme.color('border'))
            painter.drawEllipse(QPointF(x, box.bottom() + 8), 3.2, 3.2)
        painter.setPen(theme.color('text') if not self.locked else theme.color('text_muted'))
        font = QFont('Segoe UI', 9)
        painter.setFont(font)
        painter.drawText(QRectF(0, box.bottom() + 14, self.width(), 24), Qt.AlignHCenter | Qt.AlignTop | Qt.TextWordWrap, self.name)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.add.emit(self.index)
        elif event.button() == Qt.RightButton:
            self.remove.emit(self.index)


class TreeView(QWidget):
    """A skill's talents, tier by tier, joined by lines from each tier to the next"""
    add = Signal(int)
    remove = Signal(int)

    def __init__(self, skill, icons):
        super().__init__()
        self.skill = skill
        self.tiers = talents.tree(skill)
        self.nodes = {}
        column = QVBoxLayout(self)
        column.setSpacing(14)
        for tier in self.tiers:
            row = QHBoxLayout()
            row.addStretch()
            for i, name in tier:
                node = TalentNode(skill, i, name, icons[i] if i < len(icons) else None)
                node.add.connect(self.add)
                node.remove.connect(self.remove)
                self.nodes[i] = node
                row.addWidget(node)
                row.addSpacing(24)
            row.addStretch()
            column.addLayout(row)
        column.addStretch()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        color = skill_color(self.skill)
        for i, j in talents.links(self.skill): # Each talent's links to the tier below; lit when it opens the one below
            a, b = self.nodes[i], self.nodes[j]
            start = a.mapTo(self, a.box().center().toPoint())
            start.setY(int(a.mapTo(self, a.box().bottomLeft().toPoint()).y()) + 14)
            end = b.mapTo(self, b.box().topLeft().toPoint())
            end.setX(int(b.mapTo(self, b.box().center().toPoint()).x()))
            lit = a.points >= talents.MAX_POINTS and not a.locked
            painter.setPen(QPen(QColor(color) if lit else theme.color('border'), 2 if lit else 1.4))
            painter.drawLine(start, end)


class CharacterTab(QWidget):
    def __init__(self, store, log):
        super().__init__()
        self.store, self.log = store, log
        self.icons = _manifest()
        self.skills = list(store.get('skill_levels'))
        outer = QVBoxLayout(self)

        # Skill cards
        grid = QGridLayout()
        grid.setSpacing(8)
        self.cards = {}
        for n, skill in enumerate(self.skills):
            entry = self.icons.get(skill, {})
            card = SkillCard(skill, wiki_data()['skills'][skill]['displayName'], entry.get('icon'))
            card.clicked.connect(self.select)
            self.cards[skill] = card
            grid.addWidget(card, n // 6, n % 6)
        outer.addLayout(grid)

        # The selected skill's tree
        self.panel = QFrame()
        self.panel.setObjectName('Card')
        panel = QVBoxLayout(self.panel)
        header = QHBoxLayout()
        self.title_icon = QLabel()
        header.addWidget(self.title_icon)
        self.title = QLabel()
        font = self.title.font(); font.setBold(True); font.setPointSize(13); self.title.setFont(font)
        header.addWidget(self.title)
        header.addSpacing(16)
        header.addWidget(QLabel('Level'))
        self.level_box = QSpinBox()
        self.level_box.setRange(0, 100)
        self.level_box.setFixedWidth(100)
        self.level_box.valueChanged.connect(self.level_changed)
        header.addWidget(self.level_box)
        header.addSpacing(12)
        self.points_left = QLabel() # Points still to spend at this level
        header.addWidget(self.points_left)
        header.addStretch()
        clear = QPushButton('Clear')
        clear.setToolTip('Level 0 and no talent points')
        clear.clicked.connect(lambda: self.clear_skill(self.selected))
        reset = QPushButton('Defaults')
        reset.setToolTip("This skill's default level and talents")
        reset.clicked.connect(lambda: self.default_skill(self.selected))
        header.addWidget(clear)
        header.addWidget(reset)
        panel.addLayout(header)
        self.trees = {}
        for skill in self.skills:
            view = TreeView(skill, [t['icon'] for t in self.icons.get(skill, {}).get('talents', [])])
            view.add.connect(lambda i, s=skill: self.change(s, i, +1))
            view.remove.connect(lambda i, s=skill: self.change(s, i, -1))
            view.hide()
            panel.addWidget(view, 1)
            self.trees[skill] = view
        outer.addWidget(self.panel, 1)

        self.selected = None
        self.damage_type = store.get('damage_type')
        store.changed.connect(lambda path: self.refresh() if path == '' or path.startswith(('skill_levels', 'perk_trees', 'damage_type')) else None)
        store.changed.connect(self.damage_type_changed)
        self.select(DAMAGE_TYPE_SKILL.get(store.get('damage_type'), self.skills[0]))

    # ------------------------------------------------------------ store

    def points(self, skill):
        return list(self.store.get(f'perk_trees.{skill}') or [0] * 8)

    def level(self, skill):
        return int(self.store.get(f'skill_levels.{skill}') or 0)

    def set_points(self, skill, points):
        self.store.set(f'perk_trees.{skill}', [int(p) for p in points])

    # ------------------------------------------------------------ actions

    def select(self, skill):
        if skill not in self.cards:
            return
        if self.selected:
            self.cards[self.selected].set_selected(False)
            self.trees[self.selected].hide()
        self.selected = skill
        self.cards[skill].set_selected(True)
        self.trees[skill].show()
        self.title.setText(wiki_data()['skills'][skill]['displayName'])
        self.title.setStyleSheet(f'color: {skill_color(skill).name()};')
        self.title_icon.setPixmap(_icon(self.icons.get(skill, {}).get('icon'), 32))
        self.refresh()

    def change(self, skill, index, step):
        points = self.points(skill)
        level = self.level(skill)
        if step > 0 and talents.why_not_add(skill, level, points, index) is None:
            points[index] += 1
        elif step < 0 and talents.why_not_remove(skill, level, points, index) is None:
            points[index] -= 1
        else:
            return
        self.set_points(skill, points)

    def level_changed(self, value):
        skill = self.selected
        self.store.set(f'skill_levels.{skill}', int(value))
        fitted = talents.fit_to_level(skill, int(value), self.points(skill)) # A lower level gives fewer points
        if fitted != self.points(skill):
            self.set_points(skill, fitted)

    def clear_skill(self, skill):
        """Reset a skill to level 0 and no talent points"""
        self.store.set(f'skill_levels.{skill}', 0)
        self.set_points(skill, [0] * len(self.points(skill)))

    def default_skill(self, skill, log=True):
        """A skill's level and talents from defaults.py (skill_levels, and the damage type's perk_trees_for)"""
        level = defaults.skill_levels.get(skill, 0)
        self.store.set(f'skill_levels.{skill}', level)
        tree = defaults.perk_trees_for(self.store.get('damage_type')).get(skill, [0] * 8)
        self.set_points(skill, talents.fit_to_level(skill, level, tree))
        if log:
            self.log(f'{skill}: level and talents set to the defaults')

    def damage_type_changed(self, path):
        """Talents still at the old damage type's defaults follow to the new one's (defaults.PERK_TREES_FOR); talents you
        set or loaded from a save stay"""
        if path not in ('', 'damage_type'):
            return
        old, new = self.damage_type, self.store.get('damage_type')
        self.damage_type = new
        if path == '' or old == new:
            return
        before, after = defaults.perk_trees_for(old), defaults.perk_trees_for(new)
        moved = [skill for skill in after if after[skill] != before.get(skill) and self.points(skill) == before.get(skill)
                 and talents.is_legal(skill, self.level(skill), after[skill])]
        for skill in moved:
            self.set_points(skill, after[skill])
        if moved:
            self.log(f"{', '.join(moved)}: talents set to the {new} defaults")

    def defaults(self):
        """Every skill to its default level and the damage type's best talents"""
        for skill in self.skills:
            self.default_skill(skill, log=False)
        self.log(f"All skills set to the defaults: level 100 and the best talents for {self.store.get('damage_type')}")

    # ------------------------------------------------------------ show

    def apply_theme(self):
        """Card borders and the trees are drawn with the theme's colors: redo them"""
        for skill, card in self.cards.items():
            card.set_selected(skill == self.selected)
        for view in self.trees.values():
            view.update()

    def refresh(self):
        for skill, card in self.cards.items():
            card.level.setText(f'Level {self.level(skill)}')
            card.mini.set_points(self.points(skill))
        skill = self.selected
        if skill is None:
            return
        self.level_box.blockSignals(True); self.level_box.setValue(self.level(skill)); self.level_box.blockSignals(False)
        points, level = self.points(skill), self.level(skill)
        left = talents.available(skill, level) - sum(points)
        self.points_left.setText(f"{left} point{'' if left == 1 else 's'} available" if left > 0 else '') # Nothing to say when all are spent
        opened = talents.unlocked(skill, points)
        view = self.trees[skill]
        for i, node in view.nodes.items():
            node.set_state(points[i], talents.why_not_add(skill, level, points, i), i not in opened)
        view.update()
