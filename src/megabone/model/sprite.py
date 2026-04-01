from dataclasses import dataclass, field

from megabone.qt import QPixmap
from megabone.util.types import Point

from .collection import BaseCollectionModel
from .serializable import Serializable


@dataclass
class FrameData:
    index: int
    pixmap: QPixmap = field(repr=False)


@dataclass
class SpriteSheetData:
    path: str
    frame_width: int
    frame_height: int
    frames: list[FrameData] = field(default_factory=list)


@dataclass
class SpriteData(Serializable):
    name: str = "sprite"
    path: str = ""
    bone_id: str = ""
    frame_index: int = 0
    offset: Point = field(default_factory=lambda: Point())
    position: Point = field(default_factory=lambda: Point())
    rotation: float = 0.0


class SpriteModel(BaseCollectionModel):
    def __init__(self):
        super().__init__(SpriteData, "sprites")
