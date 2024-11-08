from dataclasses import dataclass
from typing import Dict, Optional

from PyQt5.QtCore import QObject, pyqtSignal


@dataclass
class Bone:
    id: str
    parent_id: Optional[str]
    position: tuple[float, float]


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
