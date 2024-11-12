from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QStatusBar, QToolBar

from megabone.controller import (
    EditorController,
    MainController,
    MainMenuController,
    MenuType,
)
from megabone.editor.mode import EditorModeRegistry
from megabone.manager import AutoSaveManager, DockConfig, DockManager, DocumentManager
from megabone.manager import StatusBarManager as status
from megabone.widget import ZenWindow


class MegaBoneMainWindow(ZenWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Megabone")
        self.setMinimumSize(800, 600)

        self.documents = DocumentManager()
        self.autosave = AutoSaveManager(self.documents)
        self.edit = EditorController(self.documents)
        self.controller = MainController()
        self.menu = MainMenuController(self.controller, self.documents)
        self.menu.populate_menu_bar(self.menuBar())

        self.setCentralWidget(self.edit.views_container())

        # Create status bar
        self.status_bar = QStatusBar(self)
        self.setStatusBar(self.status_bar)
        status().initialize(self.status_bar)
        status().add_region("left", 200)
        status().add_region("right", 800)

        # Docked widgets
        self.dock_manager = DockManager(
            self, self.menu.get_builder(MenuType.VIEW).get_submenu("Show")
        )
        self.dock_manager.create_dock(
            "Explorer", DockConfig(title="Explorer", area=Qt.RightDockWidgetArea)
        )
        self.dock_manager.create_dock(
            "History", DockConfig(title="History", area=Qt.RightDockWidgetArea)
        )
        self.dock_manager.deactivate_all()

        # Create unique toolbar
        self.toolbar = QToolBar()
        self.toolbar.setObjectName("ToolBar")
        self.addToolBar(self.toolbar)

        for action in EditorModeRegistry.create_actions(self.edit).values():
            self.toolbar.addAction(action)

        # Connect signals
        self.controller.requestFullScreen.connect(self.toggle_full_screen)
        self.controller.requestZenMode.connect(self.toggle_zen_mode)
        self.controller.requestQuit.connect(self.close)
