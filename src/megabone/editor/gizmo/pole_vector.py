from PyQt5.QtCore import Qt, QPointF, QRectF
from PyQt5.QtGui import QBrush, QColor, QPen
from PyQt5.QtWidgets import QGraphicsItem


class PoleControl(QGraphicsItem):
    def __init__(self, handle, parent=None):
        super().__init__(parent)
        self.handle = handle
        self.setFlag(QGraphicsItem.ItemIsMovable)
        self.setFlag(QGraphicsItem.ItemIsSelectable)
        self.setAcceptHoverEvents(True)

        # Position at middle of chain
        self.updatePosition()

    def updatePosition(self):
        """Update position to default pole position"""
        if len(self.handle.chain.bones) < 2:
            return

        # Find middle bone
        middle_idx = len(self.handle.chain.bones) // 2
        middle_bone = self.handle.chain.bones[middle_idx]

        # Position perpendicular to bone
        bone_vector = QPointF(
            middle_bone.end_point.x() - middle_bone.start_point.x(),
            middle_bone.end_point.y() - middle_bone.start_point.y(),
        )
        # Rotate 90 degrees and normalize
        length = (bone_vector.x() ** 2 + bone_vector.y() ** 2) ** 0.5
        if length > 0:
            pole_vector = QPointF(
                -bone_vector.y() / length * 50,  # 50 units away from bone
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
        # Draw pole control
        painter.setPen(QPen(Qt.blue, 2))
        painter.setBrush(QBrush(QColor(0, 0, 255, 127)))
        painter.drawRect(self.boundingRect())

        # Draw line to chain
        if len(self.handle.chain.bones) >= 2:
            middle_idx = len(self.handle.chain.bones) // 2
            middle_bone = self.handle.chain.bones[middle_idx]
            middle_point = QPointF(
                (middle_bone.start_point.x() + middle_bone.end_point.x()) / 2,
                (middle_bone.start_point.y() + middle_bone.end_point.y()) / 2,
            )

            painter.setPen(QPen(Qt.blue, 1, Qt.DashLine))
            painter.drawLine(self.pos(), middle_point)

    def mouseMoveEvent(self, event):
        super().mouseMoveEvent(event)
        # Update IK solution with pole vector
        self.updateChainWithPoleVector()

    def updateChainWithPoleVector(self):
        """Apply pole vector influence to chain"""
        if len(self.handle.chain.bones) < 2:
            return

        # Calculate pole vector influence
        middle_idx = len(self.handle.chain.bones) // 2
        middle_bone = self.handle.chain.bones[middle_idx]

        # Get vector from middle bone to pole
        pole_vector = QPointF(
            self.pos().x() - middle_bone.start_point.x(),
            self.pos().y() - middle_bone.start_point.y(),
        )

        # Update IK solution considering pole vector
        # This is a simplified version - you might want more sophisticated pole vector handling
        self.handle.chain.solve(self.handle.target.pos(), pole_vector)
