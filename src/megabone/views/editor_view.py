import math

from PyQt6.QtCore import QPointF, Qt
from PyQt6.QtGui import QPixmap
from PyQt6.QtWidgets import QFrame, QGraphicsItem, QGraphicsView, QSizePolicy

from megabone.editor.grid import EditorGrid
from megabone.editor.item import BoneItem, SpriteItem
from megabone.editor.layer import LayerManager
from megabone.event_filter import PanControl, ZoomControl

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

        self.doc_id = doc_id

        self.centerOn(0, 0)
        self.setContentsMargins(0, 0, 0, 0)
        self.setMouseTracking(True)
        self.setResizeAnchor(QGraphicsView.ViewportAnchor.AnchorViewCenter)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.setTransformationAnchor(QGraphicsView.ViewportAnchor.NoAnchor)
        self.setViewportUpdateMode(QGraphicsView.ViewportUpdateMode.FullViewportUpdate)
        self.setCacheMode(QGraphicsView.CacheModeFlag.CacheBackground)
        self.setFrameStyle(QFrame.Shape.NoFrame)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setDragMode(QGraphicsView.DragMode.RubberBandDrag)
        ZoomControl(self)
        PanControl(self)

        self.selected_sprite = None
        self.selected_bone = None
        self.bones = []

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

    def attachSpriteToBone(self, sprite: SpriteItem, bone: BoneItem):
        if sprite.attached_bone:
            sprite.attached_bone.connected_sprites.remove(sprite)

        bone.connected_sprites.append(sprite)
        sprite.attached_bone = bone
        sprite.bone_offset = sprite.pos() - bone.end_point

        sprite.setTransformOriginPoint(sprite.mapFromItem(bone, bone.end_point))
        sprite.initial_rotation = sprite.rotation() - math.degrees(
            bone.calculate_angle()
        )

    def addSprite(self, pixmap: QPixmap, pos: QPointF = QPointF(0, 0)):
        sprite = SpriteItem(pixmap)
        sprite.setPos(pos)
        self.modal_scene.addItem(sprite)
        self.layer_manager.add_item(sprite)
        return sprite
