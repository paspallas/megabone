import math

from PyQt5.QtCore import Qt, QPointF
from PyQt5.QtWidgets import QGraphicsScene, QGraphicsView

from megabone.viewUtils import PanControl, ZoomControl
from .item import AnimatedSpriteItem, BoneGraphicsItem
from .mode import (
    AnimationMode,
    BoneCreationMode,
    IKHandleMode,
    IKMode,
    SelectionMode,
    SpriteAttachmentMode,
    EditorModeType as Mode
)


class SkeletonEditorScene(QGraphicsScene):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def itemAt(self, position: QPointF, transform):
        items = self.items(position)

        # Check items shape
        for item in items:
            item_pos = item.mapFromScene(position)
            if item.shape().contains(item_pos):
                return item

        return None


class SkeletonEditor(QGraphicsView):
    _width = 2048
    _height = 2048

    def __init__(self, parent=None):
        super().__init__(parent)
        self.scene = SkeletonEditorScene(self)
        self.scene.setSceneRect(-self._width / 2, -self._height / 2, self._width, self._height)
        self.setScene(self.scene)
        self.fitInView(self.scene.sceneRect(), Qt.KeepAspectRatio)

        # Configure the view
        self.setViewportUpdateMode(QGraphicsView.FullViewportUpdate)
        ZoomControl(self)
        PanControl(self)

        # Initialize modes
        self.edit_modes = {
            Mode.Selection: SelectionMode(self),
            Mode.CreateBone: BoneCreationMode(self),
            Mode.AttachSprite: SpriteAttachmentMode(self),
            Mode.MoveIkChain: IKMode(self),
            Mode.CreateIkHandle: IKHandleMode(self),
            Mode.Animation: AnimationMode(self),
        }

        # Default editing mode
        self.current_edit_mode = None
        self.setEditMode(Mode.Selection)

        # Editor properties
        self.selected_sprite = None
        self.selected_bone = None
        self.bones = []

    def setEditMode(self, mode_type: Mode):
        """Change the current edit mode"""
        if self.current_edit_mode:
            self.current_edit_mode.exit()

        self.current_edit_mode = self.edit_modes[mode_type]
        self.current_edit_mode.enter()

    def mousePressEvent(self, event):
        scene_pos = self.mapToScene(event.pos())
        self.current_edit_mode.mousePressEvent(event, scene_pos)
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        scene_pos = self.mapToScene(event.pos())
        self.current_edit_mode.mouseMoveEvent(event, scene_pos)
        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        scene_pos = self.mapToScene(event.pos())
        self.current_edit_mode.mouseReleaseEvent(event, scene_pos)
        super().mouseReleaseEvent(event)

    def selectBone(self, bone):
        self.selected_bone = bone

    def selectSprite(self, sprite):
        if self.selected_sprite:
            self.selected_sprite.setSelected(False)
        self.selected_sprite = sprite
        sprite.setSelected(True)

    def clearSelection(self):
        if self.selected_bone:
            self.selected_bone.setSelected(False)
            self.selected_bone = None
        if self.selected_sprite:
            self.selected_sprite.setSelected(False)
            self.selected_sprite = None

    def attachSpriteToBone(self, sprite: AnimatedSpriteItem, bone: BoneGraphicsItem):
        if sprite.attached_bone:
            sprite.attached_bone.connected_sprites.remove(sprite)

        # Add relationship between bone and sprite
        bone.connected_sprites.append(sprite)
        sprite.attached_bone = bone
        sprite.bone_offset = sprite.pos() - bone.end_point
        sprite.initial_rotation = sprite.rotation() - math.degrees(
            bone.calculateAngle()
        )

    def addSprite(self, pixmap, pos):
        sprite = AnimatedSpriteItem(pixmap)
        sprite.setPos(pos)
        self.scene.addItem(sprite)
        return sprite

    def selectSprite(self, sprite):
        if self.selected_sprite:
            self.selected_sprite.setSelected(False)
        self.selected_sprite = sprite
        sprite.setSelected(True)
