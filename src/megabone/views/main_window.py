from megabone.controller import (
    EditorController,
    MainController,
    MainMenuController,
    MenuType,
)
from megabone.manager.autosave import AutoSaveManager
from megabone.manager.dock import DockConfig, DockManager
from megabone.manager.document import DocumentManager
from megabone.manager.status import StatusBarManager as status
from megabone.qt import QStatusBar, Qt, QToolBar
from megabone.widget import HistoryPanel, SpritePalettePanel, ZenWindow


class AppMainWindow(ZenWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Megabone")
        self.setMinimumSize(800, 600)

        self.document_collection = DocumentManager()
        self.autosave_manager = AutoSaveManager(self.document_collection)

        self.editor_controller = EditorController(self.document_collection)
        self.main_controller = MainController()
        self.menu = MainMenuController(self.main_controller, self.document_collection)
        self.history_panel = HistoryPanel(self)
        self.history_panel.set_group(self.document_collection.undo_group)

        self.setCentralWidget(self.editor_controller.tab_views())

        menubar = self.menuBar()
        assert menubar is not None, "Failed to create menubar"
        self.menu.populate_menu_bar(menubar)

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

        for action in EditorModeRegistry.create_actions(
            self.editor_controller
        ).values():
            self.toolbar.addAction(action)

        self._populate_dock()
        self._connect_signals()

    def _connect_signals(self):
        self.main_controller.requestFullScreen.connect(self.toggle_full_screen)
        self.main_controller.requestZenMode.connect(self.toggle_zen_mode)
        self.main_controller.requestQuit.connect(self.close)

    def _populate_dock(self):
        self.dock_manager = DockManager(
            self, self.menu.get_builder(MenuType.VIEW).get_submenu("Show")
        )
        self.dock_manager.create_dock(
            "Explorer",
            DockConfig(title="Explorer", area=Qt.DockWidgetArea.RightDockWidgetArea),
        )
        self.dock_manager.create_dock(
            "History",
            DockConfig(
                title="History",
                area=Qt.DockWidgetArea.RightDockWidgetArea,
                widget=self.history_panel,
            ),
        )
        self.dock_manager.create_dock(
            "Palette",
            DockConfig(
                title="Palette",
                area=Qt.DockWidgetArea.RightDockWidgetArea,
                widget=SpritePalettePanel(self),
            ),
        )
        self.dock_manager.deactivate(["Explorer"])
