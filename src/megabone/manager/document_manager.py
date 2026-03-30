from pathlib import Path

from megabone.dialog import FileDialog
from megabone.model.document import Document
from megabone.qt import QMessageBox, QObject, QUndoGroup, Signal


class DocumentManager(QObject):
    """Manages a collection of documents and IO operations"""

    addedDocument = Signal(str)
    closedDocument = Signal(str)
    activeDocumentChanged = Signal(str)
    savedDocumentAs = Signal(str, str)

    openedDocument = Signal(str, Path)
    """An opened from file document was added to the collection"""

    createdDocument = Signal(str)
    """A newly created document was added to the collection"""

    def __init__(self):
        super().__init__()

        self._documents: dict[str, Document] = {}
        self._active_document_id: str | None = None
        self._unsaved_changes: set[str] = set()
        self._undo_group = QUndoGroup(self)

    @property
    def undo_group(self) -> QUndoGroup:
        return self._undo_group

    def connect_to_document(self, document: Document) -> None:
        document.documentModified.connect(
            lambda: self._on_document_changed(document.doc_id)
        )

    def disconnect_from_document(self, document: Document) -> None:
        document.documentModified.disconnect(self._on_document_changed)

    def track_changes(self, document: Document) -> None:
        self._unsaved_changes.add(document.doc_id)

    def get_document(self, doc_id: str) -> Document | None:
        return self._documents.get(doc_id)

    def add_document(self, document: Document) -> None:
        if document.doc_id not in self._documents:
            self._documents[document.doc_id] = document
            self._undo_group.addStack(document.undo_stack)

            self.track_changes(document)
            self.connect_to_document(document)

            self.addedDocument.emit(document.doc_id)
            self.createdDocument.emit(document.doc_id)

    def get_active_document(self) -> Document | None:
        assert self._active_document_id is not None
        return self._documents.get(self._active_document_id)

    def set_active_document(self, doc_id: str) -> None:
        if doc_id not in self._documents:
            return

        if self._active_document_id != doc_id:
            self._active_document_id = doc_id
            self._undo_group.setActiveStack(self._documents[doc_id].undo_stack)

            self.activeDocumentChanged.emit(doc_id)

    def create_document(self) -> None:
        self.add_document(Document())

    def open_document(self) -> None:
        path = FileDialog.open_file()
        if path:
            self.load_document(path)

    def load_document(self, path: Path):
        try:
            doc = Document.load(path)
            self.add_document(doc)
            self.openedDocument.emit(doc.doc_id, doc.path)
        except Exception:
            QMessageBox.critical(
                None,
                "Open File Error",
                f"Unable to open project file: '{path}'",
                QMessageBox.StandardButton.Ok,
            )

    def save_document(self, document: Document | None = None) -> None:
        doc = document or self.get_active_document()

        assert doc is not None

        if doc.path:
            try:
                doc.save()
            except Exception:
                self._save_error(doc)
        else:
            self.save_document_as(doc)

    def save_document_as(self, document: Document | None = None) -> None:
        doc = document or self.get_active_document()
        path = FileDialog.save_file()

        assert doc is not None

        if path:
            try:
                doc.save(path)
                self.savedDocumentAs.emit(doc.doc_id, path.stem)
            except Exception:
                self._save_error(doc)

    def close_document(self, doc_id: str | None) -> None:
        if not doc_id:
            doc_id = self._active_document_id

        if doc_id in self._unsaved_changes:
            doc = self.get_document(doc_id)

            assert doc is not None
            name = doc.path or "Untitled"

            response = QMessageBox.question(
                None,
                "Unsaved changes",
                f"Save changes to '{name}'?",
                QMessageBox.StandardButton.Save
                | QMessageBox.StandardButton.Discard
                | QMessageBox.StandardButton.Cancel,
            )

            if response == QMessageBox.StandardButton.Cancel:
                return
            elif response == QMessageBox.StandardButton.Save:
                self.save_document(doc)

        assert doc_id is not None
        self._documents.pop(doc_id)
        self._unsaved_changes.discard(doc_id)
        self.closedDocument.emit(doc_id)

    def on_autosave_failed(self, doc_id: str, error_message: str) -> None:
        doc = self.get_document(doc_id)
        if not doc:
            return

        QMessageBox.warning(
            None,
            "Autosave Failed",
            f"Failed to create backup for '{doc.path}':\n{error_message}\n\n"
            "Please save your work manually as soon as possible.",
        )

    def _on_document_changed(self, doc_id: str) -> None:
        self._unsaved_changes.add(doc_id)

    def _save_error(self, document: Document) -> None:
        QMessageBox.critical(
            None,
            "Save File Error",
            f"Unable to Save project file: '{document.path}'",
            QMessageBox.StandardButton.Ok,
        )
