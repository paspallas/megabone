from pathlib import Path

from PyQt5.QtCore import QObject, QSettings, pyqtSignal
from PyQt5.QtWidgets import QAction, QMenu, QMessageBox

import megabone.util.constants as c


class RecentFilesManager(QObject):
    recentFileOPen = pyqtSignal(Path)

    def __init__(self, parent=None, max_files=10):
        super().__init__(parent)
        self.max_files = max_files
        self.settings = QSettings(c._SETTINGS_COMPANY_NAME, c._SETTINGS_APP_NAME)
        self.recent_files = []
        self.menu: QMenu = None

        self.load_recent_files()

    def set_menu(self, menu: QMenu):
        self.menu = menu

    def load_recent_files(self):
        """Load history from qsettings"""
        files = self.settings.value("recent_files", [])

        if isinstance(files, str):
            # Handle single file case
            files = [files]
        self.recent_files = files if files else []

    def save_recent_files(self):
        """Save history to qsettings"""
        self.settings.setValue("recent_files", self.recent_files)

    def add_recent_file(self, filepath: Path):
        # Get absolute path
        filepath = filepath.resolve(True)

        # Remove if already exists
        if filepath in self.recent_files:
            self.recent_files.remove(filepath)

        self.recent_files.insert(0, filepath)
        self.recent_files = self.recent_files[: self.max_files]

        self.save_recent_files()
        self.update_menu()

    @property
    def clear_action(self) -> QAction:
        clear_action = QAction("Clear Recent Files", self.menu)
        clear_action.triggered.connect(self.clear_recent_files)
        return clear_action

    def update_menu(self):
        self.menu.clear()

        for filepath in self.recent_files:
            action = QAction(self._formatted_filename(filepath), self)
            action.setData(filepath)
            action.setStatusTip(str(filepath))
            action.triggered.connect(lambda checked, f=filepath: self.file_selected(f))
            self.menu.addAction(action)

        if len(self.recent_files) > 0:
            self.menu.addSeparator()
            self.menu.addAction(self.clear_action)

        self.menu.update()

    def _formatted_filename(self, filepath: Path):
        """Get a formatted version for display"""
        return f"{filepath.name} ({filepath.parent})"

    def file_selected(self, filepath: Path):
        if filepath.exists():
            self.recentFileOPen.emit(filepath)
        else:
            QMessageBox.warning(
                self, "File Not Found", f"The file '{filepath}' no longer exists."
            )
            self.recent_files.remove(filepath)
            self.save_recent_files()
            self.update_menu()

    def clear_recent_files(self):
        self.recent_files = []
        self.save_recent_files()
        self.update_menu()
