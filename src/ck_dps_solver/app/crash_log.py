"""Crash log: errors go to crash.log in the user folder (next to gui_config.json), with a message box saying so. The
double-click launcher has no console, so without this an error would just close the window or be lost."""
import datetime
import faulthandler
import os
import platform
import sys
import threading
import traceback

from ck_dps_solver import __version__, paths

PATH = paths.user_file('crash.log')
MAX_BYTES = 1_000_000 # Start the log over when it gets this big
_fault_file = None


def write(title, text):
    """Add an entry to the crash log; returns the log's path"""
    try:
        if os.path.exists(PATH) and os.path.getsize(PATH) > MAX_BYTES:
            os.replace(PATH, PATH + '.old')
        with open(PATH, 'a', encoding='utf8') as f:
            f.write(f"\n===== {datetime.datetime.now():%Y-%m-%d %H:%M:%S} | {title} | CK DPS Solver {__version__} | "
                    f"Python {platform.python_version()}, {platform.platform()}\n{text.rstrip()}\n")
    except OSError:
        pass # Never let logging itself crash the app
    return PATH


def _show(title, message):
    from PySide6.QtWidgets import QApplication, QMessageBox
    if QApplication.instance() is not None:
        QMessageBox.critical(None, title, message)


def _excepthook(kind, value, tb):
    text = ''.join(traceback.format_exception(kind, value, tb))
    write('Error', text)
    sys.__stderr__ and sys.__stderr__.write(text) # Still printed when there is a console
    _show('Core Keeper DPS solver: error', f'{kind.__name__}: {value}\n\nThe details are in {PATH}')


def _thread_excepthook(args):
    _excepthook(args.exc_type, args.exc_value, args.exc_traceback)


def install():
    """Log uncaught errors (window thread and other threads) and hard crashes (faulthandler)"""
    global _fault_file
    sys.excepthook = _excepthook
    threading.excepthook = _thread_excepthook
    try:
        _fault_file = open(paths.user_file('crash_fault.log'), 'a', encoding='utf8') # Hard crashes (no Python error)
        faulthandler.enable(_fault_file)
    except OSError:
        pass
