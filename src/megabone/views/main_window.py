from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QStatusBar, QToolBar

from megabone.controller import MainController, MainMenuController
from megabone.controller import MenuType as m
from megabone.editor.mode import EditorModeRegistry
from megabone.manager import DockConfig, DockManager
from megabone.manager import StatusBarManager as status
from megabone.widget import ZenWindow


class MegaBoneMainWindow(ZenWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Megabone")
        self.setMinimumSize(800, 600)

        # Delegate user interaction to controllers
        self.main_controller = MainController()
        self.setCentralWidget(self.main_controller.get_tab_widget())

        self.menu = MainMenuController(self.main_controller)
        self.menu.populate_menu_bar(self.menuBar(), m.FILE, m.EDIT, m.VIEW, m.HELP)

        # Create status bar
        self.status_bar = QStatusBar(self)
        self.setStatusBar(self.status_bar)
        status().initialize(self.status_bar)
        status().add_region("left", 200)
        status().add_region("right", 800)

        # Docked widgets
        self.dock_manager = DockManager(
            self, self.menu.get_builder(m.VIEW).get_submenu("Show")
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

        for action in EditorModeRegistry.create_actions(
            self.main_controller.edit_controller
        ).values():
            self.toolbar.addAction(action)

        # Connect signals
        self.main_controller.requestFullScreen.connect(self.toggle_full_screen)
        self.main_controller.requestZenMode.connect(self.toggle_zen_mode)
