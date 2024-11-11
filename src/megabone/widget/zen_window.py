from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QMainWindow, QToolBar


class ZenWindow(QMainWindow):
    """Window with Zen mode"""

    def __init__(self):
        super().__init__()

        # State tracking
        self.is_zen_mode = False
        self.stored_window_state = None
        self.stored_geometry = None

    def _save_state(self) -> None:
        self.stored_window_state = self.saveState()
        self.stored_geometry = self.saveGeometry()

    def _restore_state(self) -> None:
        if self.stored_window_state:
            self.restoreState(self.stored_window_state)
        if self.stored_geometry:
            self.restoreGeometry(self.stored_geometry)

    def toggle_full_screen(self) -> None:
        if not self.isFullScreen():
            self._save_state()
            self.showFullScreen()
        else:
            self._restore_state()
            self.showMaximized()

    def toggle_zen_mode(self) -> None:
        if not self.is_zen_mode:
            self._save_state()

            if self.menuBar():
                self.menuBar().hide()

            if self.statusBar():
                self.statusBar().hide()

            for child in self.children():
                if isinstance(child, QToolBar):
                    child.hide()

            if hasattr(self, "dock_manager"):
                self.dock_manager.hide()

            self.is_zen_mode = True
            self.showFullScreen()
        else:
            self._restore_state()

            if self.menuBar():
                self.menuBar().show()

            if self.statusBar():
                self.statusBar().show()

            self.is_zen_mode = False
            self.showMaximized()

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Escape:
            if self.is_zen_mode:
                self.toggle_zen_mode()
            elif self.isFullScreen():
                self.toggle_full_screen()
        super().keyPressEvent(event)
