from dataclasses import dataclass
from enum import Enum, auto
from typing import Callable, Dict, Optional, Type

from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtWidgets import (
    QAction,
    QDockWidget,
    QLabel,
    QMainWindow,
    QMenu,
    QTabWidget,
    QVBoxLayout,
    QWidget,
)


class DockCloseAction(Enum):
    HIDE = auto()  # Hide the dock but keep it in memory
    REMOVE = auto()  # Completely remove the dock
    PREVENT = auto()  # Prevent the dock from closing


@dataclass
class DockConfig:
    """Configuration for a dock widget"""

    title: str
    area: Qt.DockWidgetArea = Qt.LeftDockWidgetArea
    allowed_areas: Qt.DockWidgetAreas = Qt.AllDockWidgetAreas
    widget: Optional[QWidget] = None
    widget_class: Optional[Type[QWidget]] = None
    floating: bool = False
    closable: bool = True
    close_action: DockCloseAction = DockCloseAction.HIDE
    on_close: Optional[Callable[[], None]] = None
    on_visibility_changed: Optional[Callable[[bool], None]] = None


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


class DockManager:
    def __init__(self, main_window: QMainWindow, view_menu: QMenu):
        self.main_window = main_window
        self.view_menu = view_menu
        self.docks: Dict[str, CustomDockWidget] = {}
        self.hidden_docks: Dict[str, CustomDockWidget] = {}

        # Enable tabbed docking
        self.main_window.setTabPosition(Qt.AllDockWidgetAreas, QTabWidget.North)
        self.main_window.setDockOptions(
            QMainWindow.AllowTabbedDocks | QMainWindow.AllowNestedDocks
        )

    def create_dock(self, dock_id: str, config: DockConfig) -> CustomDockWidget:
        """Create a new dock widget with the given configuration"""
        if dock_id in self.docks:
            raise KeyError(f"Dock with ID {dock_id} already exists")

        # Create the new dock
        dock = CustomDockWidget(config.title, self.main_window)
        dock.setObjectName(dock_id)
        dock.close_action = config.close_action
        dock.close_handler = config.on_close
        dock.visibility_handler = config.on_visibility_changed

        # Configure dock features
        features = QDockWidget.DockWidgetFloatable | QDockWidget.DockWidgetMovable
        if config.closable:
            features |= QDockWidget.DockWidgetClosable
        dock.setFeatures(features)

        # Set allowed areas
        dock.setAllowedAreas(config.allowed_areas)

        # Create and set the widget
        if config.widget:
            widget = config.widget
        elif config.widget_class:
            widget = config.widget_class()
        else:
            widget = QWidget()
            layout = QVBoxLayout()
            layout.addWidget(QLabel(config.title))
            widget.setLayout(layout)

        dock.setWidget(widget)

        # Connect close event
        dock.closeRequested.connect(lambda: self._handle_dock_close(dock_id))

        # Add dock to main window
        self.main_window.addDockWidget(config.area, dock)
        dock.setFloating(config.floating)
        self._add_to_view_menu(dock_id, config.title)

        self.docks[dock_id] = dock

        return dock

    def _handle_dock_close(self, dock_id: str):
        dock = self.docks.get(dock_id)

        if dock.close_handler:
            dock.close_handler()

        if dock.close_action == DockCloseAction.HIDE:
            dock.hide()
            self._uncheck_menu_item(dock_id)

            if dock_id not in self.hidden_docks:
                self.hidden_docks[dock_id] = dock
        elif dock.close_action == DockCloseAction.REMOVE:
            self.remove_dock(dock_id)

    def _add_to_view_menu(self, dock_id: str, title: str):
        action = QAction(title, self.main_window)
        action.setCheckable(True)
        action.setChecked(True)
        action.triggered.connect(lambda checked: self.toggle_dock(dock_id, checked))
        self.view_menu.addAction(action)

    def _uncheck_menu_item(self, dock_id: str):
        for action in self.view_menu.actions():
            if action.text() == dock_id:
                action.setChecked(False)

    def toggle_dock(self, dock_id: str, visible: bool):
        if dock_id in self.docks:
            self.docks[dock_id].setVisible(visible)
        elif dock_id in self.hidden_docks:
            dock = self.hidden_docks.get(dock_id)
            dock.setVisible(visible)
            if visible:
                self.docks[dock_id] = dock
                self.hidden_docks.pop(dock_id)

    def show_dock(self, dock_id: str):
        self.toggle_dock(dock_id, True)

    def hide_dock(self, dock_id: str):
        self.toggle_dock(dock_id, False)
        self._uncheck_menu_item(dock_id)

    def hide_all(self):
        for dock in self.docks.keys():
            self.hide_dock(dock)
