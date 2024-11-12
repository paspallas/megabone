from dataclasses import dataclass
from typing import Any, Dict, List

from PyQt5.QtCore import QObject, pyqtSignal


@dataclass
class Sprite:
    id: str
    image_path: str
    bone_id = str
    offset: tuple[float, float]

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "image_path": self.image_path,
            "bone_id": self.bone_id,
            "offset": self.offset,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Sprite":
        return cls(data["id"], data["image_path"], data["bone_id"], data["offset"])


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

    def serialize(self) -> List[Dict[str, Any]]:
        return [sprite.to_dict() for sprite in self._sprites.values()]

    def deserialize(self, data: List[Dict[str, Any]]) -> None:
        for item in data:
            self.add_sprite(Sprite.from_dict(item))
