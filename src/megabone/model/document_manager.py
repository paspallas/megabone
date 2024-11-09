import uuid
from typing import Dict, Optional, Set

from PyQt5.QtCore import QObject, pyqtSignal
from PyQt5.QtWidgets import QMessageBox

from .document import Document


class DocumentManager(QObject):
    """Manage multiple documents and coordinate its views"""

    document_added = pyqtSignal(str)
    document_removed = pyqtSignal(str)
    active_document_changed = pyqtSignal(str)

    def __init__(self):
        super().__init__()

        self._documents: Dict[str, Document] = {}
        self._active_document_id: Optional[str] = None
        # self._view_sync_groups: Dict[str, Set[BaseAnimationView]] = {}
        self._unsaved_changes: Set[str] = set()

    def create_document(self) -> str:
        """Create a new empty document and return its ID"""
        doc = Document()
        doc_id = self.generate_document_id()
        self._documents[doc_id] = doc

        # Connect to document signals
        doc.document_changed.connect(lambda: self._on_document_changed(doc_id))

        self.document_added.emit(doc_id)
        return doc_id

    def generate_document_id(self) -> str:
        return uuid.uuid4().hex

    def set_active_document(self, doc_id: str) -> None:
        if doc_id not in self._documents:
            return

        if self._active_document_id != doc_id:
            self._active_document_id = doc_id
            self.active_document_changed.emit(doc_id)

    def close_document(self, doc_id: str) -> bool:
        """Attempts to close a document. Returns True on success"""
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
        self.document_removed.emit(doc_id)

        return True

    def _on_document_changed(self, doc_id: str) -> None:
        self._unsaved_changes.add(doc_id)
