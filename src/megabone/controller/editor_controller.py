from megabone.command.sprite import CreateSpriteCommand
from megabone.editor.item import ItemFactory
from megabone.editor.mode import AbstractEditorMode, EditorModeRegistry, SelectionMode
from megabone.manager.document import DocumentManager
from megabone.manager.resource import ResourceManager
from megabone.manager.tab import TabManager
from megabone.model.document import Document
from megabone.model.sprite import SpriteData
from megabone.qt import QGraphicsView, QObject, QPointF, Signal
from megabone.views.editor_scene import ModalEditorScene
from megabone.views.editor_view import MainEditorView


class EditorController(QObject):
    """Control and create editor views for documents"""

    activeViewChanged = Signal(MainEditorView)

    def __init__(self, documents: DocumentManager) -> None:
        super().__init__()
        self.document_collection = documents
        self.view_collection: dict[str, MainEditorView] = {}
        self.current_view: MainEditorView | None = None
        self.current_mode: AbstractEditorMode | None = None

        # Support mudltiple views in a tab interface
        self.editor_views = TabManager()

        self.editor_views.viewActivated.connect(self.set_active_view)
        self.editor_views.viewClosed.connect(self.on_close_view)
        self.document_collection.openedDocument.connect(
            lambda doc, path: self.editor_views.set_view_title(doc, path.stem)
        )
        self.document_collection.closedDocument.connect(self.editor_views.close_view)
        self.document_collection.savedDocumentAs.connect(
            self.editor_views.set_view_title
        )
        self.document_collection.createdDocument.connect(self.create_editor)

        # Register instances of editor tools
        EditorModeRegistry.init(self)

    def tab_views(self) -> TabManager:
        return self.editor_views

    def set_edit_mode(self, mode: type[AbstractEditorMode]):
        """Sets the edit tool"""

        mode_instance = EditorModeRegistry.get_mode(mode)

        if mode_instance != self.current_mode:
            if self.current_mode:
                self.current_mode.deactivate()

            self.current_mode = mode_instance
            self.current_mode.activate()

    def create_editor(self, document: Document, title: str = "Untitled*") -> None:
        """Create an editor view for the document"""

        view = MainEditorView(document=document)
        view.controller = self

        # Add editor view to collection
        self.view_collection[document.doc_id] = view

        self.editor_views.add_editor(view, title)
        self.set_edit_mode(SelectionMode)

        ItemFactory.add_items_from_document(document, view)

    def set_active_view(self, view: MainEditorView) -> None:
        self.current_view = view
        scene = view.scene()

        assert isinstance(scene, ModalEditorScene)
        self.document_collection.set_active_document(scene.document.doc_id)

        self.set_edit_mode(SelectionMode)

    def on_close_view(self, view: MainEditorView) -> None:
        scene = view.scene()

        assert isinstance(scene, ModalEditorScene)
        self.document_collection.close_document(scene.document.doc_id)

    def handle_mouse_press(self, view: QGraphicsView, event) -> None:
        assert isinstance(view, MainEditorView)
        if view != self.current_view:
            self.current_view = view

        if self.current_mode:
            self.current_mode.mousePressEvent(
                event, view.mapToScene(event.position().toPoint())
            )

    def handle_mouse_move(self, view: QGraphicsView, event) -> None:
        if self.current_mode:
            self.current_mode.mouseMoveEvent(
                event, view.mapToScene(event.position().toPoint())
            )

    def handle_mouse_release(self, view: QGraphicsView, event) -> None:
        if self.current_mode:
            self.current_mode.mouseReleaseEvent(
                event, view.mapToScene(event.position().toPoint())
            )

    def on_sprite_dropped(self, path: str, index: int, scene_pos: QPointF) -> None:
        """Add sprite to document from sprite palette"""

        sheet = ResourceManager.get_sheet(path)
        if not sheet:
            return

        document = self.document_collection.get_active_document()
        assert document is not None

        data = SpriteData(
            name=document.sprites.next_name("Sprite"),
            path=path,
            frame_index=index,
            x=scene_pos.x(),
            y=scene_pos.y(),
        )
        document.push(CreateSpriteCommand(document, data))
