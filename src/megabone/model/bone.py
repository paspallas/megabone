from dataclasses import dataclass
from typing import Optional

from PyQt5.QtCore import QPointF

from .collection import BaseCollectionModel
from .serializable import Serializable


@dataclass
class BoneData(Serializable):
    start_point: Optional[QPointF] = None
    end_point: Optional[QPointF] = None
    z_index: Optional[int] = 0
    parent_id: Optional[str] = ""
    sprite_id: Optional[str] = ""

    def __post_init__(self):
        super().__post_init__()
        if not self.start_point or not self.end_point:
            self.start_point = QPointF(0, 0)
            self.end_point = QPointF(0, 0)


class BoneModel(BaseCollectionModel):
    def __init__(self):
        super().__init__(BoneData, "bones")
