from megabone.controller.editor_protocol import EditorControllerProtocol
from megabone.editor.grid import EditorGrid
from megabone.editor.layer import LayerManager
from megabone.event_filter import PanControl, ZoomControl
from megabone.model.document import Document
from megabone.qt import (
    QFrame,
    QGraphicsItem,
    QGraphicsView,
    QSizePolicy,
    Qt,
)

from .editor_scene import ModalEditorScene


class MainEditorView(QGraphicsView):
    _width = 512
    _height = 512

    def __init__(self, document: Document, parent=None, grid_size: int = 32):
        super().__init__(parent)
        self._configure_view()

        self.modal_scene = ModalEditorScene(self, document=document)
        self.modal_scene.dialogClose.connect(self.onModalDialogClose)
        self.modal_scene.setSceneRect(
            -self._width / 2, -self._height / 2, self._width, self._height
        )
        self.setScene(self.modal_scene)

        self.grid = EditorGrid(self, size=grid_size)
        self.layer_manager = LayerManager(self)
        self.controller: EditorControllerProtocol | None = None

    def _configure_view(self):
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
        self.setAcceptDrops(True)
        ZoomControl(self)
        PanControl(self)

    def showModalDialog(self):
        viewport = self.viewport()
        assert viewport is not None, "Editor view has no viewport"

        self.modal_scene.setOverlaySize(viewport.rect())
        self.modal_scene.overlay.show()

    def dragEnterEvent(self, event) -> None:
        if event.mimeData().hasFormat("application/x-megabone-sprite"):
            event.acceptProposedAction()
        else:
            event.ignore()

    def dragMoveEvent(self, event) -> None:
        if event.mimeData().hasFormat("application/x-megabone-sprite"):
            event.acceptProposedAction()

    def dropEvent(self, event) -> None:
        if not event.mimeData().hasFormat("application/x-megabone-sprite"):
            return

        raw = event.mimeData().data("application/x-megabone-sprite")
        path, index = raw.data().decode().split("|")
        index = int(index)

        scene_pos = self.mapToScene(event.position().toPoint())

        assert self.controller is not None
        self.controller.on_sprite_dropped(path, index, scene_pos)
        event.acceptProposedAction()

    def onModalDialogClose(self):
        self.modal_scene.overlay.hide()

    def mousePressEvent(self, event):
        assert self.controller is not None, "MainEditorView has no controller"

        self.controller.handle_mouse_press(self, event)
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        assert self.controller is not None, "MainEditorView has no controller"

        self.controller.handle_mouse_move(self, event)
        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        assert self.controller is not None, "MainEditorView has no controller"

        self.controller.handle_mouse_release(self, event)
        super().mouseReleaseEvent(event)

    def add_items(self, *items: QGraphicsItem):
        scene = self.scene()
        assert scene is not None, "MainEditorView has no scene set"

        for item in items:
            scene.addItem(item)
            self.layer_manager.add_item(item)

    def remove_item(self, item):
        scene = self.scene()
        assert scene is not None, "MainEditorView has no scene set"

        scene.removeItem(item)
        self.layer_manager.remove_item(item)

    # def selectBone(self, bone):
    #     self.selected_bone = bone

    # def selectSprite(self, sprite):
    #     if self.selected_sprite:
    #         self.selected_sprite.setSelected(False)
    #     self.selected_sprite = sprite
    #     sprite.setSelected(True)

    # def clearSelection(self):
    #     if self.selected_bone:
    #         self.selected_bone.setSelected(False)
    #         self.selected_bone = None
    #     if self.selected_sprite:
    #         self.selected_sprite.setSelected(False)
    #         self.selected_sprite = None

    # def attachSpriteToBone(self, sprite: SpriteItem, bone: BoneItem):
    #     if sprite.attached_bone:
    #         sprite.attached_bone.connected_sprites.remove(sprite)

    #     bone.connected_sprites.append(sprite)
    #     sprite.attached_bone = bone
    #     sprite.bone_offset = sprite.pos() - bone.end_point

    #     sprite.setTransformOriginPoint(sprite.mapFromItem(bone, bone.end_point))
    #     sprite.initial_rotation = sprite.rotation() - math.degrees(
    #         bone.calculate_angle()
    #     )
