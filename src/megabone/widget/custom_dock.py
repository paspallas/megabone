from enum import Enum, auto

from PyQt5.QtCore import pyqtSignal
from PyQt5.QtWidgets import QDockWidget


class DockCloseAction(Enum):
    HIDE = auto()  # Hide the dock but keep it in memory
    REMOVE = auto()  # Completely remove the dock
    PREVENT = auto()  # Prevent the dock from closing


class CustomDockWidget(QDockWidget):
    """Custom dock widget with close event handling"""

    closeRequested = pyqtSignal()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.close_action = DockCloseAction.HIDE
        self.close_handler = None
        self.visibility_handler = None

    def closeEvent(self, event):
        self.closeRequested.emit()
        if self.close_action == DockCloseAction.PREVENT:
            event.ignore()
        else:
            event.accept()

    def visibilityChanged(self, visible):
        super().visibilityChanged(visible)
        if self.visibility_handler:
            self.visibility_handler(visible)
