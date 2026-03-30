from megabone.editor.gizmo import PivotHandle
from megabone.editor.layer import Layer, LayeredItemMixin
from megabone.model.attachment import AttachmentData
from megabone.model.collection import BaseCollectionModel
from megabone.model.serializable import Serializable
from megabone.model.sprite import SpriteData
from megabone.qt import QColor, QGraphicsItem, QGraphicsPixmapItem, QPixmap, QPointF, Qt

from .bone import BoneItem
from .item_factory import ItemFactory
from .model_item import ModelBoundItem


@ItemFactory.register(SpriteData)
class SpriteItem(ModelBoundItem, LayeredItemMixin, QGraphicsPixmapItem):
    def __init__(self, *args, item_id: str = "", model: BaseCollectionModel, **kwargs):
        super().__init__(
            *args, model=model, item_id=item_id, layer=Layer.SPRITE, **kwargs
        )
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsMovable)
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsSelectable)
        self._path = ""

        # Attached bone
        self.attached_bone = None
        self.bone_offset = QPointF(0, 0)
        self.initial_rotation = 0

        # # Anchor point
        # self.anchor_point = anchor_point
        # self.pivot_handle = PivotHandle(self)
        # self.pivot_handle.hide()
        # self.update_pivot_handle_pos()

    def update_pivot_handle_pos(self):
        pass
        # self.pivot_handle.setPos(self.anchor_point)

    def set_anchor_point(self, new_anchor: QPointF):
        self.anchor_point = new_anchor
        self.setTransformOriginPoint(new_anchor)
        self.update()
        self.update_bone_offset()

    def update_bone_offset(self):
        pass
        # TODO change the bone sprites list to acomodate the changes
        # if self.attached_bone:
        #     new_offset = self.pos() - self.attached_bone.start_point
        #     for i, (sprite, _) in enumerate(self.attached_bone.sprites):
        #         if sprite == self:
        #             self.attached_bone.sprites[i] = (sprite, new_offset)

    def itemChange(self, change, value):
        if change in (
            QGraphicsItem.GraphicsItemChange.ItemPositionHasChanged,
            QGraphicsItem.GraphicsItemChange.ItemRotationHasChanged,
            QGraphicsItem.GraphicsItemChange.ItemTransformHasChanged,
        ):
            self.update_model()
        return super().itemChange(change, value)

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.RightButton:
            self.toggle_pivot_handle()
        else:
            super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        # TODO remove Avoid manipulating the sprite when the pivot handle is active
        if not self.pivot_handle.isVisible():
            super().mouseMoveEvent(event)

    def toggle_pivot_handle(self):
        self.pivot_handle.setVisible(not self.pivot_handle.isVisible())
        self.update()

        if self.pivot_handle.isVisible():
            self.setSelected(False)

    def apply_data_from_model(self, data: Serializable) -> None:
        assert isinstance(data, SpriteData)

        if data.image_path != self._path:
            self._load_pixmap(data.image_path)
            self._path = data.image_path

        self.setVisible(data.visible)

    def _load_pixmap(self, path: str) -> None:
        # pixmap = ResourceManager.get_pixmap(path)
        # pixmap = QPixmap(path)

        # if pixmap.isNull():
        pixmap = self._placeholder_pixmap()

        # Center the origin on the pixmap
        self.setPixmap(pixmap)
        self.setOffset(-pixmap.width() / 2, -pixmap.height() / 2)

    def _placeholder_pixmap(self) -> QPixmap:
        """Shown when the image file is missing"""

        px = QPixmap(64, 64)
        px.fill(QColor(255, 0, 255, 128))

        return px

    def apply_bone_transform(self, bone: BoneItem, att: AttachmentData) -> None:
        """Called during live bone movement"""
        import math

        self._updating = True

        assert bone.end_point is not None
        self.setPos(bone.end_point + att.offset)
        self.setRotation(math.degrees(bone.calculate_angle()) + att.rotation_offset)
        self._updating = False
