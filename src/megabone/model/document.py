import json
import uuid
from pathlib import Path

from megabone.command.document import DocumentCommand
from megabone.qt import QObject, QUndoStack, Signal

from .attachment import AttachmentModel
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

        # Connect to collections signals
        for model in [self.bones, self.sprites, self.keyframes, self.attachments]:
            model.itemAdded.connect(self._on_content_changed)
            model.itemModified.connect(self._on_content_changed)
            model.itemRemoved.connect(self._on_content_changed)

    def get_all_collections(self) -> list[BaseCollectionModel]:
        return [self.bones, self.sprites, self.keyframes, self.attachments]

    def to_dict(self) -> dict:
        """Serialize document to dictionary"""

        return {
            collection.key_name: collection.to_list()
            for collection in self.get_all_collections()
        }

    def from_dict(self, data: dict) -> "Document":
        """Load document from dictionary"""

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

    def _on_content_changed(self, *args):
        self.documentModified.emit()
