from PyQt6.QtCore import QObject, pyqtSignal

from megabone.editor.item import ItemFactory
from megabone.editor.mode import AbstractEditorMode, EditorModeRegistry, SelectionMode
from megabone.manager import DocumentManager, TabManager
from megabone.views import MainEditorView


class EditorController(QObject):
    """Manages all edit operations on the active document."""

    activeViewChanged = pyqtSignal(MainEditorView)

    def __init__(self, documents: DocumentManager) -> None:
        super().__init__()
        self.documents = documents
        self.views: dict[int, MainEditorView] = {}
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

        EditorModeRegistry.init(self)

    def views_container(self) -> TabManager:
        return self.editor_views

    def set_edit_mode(self, mode: type[AbstractEditorMode]):
        new_mode = EditorModeRegistry.get_mode(mode)

        if new_mode != self.current_mode:
            if self.current_mode:
                self.current_mode.deactivate()
            self.current_mode = new_mode
            self.current_mode.activate()

    def create_editor(self, doc_id: str, title: str = "Untitled*") -> None:
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

    def handle_mouse_press(self, view: MainEditorView, event) -> None:
        if view != self.current_view:
            self.current_view = view
        if self.current_mode:
            self.current_mode.mousePressEvent(
                event, view.mapToScene(event.position().toPoint())
            )

    def handle_mouse_move(self, view: MainEditorView, event) -> None:
        if self.current_mode:
            self.current_mode.mouseMoveEvent(
                event, view.mapToScene(event.position().toPoint())
            )

    def handle_mouse_release(self, view: MainEditorView, event) -> None:
        if self.current_mode:
            self.current_mode.mouseReleaseEvent(
                event, view.mapToScene(event.position().toPoint())
            )
