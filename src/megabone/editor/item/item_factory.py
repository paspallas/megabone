from PyQt5.QtCore import QPointF
from PyQt5.QtWidgets import QGraphicsScene

from megabone.model.document import Document

from .bone import BoneItem
from .sprite import SpriteItem


class ItemFactory:
    @staticmethod
    def add_items_from_document(document: Document, scene: QGraphicsScene):
        for bone in document.bones.get_items():
            scene.addItem(
                BoneItem(
                    document.bones,
                    QPointF(bone.start_point[0], bone.start_point[1]),
                    QPointF(bone.end_point[0], bone.end_point[1]),
                    bone.id,
                )
            )
