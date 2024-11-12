from typing import Dict, Optional

from PyQt5.QtCore import QObject, pyqtSignal

from megabone.editor.mode import *
from megabone.manager import DocumentManager, TabManager
from megabone.views import MainEditorView


class EditorController(QObject):
    """Manages all edit operations on the active document."""

    activeViewChanged = pyqtSignal(MainEditorView)

    def __init__(self, documents: DocumentManager) -> None:
        super().__init__()
        self.documents = documents
        self.views: Dict[int, MainEditorView] = {}
        self.current_view: Optional[MainEditorView] = None
        self.current_mode: Optional[AbstractEditorMode] = None

        self.tab_widget = TabManager()

        # Connect signals
        self.tab_widget.viewActivated.connect(self.set_active_view)
        self.tab_widget.viewClosed.connect(self.on_close_view)
        self.documents.savedDocumentAs.connect(self.set_view_title)
        self.documents.openedDocument.connect(self.set_view_title)
        self.documents.createdDocument.connect(self.create_editor)

        # Register and init all edit modes
        EditorModeRegistry.init(self)

    def views_container(self) -> TabManager:
        return self.tab_widget

    def set_edit_mode(self, mode: EditorModeRegistry.Mode):
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

        self.tab_widget.add_editor(view, title)

        # New views start in the selection mode
        self.set_edit_mode(EditorModeRegistry.Mode.SELECTION_MODE)

    def set_active_view(self, view: MainEditorView) -> None:
        self.current_view = view
        self.documents.set_active_document(view.doc_id)

        # On view change reset to the default edit mode
        self.set_edit_mode(EditorModeRegistry.Mode.SELECTION_MODE)

    def set_view_title(self, doc_id: str, title: str) -> None:
        for i in range(self.tab_widget.count()):
            container = self.tab_widget.widget(i)
            view = container.findChild(MainEditorView)
            if view.doc_id == doc_id:
                self.tab_widget.set_title(i, title)
                return

    def on_close_view(self, index: int, view: MainEditorView) -> None:
        if self.documents.close_document(view.doc_id):
            self.tab_widget.removeTab(index)

    def handle_mouse_press(self, view: MainEditorView, event) -> None:
        if view != self.current_view:
            self.current_view = view
        if self.current_mode:
            self.current_mode.mousePressEvent(event, view.mapToScene(event.pos()))

    def handle_mouse_move(self, view: MainEditorView, event) -> None:
        if self.current_mode:
            self.current_mode.mouseMoveEvent(event, view.mapToScene(event.pos()))

    def handle_mouse_release(self, view: MainEditorView, event) -> None:
        if self.current_mode:
            self.current_mode.mouseReleaseEvent(event, view.mapToScene(event.pos()))
