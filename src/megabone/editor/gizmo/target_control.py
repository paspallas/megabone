from PyQt5.QtCore import Qt, QRectF
from PyQt5.QtGui import QColor, QBrush, QPen
from PyQt5.QtWidgets import QGraphicsItem


class TargetControl(QGraphicsItem):
    def __init__(self, handle, parent=None):
        super().__init__(parent)
        self.handle = handle
        self.setFlag(QGraphicsItem.ItemIsMovable)
        self.setFlag(QGraphicsItem.ItemIsSelectable)
        self.setAcceptHoverEvents(True)

        # Position at end effector
        self.updatePosition()

    def updatePosition(self):
        """Update position to match end effector"""
        self.setPos(self.handle.end_bone.end_point)

    def boundingRect(self):
        return QRectF(-10, -10, 20, 20)

    def paint(self, painter, option, widget):
        # Draw target control
        painter.setPen(QPen(Qt.red, 2))
        painter.setBrush(QBrush(QColor(255, 0, 0, 127)))
        painter.drawEllipse(self.boundingRect())

        # Draw cross in center
        painter.drawLine(-5, 0, 5, 0)
        painter.drawLine(0, -5, 0, 5)

    def mouseMoveEvent(self, event):
        super().mouseMoveEvent(event)
        # Solve IK for new target position
        self.handle.chain.solve(self.pos())
        # Update pole control position
        self.handle.pole.updatePosition()
