from PyQt5.QtCore import Qt

from megabone.editor.gizmo import IKHandle
from megabone.editor.item import BoneItem

from .abstract_mode import AbstractEditorMode
from .editor_mode_register import EditorModeRegistry


@EditorModeRegistry.register("Create handles for an IK chain", "H")
class IKHandleMode(AbstractEditorMode):
    def __init__(self, controller):
        super().__init__(controller)
        self.creating_handle = False
        self.start_bone = None

    def activate(self):
        self.view.setCursor(Qt.CrossCursor)

    def mousePressEvent(self, event, scene_pos):
        if event.button() == Qt.LeftButton:
            item = self.scene.itemAt(scene_pos, self.view.transform())

            if isinstance(item, BoneItem):
                if not self.creating_handle:
                    # Start creating handle
                    self.creating_handle = True
                    self.start_bone = item
                    self.view.setCursor(Qt.DragLinkCursor)
                else:
                    # Finish creating handle
                    handle = IKHandle(self.start_bone, item)
                    self.scene.addItem(handle)
                    self.scene.addItem(handle.target)
                    self.scene.addItem(handle.pole)

                    self.creating_handle = False
                    self.start_bone = None
                    self.view.setCursor(Qt.CrossCursor)

    def mouseMoveEvent(self, event, scene_pos):
        pass

    def mouseReleaseEvent(self, event, scene_pos):
        pass
