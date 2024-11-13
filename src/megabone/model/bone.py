from dataclasses import dataclass
from typing import Optional

from .collection import BaseCollectionModel
from .serializable import Serializable


@dataclass
class BoneData(Serializable):
    parent_id: Optional[str]
    position: tuple[float, float]


class BoneModel(BaseCollectionModel):
    def __init__(self):
        super().__init__(BoneData)
