from dataclasses import dataclass, field

from megabone.qt import QPixmap

from .collection import BaseCollectionModel
from .serializable import Serializable


@dataclass
class FrameData:
    index: int
    pixmap: QPixmap = field(repr=False)  # not serialized


@dataclass
class SpriteSheetData:
    path: str
    frame_width: int
    frame_height: int
    frames: list[FrameData] = field(default_factory=list)


@dataclass
class SpriteData(Serializable):
    item_id: str = ""
    name: str = "sprite"
    image_path: str = ""
    offset: tuple[float, float] = (0.0, 0.0)
    position: tuple[float, float] = (0.0, 0.0)
    bone_id: str = ""
    z_index: int = 0
    visible: bool = True


class SpriteModel(BaseCollectionModel):
    def __init__(self):
        super().__init__(SpriteData, "sprites")
