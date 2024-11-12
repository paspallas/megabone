from typing import Dict, Optional, Set

from PyQt5.QtCore import QObject, pyqtSignal
from PyQt5.QtWidgets import QMessageBox

from megabone.dialog import FileDialog
from megabone.model.document import Document


class DocumentManager(QObject):
    """Manages a collection of documents and IO operations"""

    documentAdded = pyqtSignal(str)  # doc_id
    documentRemoved = pyqtSignal(str)  # doc_id
    activeDocumentChanged = pyqtSignal(str)  # doc_id
    savedDocumentAs = pyqtSignal(str, str)  # doc_id, path_stem
    openedDocument = pyqtSignal(str, str)  # doc_id, path_stem
    createdDocument = pyqtSignal(str)  # doc_id

    def __init__(self):
        super().__init__()

        self._documents: Dict[str, Document] = {}
        self._active_document_id: Optional[str] = None
        self._unsaved_changes: Set[str] = set()

    def connect_to_document(self, document: Document) -> None:
        document.documentChanged.connect(lambda: self._on_document_changed(document.id))

    def disconnect_from_document(self, document: Document) -> None:
        pass

    def track_changes(self, document: Document) -> None:
        self._unsaved_changes.add(document.id)

    def get_document(self, doc_id: str) -> Optional[Document]:
        return self._documents.get(doc_id, None)

    def add_document(self, document: Document) -> None:
        self._documents[document.id] = document
        self.track_changes(document)
        self.connect_to_document(document)
        self.documentAdded.emit(document.id)

    def get_active_document(self) -> Optional[Document]:
        return self._documents.get(self._active_document_id, None)

    def set_active_document(self, doc_id: str) -> None:
        if doc_id not in self._documents:
            return

        if self._active_document_id != doc_id:
            self._active_document_id = doc_id
            self.activeDocumentChanged.emit(doc_id)

    def create_document(self) -> None:
        doc = Document()
        self.add_document(doc)
        self.createdDocument.emit(doc.id)

    def open_document(self) -> None:
        path = FileDialog.open_file()
        if path:
            try:
                doc = Document.load(path)
                self.add_document(doc)
                self.createdDocument.emit(doc.id)
                self.openedDocument.emit(doc.id, path.stem)
            except Exception:
                QMessageBox.critical(
                    None,
                    "Open File Error",
                    f"Unable to open project file: '{path}'",
                    QMessageBox.Ok,
                )

    def save_document(self, document: Document = None) -> bool:
        doc = document or self.get_active_document()
        if doc.path:
            try:
                doc.save()
                return True
            except Exception:
                self._save_error(doc)
                return False

        return self.save_document_as(doc)

    def save_document_as(self, document: Document = None) -> bool:
        doc = document or self.get_active_document()
        path = FileDialog.save_file()
        if path:
            try:
                doc.save(path)
                self.savedDocumentAs.emit(doc.id, path.stem)
                return True
            except Exception:
                self._save_error(doc)

        return False

    def close_document(self, doc_id: str) -> bool:
        if doc_id not in self._documents:
            return True

        if doc_id in self._unsaved_changes:
            doc = self.get_document(doc_id)
            name = doc.path or "Untitled"

            response = QMessageBox.question(
                None,
                "Unsaved changes",
                f"Save changes to '{name}'?",
                QMessageBox.Save | QMessageBox.Discard | QMessageBox.Cancel,
            )

            if response == QMessageBox.Cancel:
                return False
            elif response == QMessageBox.Save:
                return self.save_document(doc)
            elif response == QMessageBox.Discard:
                return True

        self._documents.pop(doc_id)
        self._unsaved_changes.discard(doc_id)
        self.documentRemoved.emit(doc_id)

        return True

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
            QMessageBox.Ok,
        )
