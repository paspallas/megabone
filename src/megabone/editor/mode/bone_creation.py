from PyQt5.QtCore import QPointF, Qt

import megabone.util.utils as util
from megabone.editor.item import BoneItem
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
                bone_id = util.gen_unique_id()

                # Create a new bone
                self.new_bone = BoneItem(
                    self.bones,
                    scene_pos,
                    scene_pos + QPointF(1, 1),
                    bone_id,
                )

                # Add to the model
                self.bones.add_item(
                    bone_id, self.new_bone.create_model_data(), UpdateSource.VIEW
                )

                if event.modifiers() & Qt.ShiftModifier:
                    # If shift is held and we clicked on a bone, use it as parent
                    parent_bone = self.scene.itemAt(scene_pos, self.view.transform())
                    if isinstance(parent_bone, BoneItem):
                        self.new_bone.setParentBone(parent_bone)

                self.scene.addItem(self.new_bone)
                self.view.bones.append(self.new_bone)
                # TODO manage layers correctly
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
