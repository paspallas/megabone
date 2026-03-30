from dataclasses import dataclass, field

from megabone.qt import QPointF

from .collection import BaseCollectionModel
from .serializable import Serializable


@dataclass
class AttachmentData(Serializable):
    bone_id: str = ""
    sprite_id: str = ""
    offset: QPointF = field(default_factory=lambda: QPointF(0.0, 0.0))
    rotation_offset: float = 0.0


class AttachmentModel(BaseCollectionModel):
    def __init__(self):
        super().__init__(AttachmentData, "attachments")

    def get_items_for_bone(self, bone_id: str) -> list[Serializable]:
        pass
