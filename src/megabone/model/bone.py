import uuid
from dataclasses import dataclass
from typing import Optional

from .collection import BaseCollectionModel
from .serializable import Serializable


@dataclass
class BoneData(Serializable):
    start_point: tuple[float, float]
    end_point: tuple[float, float]
    z_index: Optional[int] = 0
    parent_id: Optional[str] = ""
    sprite_id: Optional[str] = ""

    @staticmethod
    def create() -> "BoneData":
        return BoneData(
            id=uuid.uuid4().hex, start_point=(0.0, 0.0), end_point=(0.0, 0.0)
        )


class BoneModel(BaseCollectionModel):
    def __init__(self):
        super().__init__(BoneData, "bones")
