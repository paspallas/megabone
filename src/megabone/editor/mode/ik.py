import math

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPen
from PyQt5.QtWidgets import QGraphicsEllipseItem

from .abstract_editor_mode import AbstractEditorMode
from megabone.editor.item import BoneGraphicsItem
from megabone.IKSolver import FABRIK


class IKMode(AbstractEditorMode):
    def __init__(self, editor):
        super().__init__(editor)
        self.ik_chain = None
        self.target_indicator = None
        self.dragging = False

    def enter(self):
        self.editor.setCursor(Qt.CrossCursor)
        # Create IK target indicator
        if not self.target_indicator:
            self.target_indicator = QGraphicsEllipseItem(-5, -5, 10, 10)
            self.target_indicator.setPen(QPen(Qt.red, 1))
            self.target_indicator.hide()
            self.editor.scene.addItem(self.target_indicator)

    def exit(self):
        if self.target_indicator:
            self.target_indicator.hide()

    def mousePressEvent(self, event, scene_pos):
        if event.button() == Qt.LeftButton:
            # Check if we clicked on a bone
            item = self.editor.scene.itemAt(scene_pos, self.editor.transform())
            if isinstance(item, BoneGraphicsItem):
                # Create IK chain from clicked bone up to root or branch
                # We have to take into account if the bone is not an end effector
                # in that case we need the chain from the selected bone up to the last child bone
                bones = []
                current_bone = item

                if len(current_bone.child_bones) == 0:
                    pass

                # no child bones, this is the end effector
                # build the chain up to the root bone
                while current_bone:
                    bones.insert(0, current_bone)
                    # Stop at branch point or root
                    if (
                        not current_bone.parent_bone
                        or len(current_bone.parent_bone.child_bones) > 1
                    ):
                        break
                    current_bone = current_bone.parent_bone

                self.ik_chain = FABRIK(bones)
                self.target_indicator.setPos(scene_pos)
                self.target_indicator.show()
                self.dragging = True

    def mouseMoveEvent(self, event, scene_pos):
        if self.dragging and self.ik_chain:
            self.target_indicator.setPos(scene_pos)
            # solve the chain and try to move to the mouse position
            self.ik_chain.solve(scene_pos)

            # Update attached sprites
            for bone in self.ik_chain.bones:
                for sprite in bone.connected_sprites:
                    new_pos = bone.end_point + sprite.bone_offset
                    sprite.setPos(new_pos)
                    new_rotation = (
                        math.degrees(bone.calculateAngle()) + sprite.initial_rotation
                    )
                    sprite.setRotation(new_rotation)

    def mouseReleaseEvent(self, event, scene_pos):
        if event.button() == Qt.LeftButton:
            self.dragging = False
            self.ik_chain = None
            self.target_indicator.hide()
