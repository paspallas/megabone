from megabone.editor.item import ItemFactory
from megabone.editor.mode import AbstractEditorMode, EditorModeRegistry, SelectionMode
from megabone.manager import DocumentManager, TabManager
from megabone.qt import QGraphicsView, QObject, Signal
from megabone.views.editor_view import MainEditorView


class EditorController(QObject):
    """This controller acts as a hub for all documents and editors, routing user
    interaction from edit tools to the active document
    """

    activeViewChanged = Signal(MainEditorView)

    def __init__(self, documents: DocumentManager) -> None:
        super().__init__()
        self.documents = documents
        self.views: dict[str, MainEditorView] = {}
        self.current_view: MainEditorView | None = None
        self.current_mode: AbstractEditorMode | None = None

        self.editor_views = TabManager()

        self.editor_views.viewActivated.connect(self.set_active_view)
        self.editor_views.viewClosed.connect(self.on_close_view)
        self.documents.openedDocument.connect(
            lambda doc, path: self.editor_views.set_view_title(doc, path.stem)
        )
        self.documents.closedDocument.connect(self.editor_views.close_view)
        self.documents.savedDocumentAs.connect(self.editor_views.set_view_title)
        self.documents.createdDocument.connect(self.create_editor)

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

    def create_editor(self, doc_id: str, title: str = "Untitled*") -> None:
        """Create an editor view for the selected document"""

        view = MainEditorView(doc_id=doc_id)
        view.controller = self

        self.views[doc_id] = view

        self.editor_views.add_editor(view, title)
        self.set_edit_mode(SelectionMode)

        document = self.documents.get_document(doc_id)
        assert document is not None, "Failed to get document"
        ItemFactory.add_items_from_document(document, view)

    def set_active_view(self, view: MainEditorView) -> None:
        self.current_view = view
        self.documents.set_active_document(view.doc_id)

        self.set_edit_mode(SelectionMode)

    def on_close_view(self, view: MainEditorView) -> None:
        self.documents.close_document(view.doc_id)

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
