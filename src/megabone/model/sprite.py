from dataclasses import dataclass
from typing import Optional

from .collection import BaseCollectionModel
from .serializable import Serializable


@dataclass
class SpriteData(Serializable):
    image_path: str
    offset: tuple[float, float]
    bone_id: Optional[str] = ""
    z_index: Optional[int] = 0


class SpriteModel(BaseCollectionModel):
    def __init__(self):
        super().__init__(SpriteData, "sprites")
