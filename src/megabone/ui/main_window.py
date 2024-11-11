from PyQt5.QtCore import QPointF, Qt
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QStatusBar, QTabWidget, QToolBar

from megabone.widget import DockConfig, DockManager
from megabone.widget import StatusBarManager as status
from megabone.widget import ZenWindow

from .main_controller import MainController
from .menu_controller import MainMenuController


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
        self.dock_manager.deactivate_all()

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
