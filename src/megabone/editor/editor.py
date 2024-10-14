import math

from PyQt5.QtCore import Qt, QPointF, QRectF, QLineF
from PyQt5.QtGui import QPixmap, QColor, QPen, QPainter, QBrush
from PyQt5.QtWidgets import QGraphicsScene, QGraphicsView, QSizePolicy, QFrame

from megabone.viewUtils import PanControl, ZoomControl
from .item import AnimatedSpriteItem, BoneGraphicsItem
from .status import StatusMessage
from .mode import *

__backGridColor__ = QColor("#080808")
__foreGridColor__ = QColor(210, 210, 210, 200)
__darkColor__ = QColor("#404040")
__lightColor__ = QColor("#666666")


class SkeletonEditorScene(QGraphicsScene):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def itemAt(self, position: QPointF, transform):
        items = self.items(position)

        # Check items shape
        for item in items:
            item_pos = item.mapFromScene(position)
            if item.shape().contains(item_pos):
                return item

        return None


class SkeletonEditor(QGraphicsView):
    # Default size corresponds with the Megadrive sprite plane
    _width = 512
    _height = 512

    def __init__(self, parent=None, grid_size: int = 32):
        super().__init__(parent)
        self.scene = SkeletonEditorScene(self)
        self.scene.setSceneRect(
            -self._width / 2, -self._height / 2, self._width, self._height
        )
        self.setScene(self.scene)

        # Configure grid size
        self.grid_size = grid_size

        # Configure the view
        self.centerOn(0, 0)
        self.setContentsMargins(0, 0, 0, 0)
        self.setMouseTracking(True)
        self.setResizeAnchor(QGraphicsView.AnchorViewCenter)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.setTransformationAnchor(QGraphicsView.NoAnchor)
        self.setViewportUpdateMode(QGraphicsView.FullViewportUpdate)
        self.setOptimizationFlag(QGraphicsView.DontAdjustForAntialiasing)
        self.setCacheMode(QGraphicsView.CacheBackground)
        self.setFrameStyle(QFrame.NoFrame)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        self.setDragMode(QGraphicsView.RubberBandDrag)
        ZoomControl(self)
        PanControl(self)

        # Init the editing modes from the registry
        self.current_edit_mode = None
        EditorModeRegistry.init(self)

        # Set default mode
        self.setEditMode(EditorModeRegistry.Mode.SELECTION_MODE)

        # Editor properties
        self.selected_sprite = None
        self.selected_bone = None
        self.bones = []

    def setEditMode(self, mode: "EditorModeRegistry.Mode"):
        new_mode = EditorModeRegistry.get_mode(mode)

        if new_mode != self.current_edit_mode:
            if self.current_edit_mode:
                self.current_edit_mode.deactivate()
            self.current_edit_mode = new_mode
            self.current_edit_mode.activate()

    def mousePressEvent(self, event):
        scene_pos = self.mapToScene(event.pos())
        self.current_edit_mode.mousePressEvent(event, scene_pos)
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        scene_pos = self.mapToScene(event.pos())
        self.current_edit_mode.mouseMoveEvent(event, scene_pos)
        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        scene_pos = self.mapToScene(event.pos())
        self.current_edit_mode.mouseReleaseEvent(event, scene_pos)
        super().mouseReleaseEvent(event)

    def drawBackground(self, painter: QPainter, rect: QRectF) -> None:
        painter.setPen(QPen(Qt.NoPen))

        left = int(rect.left() - rect.left() % self.grid_size)
        top = int(rect.top() - rect.top() % self.grid_size)

        for y in range(top, int(rect.bottom()), self.grid_size):
            for x in range(left, int(rect.right()), self.grid_size):
                is_dark = (x / self.grid_size + y / self.grid_size) % 2

                color = __darkColor__ if is_dark else __lightColor__
                painter.fillRect(
                    QRectF(x, y, self.grid_size, self.grid_size), QBrush(color)
                )

        l = rect.left()
        r = rect.right()
        t = rect.top()
        b = rect.bottom()

        # center visual indicator
        lines = [QLineF(l, 0, r, 0), QLineF(0, t, 0, b)]

        pen = QPen(__backGridColor__, 0, Qt.SolidLine)
        pen.setCosmetic(True)
        painter.setPen(pen)
        painter.drawLines(*lines)
        pen.setColor(__foreGridColor__)
        painter.setPen(pen)
        painter.drawRect(QRectF(-160, -112, 320, 224))

    def drawForeground(self, painter: QPainter, rect) -> None:
        start = 6
        end = 2
        lines = [
            QLineF(-start, 0, -end, 0),
            QLineF(0, -start, 0, -end),
            QLineF(end, 0, start, 0),
            QLineF(0, start, 0, end),
        ]

        painter.setRenderHint(QPainter.Antialiasing)
        pen = QPen(__foreGridColor__, 2, Qt.SolidLine)
        pen.setCosmetic(True)
        painter.setPen(pen)
        painter.drawLines(*lines)
        painter.drawEllipse(QPointF(0, 0), 1, 1)

    def showStatusMessage(self, message: str):
        StatusMessage(message, self)

    def selectBone(self, bone):
        self.selected_bone = bone

    def selectSprite(self, sprite):
        if self.selected_sprite:
            self.selected_sprite.setSelected(False)
        self.selected_sprite = sprite
        sprite.setSelected(True)

    def clearSelection(self):
        if self.selected_bone:
            self.selected_bone.setSelected(False)
            self.selected_bone = None
        if self.selected_sprite:
            self.selected_sprite.setSelected(False)
            self.selected_sprite = None

    def attachSpriteToBone(self, sprite: AnimatedSpriteItem, bone: BoneGraphicsItem):
        if sprite.attached_bone:
            sprite.attached_bone.connected_sprites.remove(sprite)

        # Add relationship between bone and sprite
        bone.connected_sprites.append(sprite)
        sprite.attached_bone = bone
        sprite.bone_offset = sprite.pos() - bone.end_point
        sprite.initial_rotation = sprite.rotation() - math.degrees(
            bone.calculateAngle()
        )

    def addSprite(self, pixmap: QPixmap, pos: QPointF):
        sprite = AnimatedSpriteItem(pixmap)
        sprite.setPos(pos)
        self.scene.addItem(sprite)
        return sprite

    def selectSprite(self, sprite):
        if self.selected_sprite:
            self.selected_sprite.setSelected(False)
        self.selected_sprite = sprite
        sprite.setSelected(True)
