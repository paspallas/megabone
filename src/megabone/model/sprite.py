from dataclasses import dataclass
from typing import Dict

from PyQt5.QtCore import QObject, pyqtSignal


@dataclass
class Sprite:
    id: str
    image_path: str
    bone_id = str
    offset: tuple[float, float]


class SpriteModel(QObject):
    sprite_added = pyqtSignal(Sprite)
    sprite_modified = pyqtSignal(str, Sprite)
    sprite_removed = pyqtSignal(str)

    def __init__(self) -> None:
        super().__init__()
        self._sprites: Dict[str, Sprite] = {}

    def add_sprite(self, sprite: Sprite) -> None:
        self._sprites[sprite.id] = sprite
        self.sprite_added.emit(sprite)
