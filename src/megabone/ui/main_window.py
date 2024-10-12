from PyQt5.QtWidgets import QMainWindow, QToolBar, QAction

from megabone.editor import SkeletonEditor
from megabone.editor.mode import EditorModeType as Mode


class MegaBoneMainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Megabone")
        self.setMinimumSize(800, 600)
        self.editor = SkeletonEditor()
        self.setCentralWidget(self.editor)

        # self.animation_player = AnimationPlayer()
        # self.animation_dock = QDockWidget("Animation", self)
        # self.animation_dock.setWidget(self.animation_player)
        # self.addDockWidget(Qt.BottomDockWidgetArea, self.animation_dock)

        # Create toolbar
        toolbar = QToolBar()
        self.addToolBar(toolbar)

        # Add tool buttons
        select_action = QAction("Select", self)
        select_action.triggered.connect(lambda: self.editor.setEditMode(Mode.Selection))
        toolbar.addAction(select_action)

        create_bone_action = QAction("Create Bone", self)
        create_bone_action.triggered.connect(
            lambda: self.editor.setEditMode(Mode.CreateBone)
        )
        toolbar.addAction(create_bone_action)

        attach_sprite_action = QAction("Attach Sprite", self)
        attach_sprite_action.triggered.connect(
            lambda: self.editor.setEditMode(Mode.AttachSprite)
        )
        toolbar.addAction(attach_sprite_action)

        create_ik_chain_action = QAction("Move Ik chain", self)
        create_ik_chain_action.triggered.connect(
            lambda: self.editor.setEditMode(Mode.MoveIkChain)
        )
        toolbar.addAction(create_ik_chain_action)

        create_ik_handle_action = QAction("Create Ik chain handle", self)
        create_ik_handle_action.triggered.connect(
            lambda: self.editor.setEditMode(Mode.CreateIkHandle)
        )
        toolbar.addAction(create_ik_handle_action)

        animation_action = QAction("Animation", self)
        animation_action.triggered.connect(
            lambda: self.editor.setEditMode(Mode.Animation)
        )
        toolbar.addAction(animation_action)
