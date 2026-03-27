from PyQt6.QtCore import QRect, pyqtSignal
from PyQt6.QtGui import QColor
from PyQt6.QtWidgets import QGraphicsItem, QGraphicsRectItem, QGraphicsScene


class OverlayItem(QGraphicsRectItem):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsSelectable, False)
        self.setBrush(QColor(10, 10, 10, 200))
        self.setZValue(1000_000_000)
        self.hide()


class ModalEditorScene(QGraphicsScene):
    dialogClose = pyqtSignal()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Create an overlay item for hiding the scene
        self.overlay = OverlayItem()
        self.addItem(self.overlay)

    def setOverlaySize(self, rect: QRect) -> None:
        self.overlay.setRect(
            -rect.width() / 2, -rect.height() / 2, rect.width(), rect.height()
        )

    def itemAt(self, pos, deviceTransform):
        items = self.items(pos)

        # Check items shape
        for item in items:
            item_pos = item.mapFromScene(pos)
            if item.shape().contains(item_pos):
                return item

        return None
