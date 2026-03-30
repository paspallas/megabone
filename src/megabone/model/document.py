import json
import uuid
from pathlib import Path

from megabone.qt import QObject, QUndoStack, Signal

from .attachment import AttachmentModel
from .base_command import DocumentCommand
from .bone import BoneModel
from .collection import BaseCollectionModel
from .keyframe import KeyframeModel
from .sprite import SpriteModel


class Document(QObject):
    """Document model"""

    documentModified = Signal()

    def __init__(self, path: Path | None = None) -> None:
        super().__init__()
        self.doc_id = uuid.uuid4().hex
        self.path = path
        self.bones = BoneModel()
        self.sprites = SpriteModel()
        self.keyframes = KeyframeModel()
        self.attachments = AttachmentModel()
        self.undo_stack = QUndoStack()

        # Connect submodel signals
        for model in [self.bones, self.sprites, self.keyframes, self.attachments]:
            model.itemAdded.connect(self._on_content_changed)
            model.itemModified.connect(self._on_content_changed)
            model.itemRemoved.connect(self._on_content_changed)

    def get_all_collections(self) -> list[BaseCollectionModel]:
        return [self.bones, self.sprites]

    def to_dict(self) -> dict:
        """Serialize document to dictionary"""

        return {
            "doc_id": self.doc_id,
            self.bones.key_name: self.bones.to_list(),
            self.sprites.key_name: self.sprites.to_list(),
            self.attachments.key_name: self.attachments.to_list(),
            self.keyframes.key_name: self.keyframes.to_list(),
        }

    def from_dict(self, data: dict) -> "Document":
        """Load document from dictionary"""

        self.doc_id = data.get("doc_id", self.doc_id)
        self.bones.from_list(data.get(self.bones.key_name, []))
        self.sprites.from_list(data.get(self.sprites.key_name, []))
        self.attachments.from_list(data.get(self.attachments.key_name, []))
        self.keyframes.from_list(data.get(self.keyframes.key_name, []))

        return self

    def save(self, path: Path | None = None) -> None:
        if path:
            self.path = path

        assert self.path is not None, "No file save path set"
        self.path.write_text(json.dumps(self.to_dict(), indent=4), encoding="utf-8")

    @staticmethod
    def load(path: Path) -> "Document":
        with path.open("r", encoding="utf-8") as f:
            return Document(path).from_dict(json.load(f))

    def push(self, command: DocumentCommand) -> None:
        self.undo_stack.push(command)
        self.documentModified.emit()

    def _on_content_changed(self, *args):
        self.documentModified.emit()
