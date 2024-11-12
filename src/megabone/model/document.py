import json
from pathlib import Path
from typing import Optional
from uuid import uuid4 as genid

from PyQt5.QtCore import QObject, pyqtSignal
from PyQt5.QtWidgets import QUndoStack

from .bone import BoneModel
from .sprite import SpriteModel


class Document(QObject):
    """Document model"""

    documentChanged = pyqtSignal()

    def __init__(self) -> None:
        super().__init__()
        self.bones = BoneModel()
        self.sprites = SpriteModel()
        self.undo_stack = QUndoStack()

        self.id = genid().hex
        self.path: Optional[Path] = None

    def save(self, path: Optional[Path] = None) -> None:
        if path:
            self.path = path

        content = {
            "bones": self.bones.serialize(),
            "sprites": self.sprites.serialize(),
        }

        self.path.write_text(json.dumps(content, indent=4), encoding="utf-8")

    @classmethod
    def load(cls, path: Path) -> "Document":
        doc = cls()

        with path.open("r", encoding="utf-8") as f:
            data = json.load(f)

            doc.bones.deserialize(data["bones"])
            doc.sprites.deserialize(data["sprites"])
            doc.path = path

        return doc

    def create_undo_command(self, command) -> None:
        self.undo_stack.push(command)
        self.documentChanged.emit()
