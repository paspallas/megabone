from PyQt6.QtCore import QPointF, QRectF, Qt
from PyQt6.QtGui import QBrush, QColor, QPen
from PyQt6.QtWidgets import QGraphicsItem


class PoleControl(QGraphicsItem):
    def __init__(self, handle, parent=None):
        super().__init__(parent)
        self.handle = handle
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsMovable)
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsSelectable)
        self.setAcceptHoverEvents(True)

        self.updatePosition()

    def updatePosition(self):
        """Update position to default pole position"""
        if len(self.handle.chain.bones) < 2:
            return

        middle_idx = len(self.handle.chain.bones) // 2
        middle_bone = self.handle.chain.bones[middle_idx]

        bone_vector = QPointF(
            middle_bone.end_point.x() - middle_bone.start_point.x(),
            middle_bone.end_point.y() - middle_bone.start_point.y(),
        )
        length = (bone_vector.x() ** 2 + bone_vector.y() ** 2) ** 0.5
        if length > 0:
            pole_vector = QPointF(
                -bone_vector.y() / length * 50,
                bone_vector.x() / length * 50,
            )
            middle_point = QPointF(
                (middle_bone.start_point.x() + middle_bone.end_point.x()) / 2,
                (middle_bone.start_point.y() + middle_bone.end_point.y()) / 2,
            )
            self.setPos(middle_point + pole_vector)

    def boundingRect(self):
        return QRectF(-5, -5, 10, 10)

    def paint(self, painter, option, widget):
        painter.setPen(QPen(Qt.GlobalColor.blue, 2))
        painter.setBrush(QBrush(QColor(0, 0, 255, 127)))
        painter.drawRect(self.boundingRect())

        if len(self.handle.chain.bones) >= 2:
            middle_idx = len(self.handle.chain.bones) // 2
            middle_bone = self.handle.chain.bones[middle_idx]
            middle_point = QPointF(
                (middle_bone.start_point.x() + middle_bone.end_point.x()) / 2,
                (middle_bone.start_point.y() + middle_bone.end_point.y()) / 2,
            )

            painter.setPen(QPen(Qt.GlobalColor.blue, 1, Qt.PenStyle.DashLine))
            painter.drawLine(self.pos(), middle_point)

    def mouseMoveEvent(self, event):
        super().mouseMoveEvent(event)
        self.updateChainWithPoleVector()

    def updateChainWithPoleVector(self):
        """Apply pole vector influence to chain"""
        if len(self.handle.chain.bones) < 2:
            return

        middle_idx = len(self.handle.chain.bones) // 2
        middle_bone = self.handle.chain.bones[middle_idx]

        pole_vector = QPointF(
            self.pos().x() - middle_bone.start_point.x(),
            self.pos().y() - middle_bone.start_point.y(),
        )

        self.handle.chain.solve(self.handle.target.pos(), pole_vector)
