from dataclasses import dataclass, field

from PyQt5.QtCore import QPointF

from .collection import BaseCollectionModel
from .serializable import Serializable


@dataclass
class SpriteData(Serializable):
    offset: QPointF = field(default_factory=lambda: QPointF(0, 0))
    image_path: str = ""
    bone_id: str = ""
    z_index: int = 0


class SpriteModel(BaseCollectionModel):
    def __init__(self):
        super().__init__(SpriteData, "sprites")
