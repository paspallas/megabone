from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QGraphicsView

from .abstract_editor_mode import AbstractEditorMode
from editor.item import BoneGraphicsItem, AnimatedSpriteItem


class SpriteAttachmentMode(AbstractEditorMode):
    def __init__(self, editor):
        super().__init__(editor)

    def enter(self):
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
