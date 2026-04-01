from enum import Enum, auto

from megabone.manager.document import DocumentManager
from megabone.qt import QObject, Signal

from .editor import EditorController


class AppState(Enum):
    NO_DOCUMENT = auto()
    DOCUMENT_ACTIVE = auto()


class AppController(QObject):
    """Top-level application FSM"""

    requestFullScreen = Signal()
    requestZenMode = Signal()
    requestQuit = Signal()
    stateChanged = Signal(AppState)
    documentOpened = Signal()
    allDocumentsClosed = Signal()

    def __init__(
        self, document_manager: DocumentManager, editor_controller: EditorController
    ) -> None:
        super().__init__()
        self._documents = document_manager
        self._editor = editor_controller
        self._state = AppState.NO_DOCUMENT

        self._documents.createdDocument.connect(self._on_document_added)
        self._documents.openedDocument.connect(self._on_document_added)
        self._documents.closedDocument.connect(self._on_document_closed)

    @property
    def state(self) -> AppState:
        return self._state

    def _transition(self, new_state: AppState) -> None:
        if self._state == new_state:
            return
        self._state = new_state
        self.stateChanged.emit(new_state)

        if new_state == AppState.DOCUMENT_ACTIVE:
            self.documentOpened.emit()
        elif new_state == AppState.NO_DOCUMENT:
            self.allDocumentsClosed.emit()

    def _on_document_added(self, *args) -> None:
        self._transition(AppState.DOCUMENT_ACTIVE)

    def _on_document_closed(self, doc_id: str) -> None:
        if self._documents.count == 0:
            self._transition(AppState.NO_DOCUMENT)

    def on_new_document(self) -> None:
        self._documents.create_document()

    def on_open_document(self) -> None:
        from megabone.dialog import FileDialog

        path = FileDialog.open_file()
        if path:
            self._documents.open_document(path)

    def on_save_document(self) -> None:
        doc = self._documents.get_active_document()
        if not doc:
            return
        if doc.path:
            self._documents.save_document(doc.id)
        else:
            self.on_save_document_as()

    def on_save_document_as(self) -> None:
        from megabone.dialog import FileDialog

        doc = self._documents.get_active_document()
        if not doc:
            return

        path = FileDialog.save_file()
        if path:
            self._documents.save_document_as(doc.id, path)

    def on_close_document(self) -> None:
        doc = self._documents.get_active_document()
        if doc:
            self._documents.close_document(doc.id)

    def on_about(self) -> None:
        pass

    def on_quit(self) -> None:
        self.requestQuit.emit()

    def on_full_screen(self) -> None:
        self.requestFullScreen.emit()

    def on_zen_mode(self) -> None:
        self.requestZenMode.emit()
