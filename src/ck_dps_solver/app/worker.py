"""Runs a search off the window's thread and reports back with signals (progress, log lines, results, errors)."""
import threading
import time
import traceback

from PySide6.QtCore import QObject, QThread, Signal

from ck_dps_solver.engine import solver

from ck_dps_solver.app import crash_log


class SearchWorker(QObject):
    stage = Signal(int, str)        # A stage starts: total steps, description
    progressed = Signal(int, int, float) # Steps done, total, seconds left (-1 if not known yet)
    logged = Signal(str)
    finished = Signal(object, object) # Results DataFrame, info dict
    failed = Signal(str)

    def __init__(self, config):
        super().__init__()
        self.config = config
        self.stop_event = threading.Event()
        self._total = self._done = 0
        self._started = time.time()

    # The progress interface solver.run_search expects
    def start(self, total, description):
        self._total, self._done, self._started = max(total, 1), 0, time.time()
        self.stage.emit(self._total, description)

    def update(self, n):
        self._done += n
        elapsed = time.time() - self._started
        left = elapsed / self._done * (self._total - self._done) if self._done >= max(self._total * 0.02, 1) and elapsed > 3 else -1.0
        self.progressed.emit(self._done, self._total, left)

    def run(self):
        try:
            results, info = solver.run_search(self.config, progress=self, should_stop=self.stop_event.is_set, log=self.logged.emit)
            self.finished.emit(results, info)
        except Exception as e: # Shown in the window instead of failing silently, and kept in crash.log
            path = crash_log.write('Search failed', traceback.format_exc())
            self.failed.emit(f'{type(e).__name__}: {e} (details in {path})')


def start_search(config):
    """A SearchWorker running on its own thread; connect its signals, then call thread.start()"""
    thread = QThread()
    worker = SearchWorker(config)
    worker.moveToThread(thread)
    thread.started.connect(worker.run)
    worker.finished.connect(thread.quit)
    worker.failed.connect(thread.quit)
    return thread, worker
