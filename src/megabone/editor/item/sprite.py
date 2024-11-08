from PyQt5.QtCore import Qt, QPointF, QRectF
from PyQt5.QtWidgets import QGraphicsItem
from PyQt5.QtGui import QPixmap, QPainter

from megabone.editor.layer import LayeredItemMixin, Layer
from megabone.editor.gizmo import PivotHandle


class SpriteItem(LayeredItemMixin, QGraphicsItem):
    def __init__(self, pixmap: QPixmap, anchor_point=QPointF(0, 0), parent=None):
        super().__init__(parent=parent, layer=Layer.SPRITE)
        self.setFlag(QGraphicsItem.ItemIsMovable)
        self.setFlag(QGraphicsItem.ItemIsSelectable)
        self.pixmap = pixmap

        # Attached bone
        self.attached_bone = None
        self.bone_offset = QPointF(0, 0)
        self.initial_rotation = 0

        # Anchor point
        self.anchor_point = anchor_point
        self.pivot_handle = PivotHandle(self)
        self.pivot_handle.hide()
        self.update_pivot_handle_pos()

    def boundingRect(self) -> QRectF:
        return QRectF(self.pixmap.rect())

    def paint(self, painter: QPainter, option, widget):
        painter.drawPixmap(0, 0, self.pixmap)

    def update_pivot_handle_pos(self):
        self.pivot_handle.setPos(self.anchor_point)

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
        if change == QGraphicsItem.ItemPositionChange and self.scene():
            self.update_bone_offset()
        return super().itemChange(change, value)

    def mousePressEvent(self, event):
        if event.button() == Qt.RightButton:
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
