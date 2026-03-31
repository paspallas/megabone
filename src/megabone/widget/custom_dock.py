from enum import Enum, auto
from typing import Callable

from megabone.qt import QCloseEvent, QDockWidget, Signal


class DockCloseAction(Enum):
    HIDE = auto()  # Hide the dock but keep it in memory
    REMOVE = auto()  # Completely remove the dock
    PREVENT = auto()  # Prevent the dock from closing


class CustomDockWidget(QDockWidget):
    """Custom dock widget with close event handling"""

    closeRequested = Signal()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.close_action = DockCloseAction.HIDE
        self.close_handler: Callable | None = None
        self.visibility_handler: Callable | None = None

    def closeEvent(self, event: QCloseEvent | None):
        self.closeRequested.emit()

        assert event is not None
        if self.close_action == DockCloseAction.PREVENT:
            event.ignore()
        else:
            event.accept()

    def visibilityChanged(self, visible):
        super().visibilityChanged(visible)

        if self.visibility_handler:
            self.visibility_handler(visible)
