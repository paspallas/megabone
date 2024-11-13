from dataclasses import dataclass
from typing import Optional

from .collection import BaseCollectionModel
from .serializable import Serializable


@dataclass
class BoneData(Serializable):
    start_point: tuple[float, float]
    end_point: tuple[float, float]
    parent_id: Optional[str] = ""


class BoneModel(BaseCollectionModel):
    def __init__(self):
        super().__init__(BoneData, "bones")
