import json
from pathlib import Path
from typing import Optional
from uuid import uuid4 as genid

from PyQt5.QtCore import QObject, pyqtSignal
from PyQt5.QtWidgets import QUndoStack

from .bone import BoneModel
from .keyframe import KeyframeModel
from .sprite import SpriteModel


class Document(QObject):
    """Document model"""

    documentModified = pyqtSignal()

    def __init__(self) -> None:
        super().__init__()
        self.id = genid().hex
        self.bones = BoneModel()
        self.sprites = SpriteModel()
        self.keyframes = KeyframeModel()
        self.undo_stack = QUndoStack()

        self.path: Optional[Path] = None

        # Connect submodel signals
        for model in [self.bones, self.sprites, self.keyframes]:
            model.itemAdded.connect(self._on_content_changed)
            model.itemModified.connect(self._on_content_changed)
            model.itemRemoved.connect(self._on_content_changed)

    def to_dict(self) -> dict:
        """Serialize document to dictionary"""
        return {
            "id": self.id,
            "bones": self.bones.to_dict(),
            "sprites": self.sprites.to_dict(),
            "keyframes": self.keyframes.to_dict(),
        }

    def from_dict(self, data: dict) -> "Document":
        """Load document from dictionary"""
        self.id = data.get("id", self.id)
        self.bones.from_dict(data.get("bones", {"items": {}}))
        self.sprites.from_dict(data.get("sprites", {"items": {}}))
        self.keyframes.from_dict(data.get("keyframes", {"items": {}}))

        return self

    def save(self, path: Optional[Path] = None) -> None:
        if path:
            self.path = path
        self.path.write_text(json.dumps(self.to_dict(), indent=4), encoding="utf-8")

    @staticmethod
    def load(path: Path) -> "Document":
        with path.open("r", encoding="utf-8") as f:
            return Document().from_dict(json.load(f))

    def create_undo_command(self, command) -> None:
        self.undo_stack.push(command)
        self.documentModified.emit()

    def _on_content_changed(self, *args):
        self.documentModified.emit()
