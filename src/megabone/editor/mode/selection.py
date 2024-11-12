from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QGraphicsView

from megabone.editor.item import BoneItem, SpriteItem

from .abstract_mode import AbstractEditorMode
from .editor_mode_register import EditorModeRegistry


@EditorModeRegistry.register("Select scene items", "S")
class SelectionMode(AbstractEditorMode):
    def __init__(self, controller):
        super().__init__(controller)
        self.dragging = False
        self.last_pos = None

    def activate(self):
        self.view.setDragMode(QGraphicsView.RubberBandDrag)
        self.view.setCursor(Qt.ArrowCursor)

    def mousePressEvent(self, event, scene_pos):
        if event.button() == Qt.LeftButton:
            item = self.scene.itemAt(scene_pos, self.view.transform())
            if item:
                if isinstance(item, BoneItem):
                    self.view.selectBone(item)
                elif isinstance(item, SpriteItem):
                    self.view.selectSprite(item)
            else:
                self.view.clearSelection()

    def mouseMoveEvent(self, event, scene_pos):
        pass

    def mouseReleaseEvent(self, event, scene_pos):
        pass
