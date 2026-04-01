from megabone.model.collection import UpdateSource
from megabone.model.document import Document
from megabone.model.sprite import SpriteData
from megabone.util.types import Point

from .document import DocumentCommand


class CreateSpriteCommand(DocumentCommand):
    def __init__(self, document: Document, data: SpriteData):
        super().__init__(document, f"Create {data.name}")
        self._data = data

    def redo(self) -> None:
        self._document.sprites.add_item(self._data, UpdateSource.COMMAND)

    def undo(self) -> None:
        self._document.sprites.remove_item(self._data.id, UpdateSource.COMMAND)


class DeleteSpriteCommand(DocumentCommand):
    def __init__(self, document: Document, sprite_id: str):
        super().__init__(document, "Delete Sprite")
        # Snapshot full state before deletion
        self._data = document.sprites.get_item(sprite_id)
        self._attachments = document.attachments.get_items_for_sprite(sprite_id)

    def redo(self) -> None:
        for att in self._attachments:
            self._document.attachments.remove_item(att.id, UpdateSource.COMMAND)

        assert self._data is not None
        self._document.sprites.remove_item(self._data.id, UpdateSource.COMMAND)

    def undo(self) -> None:
        self._document.sprites.add_item(self._data, UpdateSource.COMMAND)
        for att in self._attachments:
            self._document.attachments.add_item(att, UpdateSource.COMMAND)


class MoveSpriteCommand(DocumentCommand):
    def __init__(
        self,
        document: Document,
        sprite_id: str,
        old_pos: Point,
        new_pos: Point,
    ):
        super().__init__(document, "Move Sprite")
        self._sprite_id = sprite_id
        self._old_pos = old_pos
        self._new_pos = new_pos

    def mergeWith(self, other) -> bool:
        if not isinstance(other, MoveSpriteCommand):
            return False
        if other._sprite_id != self._sprite_id:
            return False
        self._new_pos = other._new_pos
        return True

    def redo(self) -> None:
        self._apply(self._new_pos)

    def undo(self) -> None:
        self._apply(self._old_pos)

    def _apply(self, pos: Point) -> None:
        data = self._document.sprites.get_item(self._sprite_id)

        assert isinstance(data, SpriteData)
        data.position = pos
        self._document.sprites.modify_item(data, UpdateSource.COMMAND)


class ChangeFrameCommand(DocumentCommand):
    def __init__(
        self, document: Document, sprite_id: str, old_frame: int, new_frame: int
    ):
        super().__init__(document, "Change Frame")
        self._sprite_id = sprite_id
        self._old_frame = old_frame
        self._new_frame = new_frame

    def redo(self) -> None:
        self._apply(self._new_frame)

    def undo(self) -> None:
        self._apply(self._old_frame)

    def _apply(self, frame_index: int) -> None:
        data = self._document.sprites.get_item(self._sprite_id)
        data.frame_index = frame_index
        self._document.sprites.modify_item(data, UpdateSource.COMMAND)
