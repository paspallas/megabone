from dataclasses import dataclass, field

from PyQt5.QtCore import QPointF

from .collection import BaseCollectionModel
from .serializable import Serializable


@dataclass
class BoneData(Serializable):
    start_point: QPointF = field(default_factory=lambda: QPointF(0, 0))
    end_point: QPointF = field(default_factory=lambda: QPointF(0, 0))
    z_index: int = 0
    parent_id: str = ""
    sprite_id: str = ""


class BoneModel(BaseCollectionModel):
    def __init__(self):
        super().__init__(BoneData, "bones")
