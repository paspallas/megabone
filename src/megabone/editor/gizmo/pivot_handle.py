from PyQt5.QtCore import Qt, QPointF
from PyQt5.QtGui import QColor, QPen
from PyQt5.QtWidgets import QGraphicsItem, QGraphicsEllipseItem


class PivotHandle(QGraphicsEllipseItem):
    def __init__(self, parent, size: int = 8):
        super().__init__(parent)
        self.sprite_item = parent
        self.setParentItem(parent)
        self.setZValue(1000)
        self.setPen(QPen(Qt.white, 1))
        self.setBrush(QColor(255, 255, 255, 64))
        self.setFlag(QGraphicsItem.ItemIsMovable)
        self.setFlag(QGraphicsItem.ItemSendsGeometryChanges)
        self.setRect(-size / 2, -size / 2, size, size)

        self.position = QPointF(0, 0)

    def paint(self, painter, option, widget):
        super().paint(painter, option, widget)

        # Draw guide lines
        painter.setPen(QPen(Qt.white, 1, Qt.DashLine))
        rect = self.sprite_item.boundingRect()

        # Horizontal
        painter.drawLine(
            QPointF(-self.pos().x(), 0),
            QPointF(rect.width() - self.pos().x(), 0),
        )

        # Vertical
        painter.drawLine(
            QPointF(0, -self.pos().y()), QPointF(0, rect.height() - self.pos().y())
        )

    def itemChange(self, change, value):
        if change == QGraphicsItem.ItemPositionChange:
            # Constraint the pivot handle within the parent sprite
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
