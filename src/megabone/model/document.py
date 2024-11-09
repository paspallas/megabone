import json
from pathlib import Path
from typing import Optional

from PyQt5.QtCore import QObject, pyqtSignal
from PyQt5.QtWidgets import QMessageBox, QUndoStack

from .bone import BoneModel
from .sprite import SpriteModel


class Document(QObject):
    document_changed = pyqtSignal()

    def __init__(self) -> None:
        super().__init__()

        self.bones = BoneModel()
        self.sprites = SpriteModel()
        self.undo_stack = QUndoStack()
        self._file_path: Optional[Path] = None

    def save(self, file_path: Optional[Path] = None) -> bool:
        if file_path:
            self._file_path = file_path

        if not self._file_path:
            return False

        document_data = {
            "bones": [self._bone_to_dict(bone) for bone in self.bones._bones.values()],
            "sprites": [
                self._sprites_to_dict(sprite)
                for sprite in self.sprites._sprites.values()
            ],
        }

        try:
            with self._file_path.open("w", encoding="utf-8") as f:
                json.dump(document_data, f)
            return True
        except Exception as e:
            QMessageBox.critical("Couldn't save file.")
            return False

    @classmethod
    def load(cls, file_path: Path) -> "Document":
        doc = cls()
        try:
            with file_path.open("r", encoding="utf-8") as f:
                data = json.load(f)

            # Load bone data first to maintain hierarchy
            for bone_data in data["bones"]:
                doc.bones.add_bone(cls._dict_to_bone(bone_data))

            for sprite_data in data["sprites"]:
                doc.sprites.add_sprite(cls._dict_to_sprite(sprite_data))

            doc._file_path = file_path
            return doc

        except Exception as e:
            # Open error window
            return None

    def create_undo_command(self, command) -> None:
        self.undo_stack.push(command)
        self.document_changed.emit()
