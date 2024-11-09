from PyQt5.QtCore import QPointF, Qt
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QDockWidget, QMainWindow, QStatusBar, QTabWidget, QToolBar

from megabone.editor import SkeletonEditor
from megabone.editor.mode import EditorModeRegistry
from megabone.model.document_manager import DocumentManager
from megabone.widget import MenuBuilder
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

        # Main editor area
        self.tabs = QTabWidget()
        self.tabs.setTabsClosable(True)
        self.setCentralWidget(self.tabs)

        # Docking area
        self.dock = QDockWidget("Dockable", self)
        self.dock.setAllowedAreas((Qt.TopDockWidgetArea | Qt.BottomDockWidgetArea))
        self.addDockWidget(Qt.BottomDockWidgetArea, self.dock)

        # self.editor = SkeletonEditor(self)
        # self.editor.addSprite(QPixmap("sample/yokozuna/body_piece.png"))
        # self.editor.addSprite(QPixmap("sample/yokozuna/limb_piece.png"))
        # self.editor.addSprite(QPixmap("sample/yokozuna/limb_piece.png"))
        # self.editor.addSprite(QPixmap("sample/yokozuna/shoulder_piece.png"))
        # self.editor.addSprite(QPixmap("sample/yokozuna/hand_piece.png"))

        # self.animation_player = AnimationPlayer()
        # self.animation_dock = QDockWidget("Animation", self)
        # self.animation_dock.setWidget(self.animation_player)
        # self.addDockWidget(Qt.BottomDockWidgetArea, self.animation_dock)

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
        pass

    def save_document(self):
        pass

    def setup_menu_bar(self):
        self.file_menu = (
            MenuBuilder("File", self)
            .add_action("new", "New", shortcut="Ctrl+N", triggered=self.new_document)
            .add_action("open", "Open", shortcut="Ctrl+O", triggered=self.open_document)
            .add_action("save", "Save", shortcut="Ctrl+S", triggered=self.save_document)
            .add_action("save_as", "Save as...")
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

        self.view_menu = (
            MenuBuilder("View", self)
            .add_action("explorer", "Explorer", checkable=True)
            .add_action("history", "History", checkable=True)
        )

        self.help_menu = (
            MenuBuilder("Help", self)
            .add_action("docs", "Documentation")
            .add_separator()
            .add_action("about", "About")
        )

        self.menuBar().addMenu(self.file_menu.build())
        self.menuBar().addMenu(self.edit_menu.build())
        self.menuBar().addMenu(self.view_menu.build())
        self.menuBar().addMenu(self.help_menu.build())
