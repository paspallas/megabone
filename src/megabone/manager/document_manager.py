from typing import Dict, Optional, Set

from PyQt5.QtCore import QObject, pyqtSignal
from PyQt5.QtWidgets import QMessageBox

from megabone.model.document import Document


class DocumentManager(QObject):
    """Manage the collection of documents."""

    documentAdded = pyqtSignal(str)
    documentRemoved = pyqtSignal(str)
    activeDocumentChanged = pyqtSignal(str)

    def __init__(self):
        super().__init__()

        self._documents: Dict[str, Document] = {}
        self._active_document_id: Optional[str] = None
        self._unsaved_changes: Set[str] = set()

    def get_document(self, doc_id: str) -> Optional[Document]:
        return self._documents.get(doc_id, None)

    def add_document(self, doc: Document) -> None:
        self._documents[doc.id] = doc

        # Connect to document signals
        doc.documentChanged.connect(lambda: self._on_document_changed(doc.id))

        self.documentAdded.emit(doc.id)

    def set_active_document(self, doc_id: str) -> None:
        if doc_id not in self._documents:
            return

        if self._active_document_id != doc_id:
            self._active_document_id = doc_id
            self.activeDocumentChanged.emit(doc_id)

    def close_document(self, doc_id: str) -> bool:
        if doc_id not in self._documents:
            return True

        if doc_id in self._unsaved_changes:
            response = QMessageBox.question(
                None,
                "Unsaved Changes",
                f"Save changes to {doc_id}?",
                QMessageBox.Save | QMessageBox.Discard | QMessageBox.Cancel,
            )

            if response == QMessageBox.Cancel:
                return False
            elif response == QMessageBox.Save:
                if not self._documents[doc_id].save():
                    return False

        del self._documents[doc_id]
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
            f"Failed to create backup for {doc_id}:\n{error_message}\n\n"
            "Please save your work manually as soon as possible.",
        )

    def _on_document_changed(self, doc_id: str) -> None:
        self._unsaved_changes.add(doc_id)
