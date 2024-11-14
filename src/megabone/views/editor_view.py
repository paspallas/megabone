import math

from PyQt5.QtCore import QPointF, Qt
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QFrame, QGraphicsItem, QGraphicsView, QSizePolicy

from megabone.editor.grid import EditorGrid
from megabone.editor.item import BoneItem, SpriteItem
from megabone.editor.layer import LayerManager
from megabone.event_filter import *

from .editor_scene import ModalEditorScene


class MainEditorView(QGraphicsView):
    _width = 512
    _height = 512

    def __init__(self, parent=None, doc_id: str = "", grid_size: int = 32):
        super().__init__(parent)
        self.modal_scene = ModalEditorScene(self)
        self.modal_scene.setSceneRect(
            -self._width / 2, -self._height / 2, self._width, self._height
        )
        self.setScene(self.modal_scene)

        self.grid = EditorGrid(self, size=grid_size)
        self.layer_manager = LayerManager(self)

        # Bound document id
        self.doc_id = doc_id

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
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setDragMode(QGraphicsView.RubberBandDrag)
        ZoomControl(self)
        PanControl(self)

        # Editor properties
        self.selected_sprite = None
        self.selected_bone = None
        self.bones = []

        # Connect signals
        self.modal_scene.dialogClose.connect(self.onModalDialogClose)

    def showModalDialog(self):
        self.modal_scene.setOverlaySize(self.viewport().rect())
        self.modal_scene.overlay.show()

    def onModalDialogClose(self):
        self.modal_scene.overlay.hide()

    def mousePressEvent(self, event):
        self.controller.handle_mouse_press(self, event)
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        self.controller.handle_mouse_move(self, event)
        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        self.controller.handle_mouse_release(self, event)
        super().mouseReleaseEvent(event)

    def add_items(self, *items: QGraphicsItem):
        for item in items:
            self.scene().addItem(item)
            self.layer_manager.add_item(item)

    def remove_item(self, item):
        self.scene().removeItem(item)
        self.layer_manager.remove_item(item)

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
            bone.calculate_angle()
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
