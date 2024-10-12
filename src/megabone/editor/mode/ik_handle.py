from PyQt5.QtCore import Qt

from .abstract_editor_mode import AbstractEditorMode
from megabone.editor.item import BoneGraphicsItem
from megabone.editor.gizmo import IKHandle


class IKHandleMode(AbstractEditorMode):
    def __init__(self, editor):
        super().__init__(editor)
        self.creating_handle = False
        self.start_bone = None

    def enter(self):
        self.editor.setCursor(Qt.CrossCursor)

    def mousePressEvent(self, event, scene_pos):
        if event.button() == Qt.LeftButton:
            item = self.editor.scene.itemAt(scene_pos, self.editor.transform())

            if isinstance(item, BoneGraphicsItem):
                if not self.creating_handle:
                    # Start creating handle
                    self.creating_handle = True
                    self.start_bone = item
                    self.editor.setCursor(Qt.DragLinkCursor)
                else:
                    # Finish creating handle
                    handle = IKHandle(self.start_bone, item)
                    self.editor.scene.addItem(handle)
                    self.editor.scene.addItem(handle.target)
                    self.editor.scene.addItem(handle.pole)
                    self.creating_handle = False
                    self.start_bone = None
                    self.editor.setCursor(Qt.CrossCursor)

    def mouseMoveEvent(self, event, scene_pos):
        pass

    def mouseReleaseEvent(self, event, scene_pos):
        pass
