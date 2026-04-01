from zlib import Z_NO_COMPRESSION

from megabone.command.sprite import CreateSpriteCommand
from megabone.editor.item import BoneItem, ItemFactory
from megabone.editor.item.model_item import ModelBoundItem
from megabone.editor.item.sprite import SpriteItem
from megabone.editor.layer import LayerManager
from megabone.manager.resource import ResourceManager
from megabone.model.bone import BoneData
from megabone.model.document import Document
from megabone.model.sprite import SpriteData
from megabone.qt import (
    QColor,
    QGraphicsItem,
    QGraphicsRectItem,
    QGraphicsScene,
    QRect,
    Signal,
)
from megabone.util.types import Point


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

        self.layer_manager = LayerManager(self)
        self.document = document
        self.document.documentModified.connect(self.rebuild)
        self.overlay = OverlayItem()

        # Add items from a document loaded from file
        ItemFactory.add_items_from_document(document, self)

    def setOverlaySize(self, rect: QRect) -> None:
        self.overlay.setRect(
            -rect.width() / 2, -rect.height() / 2, rect.width(), rect.height()
        )

    def add_item(self, item: QGraphicsItem) -> int:
        self.addItem(item)
        item.setSelected(False)

        return self.layer_manager.add_item(item)

    def remove_item(self, item: QGraphicsItem) -> None:
        self.layer_manager.remove_item(item)
        self.removeItem(item)

    def rebuild(self) -> None:
        """Recreate the scene with modelbounditems"""

        self.layer_manager.clear()
        self.clear()

        for model in self.document.get_all_collections():
            for data in model.get_items():
                item: ModelBoundItem | None = None

                if isinstance(data, BoneData):
                    item = BoneItem(document=self.document, id=data.id)
                elif isinstance(data, SpriteData):
                    item = SpriteItem(document=self.document, id=data.id)

                if item:
                    data.z_index = self.add_item(item)
                    item.apply_data_from_model(data)

        self.sceneRebuilt.emit()

    def on_sprite_drop(self, path: str, index: int, position: Point) -> None:
        """Add sprite to document from sprite palette"""

        sheet = ResourceManager.get_sheet(path)
        if not sheet:
            return

        data = SpriteData(
            name=self.document.sprites.next_name("Sprite"),
            path=path,
            frame_index=index,
            position=position,
            z_index=self.layer_manager.get_next_index(),
        )
        self.document.push(CreateSpriteCommand(self.document, data))
