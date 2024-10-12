from PyQt5.QtCore import QPointF
from PyQt5.QtWidgets import QGraphicsItem, QGraphicsPixmapItem


class AnimatedSpriteItem(QGraphicsPixmapItem):
    def __init__(self, pixmap, parent=None):
        super().__init__(pixmap, parent)
        self.setFlag(QGraphicsItem.ItemIsMovable)
        self.setFlag(QGraphicsItem.ItemIsSelectable)
        self.attached_bone = None

        # Store the initial offset from bone
        self.bone_offset = QPointF(0, 0)
        self.initial_rotation = 0
