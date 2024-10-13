from PyQt5.QtCore import Qt, QPointF
from PyQt5.QtWidgets import QGraphicsView

from .editor_mode_register import EditorModeRegistry, AbstractEditorMode, EditorType
from megabone.editor.item import BoneGraphicsItem


@EditorModeRegistry.register("Create a new bone")
class CreateBoneMode(AbstractEditorMode):
    def __init__(self, editor: EditorType):
        super().__init__(editor)
        self.start_point = None
        self.new_bone = None

    def activate(self):
        self.editor.setDragMode(QGraphicsView.NoDrag)
        self.editor.setCursor(Qt.CrossCursor)
        self.editor.setMouseTracking(True)
        self.editor.showStatusMessage("Shift + Right Click")

    def deactivate(self):
        self.editor.setMouseTracking(False)

    def mousePressEvent(self, event, scene_pos):
        if event.button() == Qt.LeftButton:
            if self.new_bone is None:
                # Start drawing a new bone
                self.new_bone = BoneGraphicsItem(scene_pos, scene_pos + QPointF(1, 1))

                if event.modifiers() & Qt.ShiftModifier:
                    # If shift is held and we clicked on a bone, use it as parent
                    parent_bone = self.editor.scene.itemAt(
                        scene_pos, self.editor.transform()
                    )
                    if isinstance(parent_bone, BoneGraphicsItem):
                        self.new_bone.setParentBone(parent_bone)

                self.editor.scene.addItem(self.new_bone)
                self.editor.bones.append(self.new_bone)

            else:
                # Finish drawing bone
                self.new_bone = None

    def mouseMoveEvent(self, event, scene_pos):
        if self.new_bone:
            self.new_bone.end_point = scene_pos
            self.new_bone.update()

    def mouseReleaseEvent(self, event, scene_pos):
        pass
