from megabone.controller.editor_protocol import EditorControllerProtocol
from megabone.editor.grid import EditorGrid
from megabone.event_filter import PanControl, ZoomControl
from megabone.model.document import Document
from megabone.qt import (
    QFrame,
    QGraphicsView,
    QSizePolicy,
    Qt,
)
from megabone.util.types import Point

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
        position = self.mapToScene(event.position().toPoint())

        self.modal_scene.on_sprite_drop(path, index, Point.from_qpointf(position))
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
