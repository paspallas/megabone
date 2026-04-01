from dataclasses import dataclass, field

from megabone.util.types import Point

from .collection import BaseCollectionModel
from .serializable import Serializable


@dataclass
class BoneData(Serializable):
    name: str = "bone"
    sprite_id: str = ""
    parent_id: str = ""
    z_index: int = 0
    start_point: Point = field(default_factory=lambda: Point())
    end_point: Point = field(default_factory=lambda: Point())


class BoneModel(BaseCollectionModel):
    def __init__(self):
        super().__init__(BoneData, "bones")
