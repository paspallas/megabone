from dataclasses import dataclass
from enum import Enum, auto
from typing import Any

from PyQt5.QtCore import QPointF

from .collection import BaseCollectionModel
from .serializable import Serializable


class EaseType(Enum):
    LINEAR = auto()
    EASE_IN = auto()
    EASE_OUT = auto()


@dataclass
class KeyframeData(Serializable):
    bone_id: str = ""
    frame: int = 0
    value: Any = None
    easing: EaseType = EaseType.LINEAR

    def interpolate(self, other, t):
        """Interpolate between this keyframe and another"""
        if isinstance(self.value, QPointF):
            return QPointF(
                self._ease(self.value.x(), other.value.x(), t),
                self._ease(self.value.y(), other.value.y(), t),
            )
        elif isinstance(self.value, (int, float)):
            return self._ease(self.value, other.value, t)

    def _ease(self, start, end, t):
        match self.easing:
            case EaseType.LINEAR:
                return start + (end - start) * t
            case EaseType.EASE_IN:
                return start + (end - start) * (t * t)
            case EaseType.EASE_OUT:
                return start + (end - start) * (1 - (1 - t) * (1 - t))


class KeyframeModel(BaseCollectionModel):
    def __init__(self):
        super().__init__(KeyframeData, "keyframes")
