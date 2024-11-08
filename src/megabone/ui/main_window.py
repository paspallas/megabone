from PyQt5.QtCore import QPointF
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QMainWindow, QStatusBar, QTabWidget, QToolBar

from megabone.editor import SkeletonEditor
from megabone.editor.mode import EditorModeRegistry
from megabone.model.document_manager import DocumentManager
from megabone.util import StatusBarManager as status


class MegaBoneMainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Megabone")
        self.setMinimumSize(800, 600)

        self.document_manager = DocumentManager()

        # Create status bar
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        status().initialize(self.status_bar)
        status().add_region("left", 200)
        status().add_region("right", 800)

        self.tab_widget = QTabWidget(self)
        self.setCentralWidget(self.tab_widget)

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

        # Create toolbar
        self.toolbar = QToolBar()
        self.addToolBar(self.toolbar)

        # actions = EditorModeRegistry.create_actions(self.editor)
        # for action in actions.values():
        #     self.toolbar.addAction(action)
