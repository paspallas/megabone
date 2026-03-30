from megabone.controller import (
    EditorController,
    MainController,
    MainMenuController,
    MenuType,
)
from megabone.manager import AutoSaveManager, DockConfig, DockManager, DocumentManager
from megabone.manager import StatusBarManager as status
from megabone.qt import QStatusBar, Qt, QToolBar
from megabone.widget import SpritePalettePanel, ZenWindow


class AppMainWindow(ZenWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Megabone")
        self.setMinimumSize(800, 600)

        self.documents = DocumentManager()
        self.autosave = AutoSaveManager(self.documents)
        self.edit = EditorController(self.documents)
        self.controller = MainController()
        self.menu = MainMenuController(self.controller, self.documents)

        self._create_dock_widgets()

        menubar = self.menuBar()
        assert menubar is not None, "Failed to create menubar"
        self.menu.populate_menu_bar(menubar)

        self.setCentralWidget(self.edit.tab_views())

        # Create status bar
        self.status_bar = QStatusBar(self)
        self.setStatusBar(self.status_bar)
        status().initialize(self.status_bar)
        status().add_region("left", 200)
        status().add_region("right", 800)

        # Create unique toolbar
        self.toolbar = QToolBar()
        self.toolbar.setObjectName("ToolBar")
        self.addToolBar(self.toolbar)

        # Populate all registered edit modes
        from megabone.editor.mode import EditorModeRegistry

        for action in EditorModeRegistry.create_actions(self.edit).values():
            self.toolbar.addAction(action)

        # Connect signals to super class
        self.controller.requestFullScreen.connect(self.toggle_full_screen)
        self.controller.requestZenMode.connect(self.toggle_zen_mode)
        self.controller.requestQuit.connect(self.close)

    def _create_dock_widgets(self):
        self.dock_manager = DockManager(
            self, self.menu.get_builder(MenuType.VIEW).get_submenu("Show")
        )
        self.dock_manager.create_dock(
            "Explorer",
            DockConfig(title="Explorer", area=Qt.DockWidgetArea.RightDockWidgetArea),
        )
        self.dock_manager.create_dock(
            "History",
            DockConfig(title="History", area=Qt.DockWidgetArea.RightDockWidgetArea),
        )
        self.dock_manager.create_dock(
            "Palette",
            DockConfig(
                title="Palette",
                area=Qt.DockWidgetArea.RightDockWidgetArea,
                widget=SpritePalettePanel(self),
            ),
        )
        self.dock_manager.deactivate(["Explorer", "History"])
