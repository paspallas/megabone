from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QGraphicsView

from .editor_mode_register import AbstractEditorMode, EditorModeRegistry, EditorType
from megabone.editor.item import BoneGraphicsItem, AnimatedSpriteItem


@EditorModeRegistry.register("Attach sprite to bone", "A")
class SpriteAttachmentMode(AbstractEditorMode):
    def __init__(self, editor: EditorType):
        super().__init__(editor)

    def activate(self):
        self.editor.setDragMode(QGraphicsView.NoDrag)
        self.editor.setCursor(Qt.PointingHandCursor)

    def mousePressEvent(self, event, scene_pos):
        if event.button() == Qt.LeftButton:
            item = self.editor.scene.itemAt(scene_pos, self.editor.transform())
            if isinstance(item, AnimatedSpriteItem):
                self.editor.selectSprite(item)
            elif isinstance(item, BoneGraphicsItem) and self.editor.selected_sprite:
                self.editor.attachSpriteToBone(self.editor.selected_sprite, item)

    def mouseMoveEvent(self, event, scene_pos):
        pass

    def mouseReleaseEvent(self, event, scene_pos):
        pass
