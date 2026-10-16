"""Where the app reads its bundled files and writes the user's, from source and as a packaged exe (PyInstaller).

Bundled, read-only files (data/wiki_data.json, data/icons) are read from the package. The user's files (settings,
presets, search results, crash logs, numba's compiled cache in the exe) go in %LOCALAPPDATA%\\ck-dps-solver (on other
systems ~/.local/share/ck-dps-solver), or the folder in the CK_DPS_SOLVER_HOME environment variable.

Imported first by the package (ck_dps_solver/__init__.py), so numba's cache folder is set before numba loads.
"""
import os
import sys

FROZEN = getattr(sys, 'frozen', False)
PACKAGE = os.path.dirname(os.path.abspath(__file__)) # Also inside the exe: the package's files are bundled at their paths


def _user_dir():
    if os.environ.get('CK_DPS_SOLVER_HOME'):
        return os.environ['CK_DPS_SOLVER_HOME']
    if os.environ.get('LOCALAPPDATA'):
        return os.path.join(os.environ['LOCALAPPDATA'], 'ck-dps-solver')
    return os.path.join(os.environ.get('XDG_DATA_HOME') or os.path.expanduser('~/.local/share'), 'ck-dps-solver')


USER_DIR = _user_dir()
os.makedirs(USER_DIR, exist_ok=True)
if FROZEN: # From source, numba caches next to the sources (__pycache__)
    os.environ.setdefault('NUMBA_CACHE_DIR', os.path.join(USER_DIR, 'numba_cache'))


def resource(*parts):
    """Path of a bundled, read-only file (relative to the package, e.g. resource('data', 'wiki_data.json'))"""
    return os.path.join(PACKAGE, *parts)


def user_file(*parts):
    """Path of a file the app writes (settings, presets, outputs)"""
    return os.path.join(USER_DIR, *parts)


def can_cache(module_file):
    """numba can cache compiled code only when the module's Python source is present (the exe bundles the .py files
    to keep the cache; without them it compiles on each start instead of failing)"""
    return module_file.endswith('.py') and os.path.exists(module_file)
