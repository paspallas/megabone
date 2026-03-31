from megabone.editor.item import BoneItem, SpriteItem
from megabone.qt import QGraphicsView, Qt

from .abstract_mode import AbstractEditorMode
from .editor_mode_register import EditorModeRegistry


@EditorModeRegistry.register("Select scene items", "S")
class SelectionMode(AbstractEditorMode):
    def __init__(self, controller):
        super().__init__(controller)
        self.dragging = False
        self.last_pos = None

    def activate(self):
        self.view.setDragMode(QGraphicsView.DragMode.RubberBandDrag)
        self.view.setCursor(Qt.CursorShape.ArrowCursor)

    def mousePressEvent(self, event, scene_pos):
        pass
        # if event.button() == Qt.MouseButton.LeftButton:
        #     item = self.scene.itemAt(scene_pos, self.view.transform())
        #     if item:
        #         if isinstance(item, BoneItem):
        #             self.view.selectBone(item)
        #         elif isinstance(item, SpriteItem):
        #             self.view.selectSprite(item)
        #     else:
        #         self.view.clearSelection()

    def mouseMoveEvent(self, event, scene_pos):
        pass

    def mouseReleaseEvent(self, event, scene_pos):
        pass
