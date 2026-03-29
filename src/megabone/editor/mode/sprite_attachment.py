import math

from megabone.editor.item import BoneItem, SpriteItem
from megabone.model.attachment import AttachmentData
from megabone.model.collection import UpdateSource
from megabone.qt import QGraphicsItem, QGraphicsView, Qt

from .abstract_mode import AbstractEditorMode
from .editor_mode_register import EditorModeRegistry
from .selection import SelectionMode


@EditorModeRegistry.register("Attach sprite to bone", "A")
class SpriteAttachMode(AbstractEditorMode):
    def __init__(self, controller):
        super().__init__(controller)

        self._target_bone: BoneItem | None = None

    def enter_for_bone(self, bone: BoneItem) -> None:
        """Called from context menu"""

        self._target_bone = bone
        self.activate()

    def activate(self):
        self.view.setDragMode(QGraphicsView.DragMode.NoDrag)
        self.view.setCursor(Qt.CursorShape.PointingHandCursor)

        # Lock bone items
        for item in self.scene.items():
            if isinstance(item, BoneItem):
                item.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsSelectable, False)
            elif isinstance(item, SpriteItem):
                item.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsSelectable, True)

    def mousePressEvent(self, event, scene_pos):
        if event.button() != Qt.MouseButton.LeftButton:
            return

        item = self.scene.itemAt(scene_pos, self.view.transform())
        if isinstance(item, SpriteItem) and self._target_bone:
            self._attach(item)
            self.controller.set_edit_mode(SelectionMode)

    def mouseMoveEvent(self, event, scene_pos):
        pass

    def mouseReleaseEvent(self, event, scene_pos):
        pass

    def _attach(self, sprite: SpriteItem) -> None:
        assert self._target_bone is not None
        bone = self._target_bone

        assert bone.end_point is not None
        offset = sprite.pos() - bone.end_point
        rot_offset = sprite.rotation() - math.degrees(bone.calculate_angle())

        attachment = AttachmentData(
            bone_id=bone.item_id,
            sprite_id="00",
            offset=offset,
            rotation_offset=rot_offset,
        )

        self.attachment_model.add_item(attachment, UpdateSource.VIEW)
