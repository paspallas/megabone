from PyQt5.QtCore import QPointF, Qt
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QMainWindow, QStatusBar, QTabWidget, QToolBar

from megabone.widget import DockConfig, DockManager
from megabone.widget import StatusBarManager as status

from .main_controller import MainController
from .menu_controller import MainMenuController


class ZenWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        # State tracking
        self.is_zen_mode = False
        self.stored_window_state = None
        self.stored_geometry = None

    def toggle_full_screen(self) -> None:
        if not self.isFullScreen():
            self.showFullScreen()
        else:
            self.showNormal()

    def toggle_zen_mode(self) -> None:
        if not self.is_zen_mode:
            self.stored_window_state = self.saveState()
            self.stored_geometry = self.saveGeometry()
            self.menuBar().hide()
            self.showFullScreen()

            self.is_zen_mode = True
        else:
            self.showNormal()
            self.menuBar().show()

            if self.stored_window_state:
                self.restoreState(self.stored_window_state)
            if self.stored_geometry:
                self.restoreGeometry(self.stored_geometry)

            self.is_zen_mode = False

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Escape:
            if self.is_zen_mode:
                self.toggle_zen_mode()
            elif self.isFullScreen():
                self.toggle_full_screen()
        super().keyPressEvent(event)


class MegaBoneMainWindow(ZenWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Megabone")
        self.setMinimumSize(800, 600)

        # Delegate user interaction to controllers
        self.main_controller = MainController(self)
        self.menu_controller = MainMenuController(self.main_controller)
        self.menu_controller.populate_menu_bar(
            self.menuBar(), "File", "Edit", "View", "Help"
        )

        # Create status bar
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        status().initialize(self.status_bar)
        status().add_region("left", 200)
        status().add_region("right", 800)

        # Main editing area
        self.tabs = QTabWidget()
        self.tabs.setTabsClosable(True)
        self.setCentralWidget(self.tabs)

        # Docked widgets
        self.dock_manager = DockManager(
            self, self.menu_controller.get_builder("View").get_submenu("Show")
        )
        self.dock_manager.create_dock(
            "Explorer", DockConfig(title="Explorer", area=Qt.RightDockWidgetArea)
        )
        self.dock_manager.create_dock(
            "History", DockConfig(title="History", area=Qt.RightDockWidgetArea)
        )
        self.dock_manager.hide_all()

        # self.editor = SkeletonEditor(self)
        # self.editor.addSprite(QPixmap("sample/yokozuna/body_piece.png"))
        # self.editor.addSprite(QPixmap("sample/yokozuna/limb_piece.png"))
        # self.editor.addSprite(QPixmap("sample/yokozuna/limb_piece.png"))
        # self.editor.addSprite(QPixmap("sample/yokozuna/shoulder_piece.png"))
        # self.editor.addSprite(QPixmap("sample/yokozuna/hand_piece.png"))

        # Create unique toolbar
        self.toolbar = QToolBar()
        self.toolbar.setObjectName("ToolBar")
        self.addToolBar(self.toolbar)
