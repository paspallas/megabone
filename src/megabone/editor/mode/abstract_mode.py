from abc import ABC, abstractmethod
from typing import Optional

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

    def activate(self):
        """Called when entering this state"""
        pass

    def deactivate(self):
        """Called when exiting this state"""
        pass

    @abstractmethod
    def mousePressEvent(self, event, scene_pos):
        pass

    @abstractmethod
    def mouseMoveEvent(self, event, scene_pos):
        pass

    @abstractmethod
    def mouseReleaseEvent(self, event, scene_pos):
        pass
