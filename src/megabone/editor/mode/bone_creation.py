from PyQt5.QtCore import QPointF, Qt

from megabone.editor.item import BoneItem
from megabone.model.bone import BoneData
from megabone.model.collection import UpdateSource

from .abstract_mode import AbstractEditorMode
from .editor_mode_register import EditorModeRegistry


@EditorModeRegistry.register("Create a new bone", "B")
class CreateBoneMode(AbstractEditorMode):
    def __init__(self, controller):
        super().__init__(controller)
        self.start_point = None
        self.new_bone = None

    def activate(self):
        self.view.setCursor(Qt.CrossCursor)

    def deactivate(self):
        self.view.setCursor(Qt.ArrowCursor)

    def mousePressEvent(self, event, scene_pos):
        if event.button() == Qt.LeftButton:
            if self.new_bone is None:
                bone_data = BoneData()

                # Create the bone item
                self.new_bone = BoneItem(
                    self.bones_model,
                    scene_pos,
                    scene_pos + QPointF(1, 1),
                    bone_data.id,
                )

                if event.modifiers() & Qt.ShiftModifier:
                    # If shift is held and we clicked on a bone, use it as parent
                    parent_bone = self.scene.itemAt(scene_pos, self.view.transform())
                    if isinstance(parent_bone, BoneItem):
                        self.new_bone.set_parent_bone(parent_bone)

                self.view.add_items(self.new_bone)

                # Add to the model
                self.bones_model.add_item(bone_data, UpdateSource.VIEW)

                # TODO remove this!
                self.view.bones.append(self.new_bone)
            else:
                # Finish drawing bone
                self.new_bone.setSelected(False)
                self.new_bone = None

    def mouseMoveEvent(self, event, scene_pos):
        if self.new_bone:
            self.new_bone.end_point = scene_pos
            self.new_bone.update()
            self.new_bone.update_model()

    def mouseReleaseEvent(self, event, scene_pos):
        pass
