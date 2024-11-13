from dataclasses import dataclass

from .collection import BaseCollectionModel
from .serializable import Serializable


@dataclass
class SpriteData(Serializable):
    image_path: str
    bone_id = str
    offset: tuple[float, float]


class SpriteModel(BaseCollectionModel):
    def __init__(self):
        super().__init__(SpriteData, "sprites")
