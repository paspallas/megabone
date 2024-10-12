from PyQt5.QtCore import Qt

from .abstract_editor_mode import AbstractEditorMode
from megabone.editor.gizmo import IKHandle
from megabone.editor.item import BoneGraphicsItem, AnimatedSpriteItem
from megabone.model import PropertyType


class AnimationMode(AbstractEditorMode):
    def __init__(self, editor):
        super().__init__(editor)
        self.selected_track = None

    def enter(self):
        self.editor.setCursor(Qt.CrossCursor)

    def mouseMoveEvent(self, event, scene_pos):
        pass

    def mouseReleaseEvent(self, event, scene_pos):
        pass

    def mousePressEvent(self, event, scene_pos):
        if event.button() == Qt.LeftButton:
            # Get clicked item
            item = self.editor.scene.itemAt(scene_pos, self.editor.transform())

            if isinstance(item, (BoneGraphicsItem, IKHandle, AnimatedSpriteItem)):
                # If we have a selected track and it matches the item type
                if self.selected_track and isinstance(
                    item, self.selected_track.target.__class__
                ):
                    # Add keyframe at current frame
                    current_frame = (
                        self.editor.animation_player.current_animation.current_frame
                    )

                    if isinstance(item, BoneGraphicsItem):
                        value = item.calculateAngle()
                    elif isinstance(item, IKHandle):
                        if self.selected_track.property_type == PropertyType.IK_TARGET:
                            value = item.target.pos()
                        else:  # IK_POLE
                            value = item.pole.pos()
                    else:  # AnimatedSprite
                        if self.selected_track.property_type == PropertyType.POSITION:
                            value = item.pos()
                        elif (
                            self.selected_track.property_type
                            == PropertyType.SPRITE_OFFSET
                        ):
                            value = item.bone_offset

                    self.selected_track.addKeyframe(current_frame, value)
                    self.editor.animation_player.updateUI()
