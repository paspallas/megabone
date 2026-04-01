import math

from megabone.editor.layer import Layer, LayeredItemMixin
from megabone.model.attachment import AttachmentData
from megabone.model.bone import BoneData
from megabone.model.document import Document
from megabone.model.serializable import Serializable
from megabone.qt import (
    QBrush,
    QColor,
    QGraphicsItem,
    QLinearGradient,
    QPainterPath,
    QPen,
    QPointF,
    QRectF,
    Qt,
)
from megabone.util.types import Point

from .item_factory import ItemFactory
from .model_item import ModelBoundItem


@ItemFactory.register(BoneData)
class BoneItem(LayeredItemMixin, ModelBoundItem):
    _bone_width_start = 6
    _bone_width_end = 2
    _selected_color = QColor(230, 10, 230)
    _hover_color = QColor(200, 200, 255)
    _primary_color = QColor(100, 150, 255)
    _ghost_color = QColor(255, 0, 255)

    def __init__(
        self,
        document: Document,
        start_point: Point | None = None,
        end_point: Point | None = None,
        id: str = "",
        z_index: int = 0,
        is_ghost: bool = False,
    ):
        super().__init__(
            layer=Layer.BONE,
            z_index=z_index,
            id=id,
            model=document.bones,
            document=document,
        )
        self.start_point = start_point or Point(0, 0)
        self.end_point = end_point or Point(1, 1)

        self.is_hovered = False
        self.is_ghost = is_ghost

        # Bone hierarchy — runtime only, resolved from model parent_id on rebuild
        self.parent_bone: BoneItem | None = None
        self.child_bones: list[BoneItem] = []

        # Attachments — resolved from AttachmentModel on rebuild
        self._attachments: list[AttachmentData] = []

        self.setAcceptHoverEvents(True)
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsSelectable)

        if self.is_ghost:
            self.setOpacity(0.5)

    @classmethod
    def create_ghost(cls, document: Document, start: Point, end: Point) -> "BoneItem":
        return cls(
            document=document,
            start_point=start,
            end_point=end,
            id="__ghost__",
            is_ghost=True,
        )

    def calculate_length(self) -> float:
        return self.end_point.distance_to(self.start_point)

    def calculate_angle(self) -> float:
        new_point = self.end_point - self.start_point
        return math.atan2(new_point.y, new_point.y)

    def _safe_length(self) -> float:
        length = self.calculate_length()
        return length if length > 0 else 0.001

    def boundingRect(self) -> QRectF:
        return self.shape().boundingRect()

    def shape(self) -> QPainterPath:
        np = (self.end_point - self.start_point).normalized()
        nx, ny = -np.y, np.x

        hw_start = self._bone_width_start / 2
        hw_end = self._bone_width_end / 2

        start_left = QPointF(
            self.start_point.x + nx * hw_start, self.start_point.y + ny * hw_start
        )
        start_right = QPointF(
            self.start_point.x - nx * hw_start, self.start_point.y - ny * hw_start
        )
        end_left = QPointF(
            self.end_point.x + nx * hw_end, self.end_point.y + ny * hw_end
        )
        end_right = QPointF(
            self.end_point.x - nx * hw_end, self.end_point.y - ny * hw_end
        )

        path = QPainterPath()
        path.moveTo(start_left)
        path.lineTo(end_left)
        path.lineTo(end_right)
        path.lineTo(start_right)
        path.closeSubpath()
        return path

    def paint(self, painter, option, widget=None) -> None:
        if self.is_ghost:
            pen = QPen(self._ghost_color, 1, Qt.PenStyle.DashLine)
            painter.setPen(pen)
            painter.setBrush(Qt.BrushStyle.NoBrush)
            painter.drawPath(self.shape())
            return

        if self.isSelected():
            base_color = self._selected_color
        elif self.is_hovered:
            base_color = self._hover_color
        else:
            base_color = self._primary_color

        gradient = QLinearGradient(
            self.start_point.to_qpointf(), self.end_point.to_qpointf()
        )
        gradient.setColorAt(0, base_color.lighter(120))
        gradient.setColorAt(1, base_color.darker(120))

        painter.setPen(QPen(base_color.darker(150), 1))
        painter.setBrush(QBrush(gradient))
        painter.drawPath(self.shape())

        joint_radius = min(self._bone_width_start, self._bone_width_end) * 0.6
        painter.setBrush(QBrush(base_color.darker(120)))
        painter.drawEllipse(self.start_point.to_qpointf(), joint_radius, joint_radius)

    def hoverEnterEvent(self, event) -> None:
        self.is_hovered = True
        self.update()
        super().hoverEnterEvent(event)

    def hoverLeaveEvent(self, event) -> None:
        self.is_hovered = False
        self.update()
        super().hoverLeaveEvent(event)

    def mousePressEvent(self, event) -> None:
        if event.button() == Qt.MouseButton.LeftButton and not self.is_ghost:
            super().mousePressEvent(event)

    def set_parent_bone(self, parent: "BoneItem | None") -> None:
        # Detach from old parent
        if self.parent_bone and self in self.parent_bone.child_bones:
            self.parent_bone.child_bones.remove(self)

        self.parent_bone = parent

        if parent:
            parent.child_bones.append(self)
            self.start_point = parent.end_point
            self.update()

    def detach_from_parent(self) -> None:
        self.set_parent_bone(None)

    @property
    def parent_id(self) -> str:
        return self.parent_bone.id if self.parent_bone else ""

    def set_attachments(self, attachments: list[AttachmentData]) -> None:
        """Called by scene rebuild to wire up sprite attachments"""
        self._attachments = attachments

    def update_attached_sprites(self, sprite_items: dict) -> None:
        """
        Push bone transform to all attached sprites.
        sprite_items: dict[item_id → SpriteItem] from the scene.
        """
        for att in self._attachments:
            sprite = sprite_items.get(att.sprite_id)
            if sprite:
                sprite.apply_bone_transform(self, att)

    def update_children(self) -> None:
        """Propagate end point to all child start points recursively"""
        for child in self.child_bones:
            child.start_point = self.end_point
            child.update()
            child.update_children()

    def create_data_for_model(self) -> BoneData:
        return BoneData(
            id=self.id,
            start_point=self.start_point,
            end_point=self.end_point,
            z_index=self.z_index,
            parent_id=self.parent_id,
        )

    def apply_data_from_model(self, data: Serializable) -> None:
        assert isinstance(data, BoneData)

        self.start_point = data.start_point
        self.end_point = data.end_point
        self.z_index = data.z_index

        self.prepareGeometryChange()
        self.update()

    def request_delete(self) -> None:
        from megabone.command.bone import DeleteBoneCommand

        self._document.push(DeleteBoneCommand(self._document, self.id))
