from PyQt6.QtCore import QPointF, Qt
from PyQt6.QtGui import QColor, QPen
from PyQt6.QtWidgets import QGraphicsEllipseItem, QGraphicsItem


class PivotHandle(QGraphicsEllipseItem):
    def __init__(self, parent, size: int = 8):
        super().__init__(parent)
        self.sprite_item = parent
        self.setParentItem(parent)
        self.setZValue(1000)
        self.setPen(QPen(Qt.GlobalColor.white, 1))
        self.setBrush(QColor(255, 255, 255, 64))
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsMovable)
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemSendsGeometryChanges)
        self.setRect(-size / 2, -size / 2, size, size)

        self.position = QPointF(0, 0)

    def paint(self, painter, option, widget):
        super().paint(painter, option, widget)

        painter.setPen(QPen(Qt.GlobalColor.white, 1, Qt.PenStyle.DashLine))
        rect = self.sprite_item.boundingRect()

        painter.drawLine(
            QPointF(-self.pos().x(), 0),
            QPointF(rect.width() - self.pos().x(), 0),
        )

        painter.drawLine(
            QPointF(0, -self.pos().y()), QPointF(0, rect.height() - self.pos().y())
        )

    def itemChange(self, change, value):
        if change == QGraphicsItem.GraphicsItemChange.ItemPositionChange:
            parent = self.parentItem()
            if parent:
                return QPointF(
                    max(0, min(value.x(), self.sprite_item.boundingRect().width())),
                    max(0, min(value.y(), self.sprite_item.boundingRect().height())),
                )
        return super().itemChange(change, value)

    def mouseMoveEvent(self, event):
        super().mouseMoveEvent(event)
        self.update_sprite_anchor()

    def mouseReleaseEvent(self, event):
        super().mouseReleaseEvent(event)
        self.update_sprite_anchor()

    def update_sprite_anchor(self):
        self.position = self.pos()
        self.sprite_item.set_anchor_point(self.pos())
