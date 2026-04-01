from megabone.model.bone import BoneData
from megabone.model.collection import UpdateSource
from megabone.model.document import Document
from megabone.qt import QUndoCommand
from megabone.util.types import Point

from .document import DocumentCommand


class MoveBoneCommand(DocumentCommand):
    def __init__(
        self, document: Document, bone_id: str, old_end: Point, new_end: Point
    ):
        super().__init__(document, "Move Bone")
        self._bone_id = bone_id
        self._old_end = old_end
        self._new_end = new_end

    def id(self) -> int:
        return 1001

    def mergeWith(self, other: QUndoCommand) -> bool:
        if not isinstance(other, MoveBoneCommand):
            return False

        if other._bone_id != self._bone_id:
            return False

        self._new_end = other._new_end
        return True

    def redo(self) -> None:
        data = self._document.bones.get_item(self._bone_id)
        data.end_point = self._new_end
        self._document.bones.update_item(data, UpdateSource.COMMAND)

    def undo(self) -> None:
        data = self._document.bones.get_item(self._bone_id)
        data.end_point = self._old_end
        self._document.bones.modify_item(data, UpdateSource.COMMAND)


class CreateBoneCommand(DocumentCommand):
    def __init__(self, document: Document, bone_data: BoneData):
        super().__init__(document, f"Create {bone_data.name}")
        self._bone_data = bone_data

    def redo(self) -> None:
        self._document.bones.add_item(self._bone_data, UpdateSource.COMMAND)

    def undo(self) -> None:
        self._document.bones.remove_item(self._bone_data.id, UpdateSource.COMMAND)


class DeleteBoneCommand(DocumentCommand):
    def __init__(self, document: Document, bone_id: str):
        super().__init__(document, "Delete Bone")
        self._bone_id = bone_id

        # Snapshot full state before deletion
        self._bone_data = document.bones.get_item(bone_id)
        # self._attachments = document.attachments.get_items_for_bone(bone_id)

    def redo(self) -> None:
        # for att in self._attachments:
        #     self._document.attachments.remove_item(att.id, UpdateSource.COMMAND)
        self._document.bones.remove_item(self._bone_id, UpdateSource.COMMAND)

    def undo(self) -> None:
        self._document.bones.add_item(self._bone_data, UpdateSource.COMMAND)
        # for att in self._attachments:
        #     self._document.attachments.add_item(att, UpdateSource.COMMAND)


class RenameBoneCommand(DocumentCommand):
    def __init__(self, document: Document, bone_id: str, old_name: str, new_name: str):
        super().__init__(document, f"Rename to '{new_name}'")
        self._bone_id = bone_id
        self._old_name = old_name
        self._new_name = new_name

    def redo(self) -> None:
        self._set_name(self._new_name)

    def undo(self) -> None:
        self._set_name(self._old_name)

    def _set_name(self, name: str) -> None:
        data = self._document.bones.get_item(self._bone_id)

        assert isinstance(data, BoneData)
        data.name = name
        self._document.bones.modify_item(data, UpdateSource.COMMAND)
