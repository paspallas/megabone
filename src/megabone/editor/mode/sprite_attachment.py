from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QGraphicsView

from megabone.editor.item import BoneItem, SpriteItem

from .abstract_mode import AbstractEditorMode
from .editor_mode_register import EditorModeRegistry


@EditorModeRegistry.register("Attach sprite to bone", "A")
class SpriteAttachmentMode(AbstractEditorMode):
    def __init__(self, controller):
        super().__init__(controller)

    def activate(self):
        self.view.setDragMode(QGraphicsView.NoDrag)
        self.view.setCursor(Qt.PointingHandCursor)

    def mousePressEvent(self, event, scene_pos):
        if event.button() == Qt.LeftButton:
            item = self.scene.itemAt(scene_pos, self.view.transform())
            if isinstance(item, SpriteItem):
                self.view.selectSprite(item)
            elif isinstance(item, BoneItem) and self.view.selected_sprite:
                self.view.attachSpriteToBone(self.view.selected_sprite, item)

    def mouseMoveEvent(self, event, scene_pos):
        pass

    def mouseReleaseEvent(self, event, scene_pos):
        pass
