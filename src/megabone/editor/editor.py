import math

from PyQt5.QtCore import QEvent, QObject, QPointF, QRect, Qt, pyqtSignal
from PyQt5.QtGui import QColor, QPixmap
from PyQt5.QtWidgets import (
    QFrame,
    QGraphicsItem,
    QGraphicsRectItem,
    QGraphicsScene,
    QGraphicsView,
    QSizePolicy,
)

from megabone.dialog.modal import DialogType, ModalDialogFactory
from megabone.viewUtils import *

from .grid import EditorGrid
from .item import BoneItem, SpriteItem
from .layer import LayerManager
from .mode import *
from .status import StatusMessage


class OverlayItem(QGraphicsRectItem):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.setFlag(QGraphicsItem.ItemIsSelectable, False)
        self.setBrush(QColor(10, 10, 10, 200))
        self.setZValue(10_000_000)
        self.hide()


class ModalEditorScene(QGraphicsScene):
    dialogClose = pyqtSignal()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.modal_active = False

        # Create an overlay item for hiding the scene
        self.overlay = OverlayItem()
        self.addItem(self.overlay)

    def setOverlaySize(self, rect: QRect) -> None:
        self.overlay.setRect(
            -rect.width() / 2, -rect.height() / 2, rect.width(), rect.height()
        )

    def itemAt(self, position: QPointF, transform):
        items = self.items(position)

        # Check items shape
        for item in items:
            item_pos = item.mapFromScene(position)
            if item.shape().contains(item_pos):
                return item

        return None


class SkeletonEditor(QGraphicsView):
    _width = 512
    _height = 512

    def __init__(self, parent=None, grid_size: int = 32):
        super().__init__(parent)
        self.modal_scene = ModalEditorScene(self)
        self.modal_scene.setSceneRect(
            -self._width / 2, -self._height / 2, self._width, self._height
        )
        self.setScene(self.modal_scene)

        self.grid = EditorGrid(self, size=grid_size)
        self.layer_manager = LayerManager(self)

        # Configure the view
        self.centerOn(0, 0)
        self.setContentsMargins(0, 0, 0, 0)
        self.setMouseTracking(True)
        self.setResizeAnchor(QGraphicsView.AnchorViewCenter)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.setTransformationAnchor(QGraphicsView.NoAnchor)
        self.setViewportUpdateMode(QGraphicsView.FullViewportUpdate)
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

        # Connect signals
        self.modal_scene.dialogClose.connect(self.onModalDialogClose)

    def setEditMode(self, mode: "EditorModeRegistry.Mode"):
        new_mode = EditorModeRegistry.get_mode(mode)

        if new_mode != self.current_edit_mode:
            if self.current_edit_mode:
                self.current_edit_mode.deactivate()
            self.current_edit_mode = new_mode
            self.current_edit_mode.activate()

    def showModalDialog(self):
        self.modal_scene.setOverlaySize(self.viewport().rect())
        self.modal_scene.overlay.show()

        # Create the dialog
        self.dialog = ModalDialogFactory.create_dialog(
            DialogType.NAME_INPUT, self, prompt="New Bone Name:"
        )
        self.dialog.show()
        self.dialog.finished.connect(self.modal_scene.dialogClose.emit)

    def onModalDialogClose(self):
        self.modal_scene.overlay.hide()

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

    # TODO move all operations to a controller class

    def attachSpriteToBone(self, sprite: SpriteItem, bone: BoneItem):
        if sprite.attached_bone:
            sprite.attached_bone.connected_sprites.remove(sprite)

        # Add relationship between bone and sprite
        bone.connected_sprites.append(sprite)
        sprite.attached_bone = bone
        sprite.bone_offset = sprite.pos() - bone.end_point

        # Set default anchor point of the sprite to the end_point of the bone
        sprite.setTransformOriginPoint(sprite.mapFromItem(bone, bone.end_point))
        sprite.initial_rotation = sprite.rotation() - math.degrees(
            bone.calculateAngle()
        )

    def addSprite(self, pixmap: QPixmap, pos: QPointF = QPointF(0, 0)):
        # pixmap.setMask(pixmap.createMaskFromColor(Qt.magenta))
        sprite = SpriteItem(pixmap)
        sprite.setPos(pos)
        self.modal_scene.addItem(sprite)
        self.layer_manager.add_item(sprite)
        return sprite

    def selectSprite(self, sprite):
        if self.selected_sprite:
            self.selected_sprite.setSelected(False)
        self.selected_sprite = sprite
        sprite.setSelected(True)
