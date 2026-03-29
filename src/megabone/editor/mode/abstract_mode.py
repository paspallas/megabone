from abc import ABC, abstractmethod

from megabone.model.bone import BoneModel
from megabone.model.document import Document
from megabone.model.keyframe import KeyframeModel
from megabone.model.sprite import SpriteModel
from megabone.qt import QGraphicsScene, QGraphicsView


class AbstractEditorMode(ABC):
    description: str = ""
    icon_path: str | None = None
    shortcut: str | None = None

    def __init__(self, controller):
        self.controller = controller

    def _document(self) -> Document:
        document = self.controller.documents.get_active_document()

        assert document is not None
        return document

    @property
    def scene(self) -> QGraphicsScene:
        scene = self.view.scene()

        assert scene is not None
        return scene

    @property
    def view(self) -> QGraphicsView:
        return self.controller.current_view

    @property
    def sprites_model(self) -> SpriteModel:
        return self._document().sprites

    @property
    def bones_model(self) -> BoneModel:
        return self._document().bones

    @property
    def keys_model(self) -> KeyframeModel:
        return self._document().keyframes

    def activate(self):
        """Called when entering this state"""
        pass

    def deactivate(self):
        """Called when exiting this state"""
        pass

    @abstractmethod
    def mousePressEvent(self, event, scene_pos):
        raise NotImplementedError()

    @abstractmethod
    def mouseMoveEvent(self, event, scene_pos):
        raise NotImplementedError()

    @abstractmethod
    def mouseReleaseEvent(self, event, scene_pos):
        raise NotImplementedError()
