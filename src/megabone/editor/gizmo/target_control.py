from PyQt6.QtCore import QRectF, Qt
from PyQt6.QtGui import QBrush, QColor, QPen
from PyQt6.QtWidgets import QGraphicsItem


class TargetControl(QGraphicsItem):
    def __init__(self, handle, parent=None):
        super().__init__(parent)
        self.handle = handle
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsMovable)
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsSelectable)
        self.setAcceptHoverEvents(True)

        self.updatePosition()

    def updatePosition(self):
        """Update position to match end effector"""
        self.setPos(self.handle.end_bone.end_point)

    def boundingRect(self):
        return QRectF(-10, -10, 20, 20)

    def paint(self, painter, option, widget):
        painter.setPen(QPen(Qt.GlobalColor.red, 2))
        painter.setBrush(QBrush(QColor(255, 0, 0, 127)))
        painter.drawEllipse(self.boundingRect())

        painter.drawLine(-5, 0, 5, 0)
        painter.drawLine(0, -5, 0, 5)

    def mouseMoveEvent(self, event):
        super().mouseMoveEvent(event)
        self.handle.chain.solve(self.pos())
        self.handle.pole.updatePosition()
