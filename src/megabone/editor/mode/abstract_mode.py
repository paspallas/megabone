from abc import ABC, abstractmethod

from megabone.model.attachment import AttachmentModel
from megabone.model.bone import BoneModel
from megabone.model.document import Document
from megabone.model.keyframe import KeyframeModel
from megabone.model.sprite import SpriteModel
from megabone.qt import QGraphicsView
from megabone.views.editor_scene import ModalEditorScene


class AbstractEditorMode(ABC):
    description: str = ""
    icon_path: str | None = None
    shortcut: str | None = None

    def __init__(self, controller):
        self.controller = controller

    @property
    def document(self) -> Document:
        document = self.controller.document_collection.get_active_document()

        assert document is not None
        return document

    @property
    def scene(self) -> ModalEditorScene:
        scene = self.view.scene()

        assert isinstance(scene, ModalEditorScene)
        return scene

    @property
    def view(self) -> QGraphicsView:
        return self.controller.current_view

    @property
    def sprites_model(self) -> SpriteModel:
        return self.document.sprites

    @property
    def bones_model(self) -> BoneModel:
        return self.document.bones

    @property
    def attachment_model(self) -> AttachmentModel:
        return self.document.attachments

    @property
    def keys_model(self) -> KeyframeModel:
        return self.document.keyframes

    def activate(self):
        """Called when entering this state"""
        pass

    def deactivate(self):
        """Called when exiting this state"""
        pass

    @abstractmethod
    def mousePressEvent(self, event, scene_pos):
        raise NotImplementedError

    @abstractmethod
    def mouseMoveEvent(self, event, scene_pos):
        raise NotImplementedError

    @abstractmethod
    def mouseReleaseEvent(self, event, scene_pos):
        raise NotImplementedError
