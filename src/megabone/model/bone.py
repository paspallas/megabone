from dataclasses import dataclass
from typing import Any, Dict, List, Optional

from PyQt5.QtCore import QObject, pyqtSignal


@dataclass
class Bone:
    id: str
    parent_id: Optional[str]
    position: tuple[float, float]

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "parent_id": self.parent_id,
            "position": (self.position[0], self.position[1]),
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Bone":
        return cls(data["id"], data["parent_id"], data["position"])


class BoneModel(QObject):
    bone_added = pyqtSignal(Bone)
    bone_modified = pyqtSignal(str, Bone)
    bone_removed = pyqtSignal(str)

    def __init__(self) -> None:
        super().__init__()
        self._bones: Dict[str, Bone] = {}

    def add_bone(self, bone: Bone) -> None:
        self._bones[bone.id] = bone
        self.bone_added.emit(bone)

    def serialize(self) -> List[Dict[str, Any]]:
        return [bone.to_dict() for bone in self._bones.values()]

    def deserialize(self, data: List[Dict[str, Any]]) -> None:
        for item in data:
            self.add_bone(Bone.from_dict(data))
