from PyQt5.QtCore import QPointF, Qt
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QMainWindow, QStatusBar, QTabWidget, QToolBar

from megabone.dialog import FileDialog
from megabone.editor import SkeletonEditor
from megabone.editor.mode import EditorModeRegistry
from megabone.model.document_manager import DocumentManager
from megabone.widget import DockConfig, DockManager, MenuBuilder
from megabone.widget import StatusBarManager as status


class MegaBoneMainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Megabone")
        self.setMinimumSize(800, 600)

        self.setup_menu_bar()

        # Manage all operations on the data model
        self.active_document = None
        self.document_manager = DocumentManager()

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
        self.dock_manager = DockManager(self, self.view_menu.menu)
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
        self.addToolBar(self.toolbar)

    def new_document(self):
        id = self.document_manager.create_document()
        editor = SkeletonEditor()
        actions = EditorModeRegistry.create_actions(editor)
        for action in actions.values():
            self.toolbar.addAction(action)

        index = self.tabs.addTab(editor, id)

    def open_document(self):
        file = FileDialog.open_file()
        if file:
            pass

    def save_document(self):
        file = FileDialog.save_file()
        if file:
            pass

    def setup_menu_bar(self):
        self.file_menu = (
            MenuBuilder("File", self)
            .add_action("new", "New", shortcut="Ctrl+N", triggered=self.new_document)
            .add_action(
                "open",
                "Open...",
                shortcut="Ctrl+O",
                triggered=self.open_document,
            )
            .add_action("save", "Save", shortcut="Ctrl+S", triggered=self.save_document)
            .add_action("save_as", "Save As...")
            .add_separator()
            .begin_submenu("Export")
            .add_action("sprite_sheet", "As Sprite Sheet")
            .end_submenu()
            .add_separator()
            .add_action("exit", "Exit", shortcut="Ctrl+Q")
        )

        self.edit_menu = (
            MenuBuilder("Edit", self)
            .add_action("undo", "Undo", shortcut="Ctrl+Z")
            .add_action("redo", "Redo", shortcut="Ctrl+Y")
        )

        self.help_menu = (
            MenuBuilder("Help", self)
            .add_action("docs", "Documentation")
            .add_separator()
            .add_action("about", "About")
        )

        self.view_menu = MenuBuilder("View", self)

        self.menuBar().addMenu(self.file_menu.build())
        self.menuBar().addMenu(self.edit_menu.build())
        self.menuBar().addMenu(self.view_menu.build())
        self.menuBar().addMenu(self.help_menu.build())
