"""Slide a widget open or closed (animating its height) instead of showing or hiding it at once."""
from PySide6.QtCore import QEasingCurve, QObject, QPropertyAnimation

DURATION_MS = 300
UNLIMITED = 16777215 # Qt's largest widget size


class Collapsible(QObject):
    """Shows or hides `widget`, sliding it open or closed. `page`: the widget whose layout holds it (measures the open
    height, which can be more than the widget's own size hint when it stretches to fill space)."""
    def __init__(self, widget, page, duration=DURATION_MS):
        super().__init__(widget)
        self.widget, self.page, self.duration = widget, page, duration
        self.animation = None

    def is_open(self):
        return not self.widget.isHidden() and self.widget.maximumHeight() > 0

    def set_open(self, show, animate=True):
        widget = self.widget
        if self.animation is not None:
            self.animation.stop()
            self.animation = None
        if not animate or not self.page.isVisible() or show == self.is_open():
            widget.setMaximumHeight(UNLIMITED)
            widget.setVisible(show)
            return
        if show:
            # Measure the open height, then grow into it
            self.page.setUpdatesEnabled(False)
            widget.setMaximumHeight(UNLIMITED)
            widget.setVisible(True)
            self.page.layout().activate()
            target = widget.height()
            widget.setMaximumHeight(0)
            self.page.setUpdatesEnabled(True)
            start = 0
        else:
            start, target = widget.height(), 0
        animation = QPropertyAnimation(widget, b'maximumHeight', self)
        animation.setDuration(self.duration)
        animation.setStartValue(start)
        animation.setEndValue(target)
        animation.setEasingCurve(QEasingCurve.InOutCubic)
        def done():
            widget.setMaximumHeight(UNLIMITED) # Open: free to resize with the window again
            widget.setVisible(show)
            if self.animation is animation:
                self.animation = None
        animation.finished.connect(done)
        self.animation = animation
        animation.start()
