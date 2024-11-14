from dataclasses import dataclass
from typing import Optional

from .collection import BaseCollectionModel
from .serializable import Serializable


@dataclass
class SpriteData(Serializable):
    offset: tuple[float, float] = (0, 0)
    image_path: str = ""
    bone_id: Optional[str] = ""
    z_index: Optional[int] = 0


class SpriteModel(BaseCollectionModel):
    def __init__(self):
        super().__init__(SpriteData, "sprites")
