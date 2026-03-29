from typing import Optional

from megabone.editor.item import BoneItem
from megabone.model.document import Document
from megabone.qt import (
    QColor,
    QGraphicsItem,
    QGraphicsRectItem,
    QGraphicsScene,
    QRect,
    Signal,
)


class OverlayItem(QGraphicsRectItem):
    """Hide the scene on modal mode"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsSelectable, False)
        self.setBrush(QColor(10, 10, 10, 200))
        self.setZValue(1000_000_000)
        self.hide()


class ModalEditorScene(QGraphicsScene):
    dialogClose = Signal()
    sceneRebuilt = Signal()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self._document: Optional[Document] = None

        self.overlay = OverlayItem()
        self.addItem(self.overlay)

    def setOverlaySize(self, rect: QRect) -> None:
        self.overlay.setRect(
            -rect.width() / 2, -rect.height() / 2, rect.width(), rect.height()
        )

    def set_document(self, document: Document) -> None:
        self._document = document
        document.documentModified.connect(self.rebuild)
        self.rebuild()

    def rebuild(self) -> None:
        self.clear()
        self.addItem(self.overlay)

        if self._document:
            for bone_data in self._document.bones.get_items():
                item = BoneItem(model=self._document.bones)
                item.apply_data_from_model(bone_data)
                self.addItem(item)

        self.sceneRebuilt.emit()

    def itemAt(self, pos, deviceTransform):
        items = self.items(pos)

        # Check items shape
        for item in items:
            item_pos = item.mapFromScene(pos)
            if item.shape().contains(item_pos):
                return item

        return None
