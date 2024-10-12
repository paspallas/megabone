from abc import ABC, abstractmethod


class AbstractEditorMode(ABC):
    def __init__(self, editor):
        self.editor = editor

    @abstractmethod
    def mousePressEvent(self, event, scene_pos):
        pass

    @abstractmethod
    def mouseMoveEvent(self, event, scene_pos):
        pass

    @abstractmethod
    def mouseReleaseEvent(self, event, scene_pos):
        pass

    def enter(self):
        """Called when entering this state"""
        pass

    def exit(self):
        """Called when exiting this state"""
        pass
