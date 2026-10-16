"""Widgets tied to a value in the ConfigStore: editing the widget sets the value; changing the value (anywhere) updates
the widget."""
from PySide6.QtWidgets import QButtonGroup, QCheckBox, QComboBox, QDoubleSpinBox, QHBoxLayout, QLabel, QLineEdit, QPushButton, QSpinBox, QWidget


def _watch(store, path, refresh):
    store.changed.connect(lambda changed: refresh() if changed in ('', path) or path.startswith(changed + '.') or changed.startswith(path + '.') else None)
    refresh()


def checkbox(store, path, text, tooltip=''):
    box = QCheckBox(text)
    box.setToolTip(tooltip)
    def refresh():
        box.blockSignals(True); box.setChecked(bool(store.get(path))); box.blockSignals(False)
    box.toggled.connect(lambda on: store.set(path, bool(on)))
    _watch(store, path, refresh)
    return box


def combo(store, path, values, tooltip=''):
    box = QComboBox()
    box.addItems(values)
    box.setToolTip(tooltip)
    def refresh():
        box.blockSignals(True); box.setCurrentText(str(store.get(path))); box.blockSignals(False)
    box.currentTextChanged.connect(lambda text: store.set(path, text))
    _watch(store, path, refresh)
    return box


def spin(store, path, minimum, maximum, step=1, decimals=0, tooltip='', width=None):
    box = QDoubleSpinBox() if decimals else QSpinBox()
    if decimals: box.setDecimals(decimals)
    box.setRange(minimum, maximum)
    box.setSingleStep(step)
    box.setToolTip(tooltip)
    if width: box.setFixedWidth(width)
    cast = float if decimals else int
    def refresh():
        box.blockSignals(True); box.setValue(cast(store.get(path) or 0)); box.blockSignals(False)
    box.valueChanged.connect(lambda value: store.set(path, cast(value)))
    _watch(store, path, refresh)
    return box


def line(store, path, tooltip=''):
    edit = QLineEdit()
    edit.setToolTip(tooltip)
    def refresh():
        if edit.text() != str(store.get(path) or ''):
            edit.blockSignals(True); edit.setText(str(store.get(path) or '')); edit.blockSignals(False)
    edit.textChanged.connect(lambda text: store.set(path, text))
    _watch(store, path, refresh)
    return edit


def switch(store, path, text, tooltip='', label_width=None):
    """A label and an On | Off switch for a true/false value"""
    widget = QWidget()
    row = QHBoxLayout(widget)
    row.setContentsMargins(0, 0, 0, 0)
    row.setSpacing(0)
    label = QLabel(text)
    if label_width: label.setFixedWidth(label_width)
    row.addWidget(label)
    row.addSpacing(8)
    on, off = QPushButton('On'), QPushButton('Off')
    group = QButtonGroup(widget)
    for button, side in ((on, 'left'), (off, 'right')):
        button.setCheckable(True)
        button.setProperty('segment', side)
        group.addButton(button)
        row.addWidget(button)
    widget.setToolTip(tooltip)
    def refresh(): # Both buttons quiet: checking one unchecks the other, which would signal a change
        on.blockSignals(True); off.blockSignals(True)
        (on if store.get(path) else off).setChecked(True)
        on.blockSignals(False); off.blockSignals(False)
    on.toggled.connect(lambda checked: store.set(path, bool(checked)))
    _watch(store, path, refresh)
    return widget


def setting(store, name, help_text='', label_width=None):
    """A setting from config['settings']: an On | Off switch, or a labeled number box (e.g. fight length in seconds)"""
    value = store.get(f'settings.{name}')
    if isinstance(value, bool) or value is None:
        return switch(store, f'settings.{name}', name, help_text, label_width)
    widget = QWidget()
    row = QHBoxLayout(widget)
    row.setContentsMargins(0, 0, 0, 0)
    label = QLabel(f'{name} (sec)' if name == 'Fight length' else name)
    if label_width: label.setFixedWidth(label_width)
    row.addWidget(label)
    row.addWidget(spin(store, f'settings.{name}', 0, 3600, 5, decimals=1, width=120))
    widget.setToolTip(help_text)
    return widget
