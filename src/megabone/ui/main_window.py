from PyQt5.QtWidgets import QMainWindow, QToolBar

from megabone.editor import SkeletonEditor
from megabone.editor.mode import EditorModeRegistry


class MegaBoneMainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Megabone")
        self.setMinimumSize(800, 600)

        self.editor = SkeletonEditor(self)
        self.setCentralWidget(self.editor)

        # self.animation_player = AnimationPlayer()
        # self.animation_dock = QDockWidget("Animation", self)
        # self.animation_dock.setWidget(self.animation_player)
        # self.addDockWidget(Qt.BottomDockWidgetArea, self.animation_dock)

        # Create toolbar
        self.toolbar = QToolBar()
        self.addToolBar(self.toolbar)

        actions = EditorModeRegistry.create_actions(self.editor)
        for action in actions.values():
            self.toolbar.addAction(action)
