from megabone.editor.item import BoneItem
from megabone.editor.item.sprite import SpriteItem
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


class ModalEditorScene(QGraphicsScene):
    dialogClose = Signal()
    sceneRebuilt = Signal()

    def __init__(self, *args, document: Document, **kwargs):
        super().__init__(*args, **kwargs)

        self.document = document
        self.document.documentModified.connect(self.rebuild)
        self.overlay = OverlayItem()

    def setOverlaySize(self, rect: QRect) -> None:
        self.overlay.setRect(
            -rect.width() / 2, -rect.height() / 2, rect.width(), rect.height()
        )

    def rebuild(self) -> None:
        self.clear()

        if self.document:
            #     for bone_data in self._document.bones.get_items():
            #         item = BoneItem(model=self._document.bones)
            #         item.apply_data_from_model(bone_data)
            #         self.addItem(item)

            for sprite_data in self.document.sprites.get_items():
                item = SpriteItem(
                    item_id=sprite_data.id,
                    document=self.document,
                )
                item.apply_data_from_model(sprite_data)
                self.addItem(item)

        self.sceneRebuilt.emit()
