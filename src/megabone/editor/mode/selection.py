from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QGraphicsView

from .abstract_editor_mode import AbstractEditorMode
from megabone.editor.item import BoneGraphicsItem, AnimatedSpriteItem


class SelectionMode(AbstractEditorMode):
    def __init__(self, editor):
        super().__init__(editor)
        self.dragging = False
        self.last_pos = None

    def enter(self):
        self.editor.setDragMode(QGraphicsView.RubberBandDrag)
        self.editor.setCursor(Qt.ArrowCursor)

    def mousePressEvent(self, event, scene_pos):
        if event.button() == Qt.LeftButton:
            item = self.editor.scene.itemAt(scene_pos, self.editor.transform())
            if item:
                if isinstance(item, BoneGraphicsItem):
                    self.editor.selectBone(item)
                elif isinstance(item, AnimatedSpriteItem):
                    self.editor.selectSprite(item)
            else:
                self.editor.clearSelection()

    def mouseMoveEvent(self, event, scene_pos):
        pass

    def mouseReleaseEvent(self, event, scene_pos):
        pass
