from megabone.command.sprite import MoveSpriteCommand
from megabone.editor.layer import Layer, LayeredItemMixin
from megabone.manager.resource import ResourceManager
from megabone.model.document import Document
from megabone.model.serializable import Serializable
from megabone.model.sprite import SpriteData
from megabone.qt import QColor, QGraphicsItem, QPixmap, QRectF, Qt

from .item_factory import ItemFactory
from .model_item import ModelBoundItem


@ItemFactory.register(SpriteData)
class SpriteItem(LayeredItemMixin, ModelBoundItem):
    def __init__(self, document: Document, item_id: str = ""):
        super().__init__(
            layer=Layer.SPRITE,
            z_index=0,
            item_id=item_id,
            model=document.sprites,
            document=document,
        )
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsMovable)
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsSelectable)

        self._path = ""
        self._pixmap: QPixmap = self._placeholder_pixmap()

    def boundingRect(self) -> QRectF:
        w = self._pixmap.width()
        h = self._pixmap.height()
        return QRectF(-w / 2, -h / 2, w, h)

    def paint(self, painter, option, widget=None) -> None:
        painter.drawPixmap(
            int(-self._pixmap.width() / 2),
            int(-self._pixmap.height() / 2),
            self._pixmap,
        )
        # Selection indicator
        if self.isSelected():
            painter.setPen(Qt.GlobalColor.white)
            painter.drawRect(self.boundingRect())

    def mouseReleaseEvent(self, event) -> None:
        super().mouseReleaseEvent(event)

        old_data = self.current_data()

        assert isinstance(old_data, SpriteData)
        # snapshot the values before any mutation
        old_pos = (old_data.x, old_data.y)

        new_data = self.create_data_for_model()
        new_pos = (new_data.x, new_data.y)

        if old_pos != new_pos:
            self.push_command(
                MoveSpriteCommand(
                    self._document,
                    self.item_id,
                    old_pos,
                    new_pos,
                )
            )

    def apply_data_from_model(self, data: Serializable) -> None:
        assert isinstance(data, SpriteData)

        if data.path != self._path:
            self._load_pixmap(data.path, data.frame_index)
            self._path = data.path

        self.setPos(data.x, data.y)
        self.setRotation(data.rotation)
        self.setVisible(data.visible)
        self.prepareGeometryChange()

    def create_data_for_model(self) -> SpriteData:
        from copy import copy

        data = copy(self.current_data())

        assert isinstance(data, SpriteData)
        data.x = self.pos().x()
        data.y = self.pos().y()
        data.rotation = self.rotation()
        return data

    def set_pixmap(self, pixmap: QPixmap) -> None:
        self.prepareGeometryChange()
        self._pixmap = pixmap
        self.update()

    def _load_pixmap(self, path: str, frame_index: int) -> None:
        if not path:
            self._pixmap = self._placeholder_pixmap()
            return

        pixmap = ResourceManager.get_frame(path, frame_index)
        # Removing the spritesheet from the palette deletes frame data from the resource cache

        if pixmap is None:
            self._pixmap = self._placeholder_pixmap()
        else:
            self._pixmap = pixmap if not pixmap.isNull() else self._placeholder_pixmap()

        self.prepareGeometryChange()
        self.update()

    @staticmethod
    def _placeholder_pixmap() -> QPixmap:
        px = QPixmap(32, 32)
        px.fill(QColor(255, 0, 255, 128))

        return px

    # def apply_bone_transform(self, bone: BoneItem, att: AttachmentData) -> None:
    #     """Called during live bone movement"""
    #     import math

    #     self._updating = True

    #     assert bone.end_point is not None
    #     self.setPos(bone.end_point + att.offset)
    #     self.setRotation(math.degrees(bone.calculate_angle()) + att.rotation_offset)
    #     self._updating = False
