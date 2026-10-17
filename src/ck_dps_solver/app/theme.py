"""Colors of the app, in one place. Each theme is a table of named colors; the stylesheet is built from it.

To change the look, edit the hex values below (or add a theme: copy one and rename it). Widgets never hard-code colors:
they use these names, through the stylesheet or color(name).
"""
import os
import tempfile

from PySide6.QtGui import QColor, QPalette

THEMES = {
    # Sunset: purple and orange on light panels
    'Sunset light': {
        'window': '#f4eff9',        # Behind everything
        'panel': '#ffffff',         # Cards, tables, inputs
        'panel_alt': '#f8f3fc',     # Alternate table rows
        'header': '#4a2470',        # Title bar and tab bar background
        'header_text': '#ffffff',
        'tab': '#6a3a9c',           # Unselected tabs
        'text': '#2b1a3d',
        'text_muted': '#7d6b91',
        'border': '#dcd0ea',
        'primary': '#7b3fc4',       # Buttons, selected tab, selection
        'primary_hover': '#8e55d6',
        'primary_text': '#ffffff',
        'accent': '#f26b1d',        # Run, progress, highlights
        'accent_hover': '#ff8436',
        'accent_text': '#ffffff',
        'selection': '#e6d6f7',     # Selected table rows
        'success': '#1f9d55',
        'error': '#c53030',
        'chart_moment': '#7b3fc4',  # DPS curve: at that moment
        'chart_average': '#f26b1d', # DPS curve: average for a fight that long
        'chart_grid': '#ece4f4',
    },
    'Sunset dark': {
        'window': '#1e1229',
        'panel': '#2a1a3a',
        'panel_alt': '#311f44',
        'header': '#150b1f',
        'header_text': '#f6ecff',
        'tab': '#3d2556',
        'text': '#efe6f8',
        'text_muted': '#a993c0',
        'border': '#47305f',
        'primary': '#9a5be0',
        'primary_hover': '#ae74ec',
        'primary_text': '#ffffff',
        'accent': '#ff7a2b',
        'accent_hover': '#ff9450',
        'accent_text': '#1e1229',
        'selection': '#4b2d6e',
        'success': '#4ade80',
        'error': '#f87171',
        'chart_moment': '#b58cf0',
        'chart_average': '#ff8a3d',
        'chart_grid': '#3a2850',
    },
    # Sunset red ("Sunset Sky" palette): Redbox #92332D, Berry Crush #A96775, Tilted Pinball #EC5120,
    # Grape Soda #AC94A5, Baby Jane #CEA3A4
    'Sunset red light': {
        'window': '#f7eeee',
        'panel': '#ffffff',
        'panel_alt': '#fbf4f4',
        'header': '#92332d',
        'header_text': '#ffffff',
        'tab': '#a96775',
        'text': '#3a1f24',
        'text_muted': '#8a6f7e',
        'border': '#e3cfd0',
        'primary': '#96505f',
        'primary_hover': '#a96775',
        'primary_text': '#ffffff',
        'accent': '#ec5120',
        'accent_hover': '#f26a3d',
        'accent_text': '#ffffff',
        'selection': '#efd9da',
        'success': '#1f9d55',
        'error': '#b91c1c',
        'chart_moment': '#92332d',
        'chart_average': '#ec5120',
        'chart_grid': '#f0e2e2',
    },
    'Sunset red dark': {
        'window': '#1f1316',
        'panel': '#2b1b1f',
        'panel_alt': '#332126',
        'header': '#170d10',
        'header_text': '#f8ecec',
        'tab': '#4a2a31',
        'text': '#f3e6e7',
        'text_muted': '#ac94a5',
        'border': '#553339',
        'primary': '#a96775',
        'primary_hover': '#bd7e8b',
        'primary_text': '#ffffff',
        'accent': '#ec5120',
        'accent_hover': '#f26c40',
        'accent_text': '#1f1316',
        'selection': '#5a2f36',
        'success': '#4ade80',
        'error': '#f87171',
        'chart_moment': '#cea3a4',
        'chart_average': '#ec5120',
        'chart_grid': '#3d272c',
    },
    # Combat styles: main color (buttons, tabs, selection), accent (Run, progress, header line), special (header text, DPS line)
    'Melee': { # Orange main, yellow accent, white special; orange-tinted backgrounds
        'window': '#241307', 'panel': '#33190a', 'panel_alt': '#3c1f0e', 'header': '#1c0e05', 'header_text': '#ffffff', 'tab': '#4d2810',
        'text': '#fff4ea', 'text_muted': '#c99a76', 'border': '#6a3815',
        'primary': '#ff8a35', 'primary_hover': '#ffa15c', 'primary_text': '#1a0f06',
        'accent': '#ffd23f', 'accent_hover': '#ffdd6b', 'accent_text': '#1a1405',
        'selection': '#7a3a10', 'success': '#4ade80', 'error': '#f87171',
        'chart_moment': '#ffffff', 'chart_average': '#ffd23f', 'chart_grid': '#4a2610', 'special': '#ffffff',
    },
    'Range': { # Forest greens; brown only for the Run button and the line under the header
        'window': '#0f1a12', 'panel': '#15241a', 'panel_alt': '#1a2c20', 'header': '#0b1a0f', 'header_text': '#ffffff', 'tab': '#1f3a26',
        'text': '#eef5ee', 'text_muted': '#93ad97', 'border': '#2c4a33',
        'primary': '#3a8a50', 'primary_hover': '#47a05f', 'primary_text': '#ffffff',
        'accent': '#8b5a2b', 'accent_hover': '#a06a35', 'accent_text': '#fff3e6', 'progress': '#4f9e63',
        'selection': '#24452e', 'success': '#6fbf7f', 'error': '#f87171',
        'chart_moment': '#ffffff', 'chart_average': '#6fbf7f', 'chart_grid': '#22382a', 'special': '#ffffff',
    },
    'Magic': { # Blue main, light blue accent, light grey special
        'window': '#0c1420', 'panel': '#121d2c', 'panel_alt': '#172435', 'header': '#080e17', 'header_text': '#d6dbe2', 'tab': '#1a2c44',
        'text': '#e9f0f8', 'text_muted': '#8ea3bb', 'border': '#243a56',
        'primary': '#198de6', 'primary_hover': '#3ea2ee', 'primary_text': '#ffffff',
        'accent': '#8fd3ff', 'accent_hover': '#b0e0ff', 'accent_text': '#04213a',
        'selection': '#153f66', 'success': '#8ff0a4', 'error': '#f87171',
        'chart_moment': '#d6dbe2', 'chart_average': '#8fd3ff', 'chart_grid': '#20324a', 'special': '#d6dbe2',
    },
    'Summoning': { # Purple main, pink accent, light grey special
        'window': '#170f1c', 'panel': '#211628', 'panel_alt': '#281a31', 'header': '#100a14', 'header_text': '#d6d3dc', 'tab': '#352242',
        'text': '#f1ebf5', 'text_muted': '#a898b5', 'border': '#45305a',
        'primary': '#ba4ddb', 'primary_hover': '#c96ae3', 'primary_text': '#ffffff',
        'accent': '#ff6fb5', 'accent_hover': '#ff8fc5', 'accent_text': '#2a0718',
        'selection': '#4d2a5e', 'success': '#4ade80', 'error': '#f87171',
        'chart_moment': '#d6d3dc', 'chart_average': '#ff6fb5', 'chart_grid': '#35243f', 'special': '#d6d3dc',
    },
}
DEFAULT_THEME = 'Sunset dark'
DYNAMIC = 'Dynamic' # Theme choice: the damage type's theme (fades into it when the damage type changes)

_current = dict(THEMES[DEFAULT_THEME])


def color(name):
    """A color of the current theme, for widgets that draw themselves (e.g. the DPS chart)"""
    return QColor(_current[name])


def special_color():
    """The theme's special color (combat themes: white or light grey), for notes that should stand out; others: accent"""
    return QColor(_current.get('special', _current['accent']))


def progress_color():
    """The progress bar's fill (some themes give it its own color)"""
    return QColor(_current.get('progress', _current['accent']))


def readable_on(background):
    """Black or white, whichever reads better on a color"""
    luminance = 0.299 * background.red() + 0.587 * background.green() + 0.114 * background.blue()
    return QColor('#000000') if luminance > 150 else QColor('#ffffff')


def _check_image(color):
    """A checkmark (SVG file) in a color, for checked checkboxes (styled indicators don't draw Qt's own)"""
    folder = os.path.join(tempfile.gettempdir(), 'ck-dps-solver-theme')
    os.makedirs(folder, exist_ok=True)
    path = os.path.join(folder, f'check_{color.lstrip("#")}.svg')
    if not os.path.exists(path):
        with open(path, 'w', encoding='utf8') as f:
            f.write(f'<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 16 16"><path d="M3.5 8.5l3 3 6-7" '
                    f'fill="none" stroke="{color}" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"/></svg>')
    return path.replace(os.sep, '/')


def stylesheet(c):
    """The app's stylesheet from a theme's colors"""
    check = _check_image(c['primary_text'])
    return f"""
    QWidget {{ color: {c['text']}; font-family: 'Segoe UI', 'Arial'; font-size: 10pt; }}
    QMainWindow, QDialog {{ background: {c['window']}; }}
    QLabel#Title {{ color: {c['header_text']}; font-size: 15pt; font-weight: 600; }}
    QLabel#Subtitle {{ color: {c['header_text']}; }}
    QFrame#Header {{ background: {c['header']}; border: none; border-bottom: 3px solid {c['accent']}; }}
    QLabel[muted="true"] {{ color: {c['text_muted']}; }}
    QLabel[status="good"] {{ color: {c['success']}; font-weight: 600; }}
    QLabel[status="bad"] {{ color: {c['error']}; font-weight: 600; }}

    QTabWidget::pane {{ border: 1px solid {c['border']}; background: {c['window']}; top: -1px; }}
    QTabBar::tab {{ background: {c['tab']}; color: {c['header_text']}; padding: 8px 18px; border: none; margin-right: 2px;
                    border-top-left-radius: 6px; border-top-right-radius: 6px; }}
    QTabBar::tab:selected {{ background: {c['primary']}; color: {c['primary_text']}; }}
    QTabBar::tab:hover:!selected {{ background: {c['primary_hover']}; }}

    QGroupBox {{ background: {c['panel']}; border: 1px solid {c['border']}; border-radius: 8px; margin-top: 14px; padding: 10px; }}
    QGroupBox::title {{ subcontrol-origin: margin; left: 10px; padding: 0 4px; color: {c['primary']}; font-weight: 600; }}

    QPushButton {{ background: {c['primary']}; color: {c['primary_text']}; border: none; border-radius: 6px; padding: 6px 14px; }}
    QPushButton:hover {{ background: {c['primary_hover']}; }}
    QPushButton:disabled {{ background: {c['border']}; color: {c['text_muted']}; }}
    QPushButton[accent="true"] {{ background: {c['accent']}; color: {c['accent_text']}; font-weight: 600; }}
    QPushButton[accent="true"]:hover {{ background: {c['accent_hover']}; }}
    QPushButton[flat="true"] {{ background: transparent; color: {c['header_text']}; border: 1px solid {c['header_text']}; }}
    QPushButton[segment="left"], QPushButton[segment="right"], QPushButton[toggle="true"] {{ background: transparent; color: {c['text']}; border: 1px solid {c['primary']}; }}
    QPushButton[segment="left"]:hover, QPushButton[segment="right"]:hover, QPushButton[toggle="true"]:hover {{ background: {c['selection']}; }}
    QPushButton[segment="left"]:checked, QPushButton[segment="right"]:checked, QPushButton[toggle="true"]:checked {{ background: {c['primary']}; color: {c['primary_text']}; }}
    QPushButton[segment="left"] {{ border-top-right-radius: 0; border-bottom-right-radius: 0; padding: 3px 12px; }}
    QPushButton[segment="right"] {{ border-top-left-radius: 0; border-bottom-left-radius: 0; border-left: none; padding: 3px 12px; }}
    QFrame#Card {{ background: {c['panel_alt']}; border: 1px solid {c['border']}; border-radius: 8px; }}
    QFrame#Card QLabel {{ background: transparent; }}

    QLineEdit, QSpinBox, QDoubleSpinBox, QComboBox {{ background: {c['panel']}; border: 1px solid {c['border']}; border-radius: 5px;
                                                     padding: 4px 6px; selection-background-color: {c['primary']}; }}
    QLineEdit:focus, QSpinBox:focus, QDoubleSpinBox:focus, QComboBox:focus {{ border: 1px solid {c['primary']}; }}
    QComboBox QAbstractItemView {{ background: {c['panel']}; selection-background-color: {c['selection']}; selection-color: {c['text']}; }}
    QCheckBox, QRadioButton {{ spacing: 6px; }}
    QCheckBox::indicator, QTreeView::indicator {{ width: 14px; height: 14px; border: 1px solid {c['text_muted']}; border-radius: 3px; background: {c['panel']}; }}
    QCheckBox::indicator:hover, QTreeView::indicator:hover {{ border: 1px solid {c['primary']}; }}
    QCheckBox::indicator:checked, QTreeView::indicator:checked {{ background: {c['primary']}; border: 1px solid {c['primary']}; image: url({check}); }}
    QCheckBox::indicator:disabled, QTreeView::indicator:disabled {{ border: 1px solid {c['border']}; background: {c['panel_alt']}; }}
    QCheckBox::indicator:checked:disabled, QTreeView::indicator:checked:disabled {{ background: {c['border']}; }}
    QRadioButton::indicator {{ width: 14px; height: 14px; border: 1px solid {c['text_muted']}; border-radius: 8px; background: {c['panel']}; }}
    QRadioButton::indicator:hover {{ border: 1px solid {c['primary']}; }}
    QRadioButton::indicator:checked {{ border: 1px solid {c['primary']};
        background: qradialgradient(cx:0.5, cy:0.5, radius:0.5, fx:0.5, fy:0.5, stop:0 {c['primary']}, stop:0.5 {c['primary']}, stop:0.6 {c['panel']}, stop:1 {c['panel']}); }}
    QCheckBox:disabled, QRadioButton:disabled, QLabel:disabled {{ color: {c['text_muted']}; }}

    QTableView, QTreeView, QListWidget, QTextEdit, QPlainTextEdit {{ background: {c['panel']}; alternate-background-color: {c['panel_alt']};
        border: 1px solid {c['border']}; border-radius: 6px; selection-background-color: {c['selection']}; selection-color: {c['text']}; }}
    QTableView#FrozenColumn {{ border: none; border-right: 2px solid {c['border']}; }}
    QHeaderView::section {{ background: {c['header']}; color: {c['header_text']}; padding: 5px 8px; border: none; border-right: 1px solid {c['primary']}; }}

    QProgressBar {{ background: {c['panel']}; border: 1px solid {c['border']}; border-radius: 6px; text-align: center; height: 18px; }}
    QProgressBar::chunk {{ background: {c.get('progress', c['accent'])}; border-radius: 5px; }}
    QStatusBar {{ background: {c['header']}; color: {c['header_text']}; }}
    QSplitter::handle {{ background: {c['border']}; }}
    QToolTip {{ background: {c['header']}; color: {c['header_text']}; border: 1px solid {c['accent']}; padding: 6px; font-family: 'Segoe UI'; font-size: 10pt; }}
    """


def apply(app, name):
    """Apply a theme to the whole app"""
    global _current
    _current = dict(THEMES.get(name, THEMES[DEFAULT_THEME]))
    palette = QPalette()
    for role, key in [(QPalette.Window, 'window'), (QPalette.Base, 'panel'), (QPalette.AlternateBase, 'panel_alt'), (QPalette.Text, 'text'),
                      (QPalette.WindowText, 'text'), (QPalette.Button, 'panel'), (QPalette.ButtonText, 'text'),
                      (QPalette.Highlight, 'primary'), (QPalette.HighlightedText, 'primary_text'), (QPalette.ToolTipBase, 'header'),
                      (QPalette.ToolTipText, 'header_text'), (QPalette.PlaceholderText, 'text_muted')]:
        palette.setColor(role, QColor(_current[key]))
    app.setPalette(palette)
    app.setStyleSheet(stylesheet(_current))
