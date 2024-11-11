from PyQt5.QtCore import QPointF, Qt

from megabone.editor.item import BoneItem
from megabone.manager import StatusBarManager as status

from .editor_mode_register import AbstractEditorMode, EditorModeRegistry, EditorType


@EditorModeRegistry.register("Create a new bone", "B")
class CreateBoneMode(AbstractEditorMode):
    def __init__(self, editor: EditorType):
        super().__init__(editor)
        self.start_point = None
        self.new_bone = None

    def activate(self):
        self.editor.setCursor(Qt.CrossCursor)

    def deactivate(self):
        self.editor.setCursor(Qt.ArrowCursor)

    def mousePressEvent(self, event, scene_pos):
        if event.button() == Qt.LeftButton:
            if self.new_bone is None:
                # Start drawing a new bone
                self.new_bone = BoneItem(scene_pos, scene_pos + QPointF(1, 1))

                if event.modifiers() & Qt.ShiftModifier:
                    # If shift is held and we clicked on a bone, use it as parent
                    parent_bone = self.editor.scene().itemAt(
                        scene_pos, self.editor.transform()
                    )
                    if isinstance(parent_bone, BoneItem):
                        self.new_bone.setParentBone(parent_bone)

                # TODO manage addition of all items to the editor in a centralized place
                self.editor.scene().addItem(self.new_bone)
                self.editor.bones.append(self.new_bone)
                # self.editor.layer_control.add_item(self.new_bone)

            else:
                # Finish drawing bone
                self.new_bone.setSelected(False)
                self.new_bone = None

    def mouseMoveEvent(self, event, scene_pos):
        if self.new_bone:
            self.new_bone.end_point = scene_pos
            self.new_bone.update()

    def mouseReleaseEvent(self, event, scene_pos):
        pass
