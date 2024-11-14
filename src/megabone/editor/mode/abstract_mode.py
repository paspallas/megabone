from abc import ABC, abstractmethod
from typing import Optional

from megabone.model.bone import BoneModel
from megabone.model.keyframe import KeyframeModel
from megabone.model.sprite import SpriteModel
from megabone.views import MainEditorView, ModalEditorScene


class AbstractEditorMode(ABC):
    description: str = ""
    icon_path: Optional[str] = None
    shortcut: Optional[str] = None

    def __init__(self, controller):
        self.controller = controller

    @property
    def scene(self) -> ModalEditorScene:
        return self.controller.current_view.scene()

    @property
    def view(self) -> MainEditorView:
        return self.controller.current_view

    @property
    def sprites_model(self) -> SpriteModel:
        return self.controller.documents.get_active_document().sprites

    @property
    def bones_model(self) -> BoneModel:
        return self.controller.documents.get_active_document().bones

    @property
    def keys_model(self) -> KeyframeModel:
        return self.controller.documents.get_active_document().keyframes

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
