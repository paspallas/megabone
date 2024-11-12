import json
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
        self.file_path: Optional[str] = None

    def save(self, file_path: Optional[str] = None) -> None:
        if file_path:
            self.file_path = file_path

        content = {
            "id": self.id,
            "bones": self.bones.serialize(),
            "sprites": self.sprites.serialize(),
        }

        with open(self.file_path, "w", encoding="utf-8") as f:
            f.write(json.dumps(content, indent=4))

    @classmethod
    def load(cls, file_path: str) -> "Document":
        doc = cls()

        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)

            doc.bones.deserialize(data["bones"])
            doc.sprites.deserialize(data["sprites"])
            doc.file_path = file_path

        return doc

    def create_undo_command(self, command) -> None:
        self.undo_stack.push(command)
        self.documentChanged.emit()
