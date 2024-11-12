import os
import tempfile
import time
from pathlib import Path
from typing import Dict, List, Optional, Set

from PyQt5.QtCore import QObject, QTimer, pyqtSignal

from megabone.model.document import Document

from .document_manager import DocumentManager


class AutoSaveManager(QObject):
    """Manage automatic backup of documents"""

    _MINIMUM_INTERVAL_SECS = 30
    _SAVE_INTERVAL_SECS = 2 * 60 * 1000

    autosaveCompleted = pyqtSignal(str)  # document id
    backupRecovered = pyqtSignal(str)  # document id

    def __init__(self, document_manager: DocumentManager):
        super().__init__()

        self.document_manager = document_manager
        self._autosave_timer = QTimer(self)
        self._dirty_documents: Set[str] = set()
        self._last_save_times: Dict[str, float] = {}
        self._backup_path = self._setup_backup_directory()

        # Configure timer
        self._autosave_timer.timeout.connect(self._perform_autosave)
        self._autosave_timer.setInterval(self._SAVE_INTERVAL_SECS)
        self._autosave_timer.start()

        # Connect signals
        self.document_manager.addedDocument.connect(self._on_document_added)
        self.document_manager.closedDocument.connect(self._on_document_removed)

    def _setup_backup_directory(self) -> Path:
        """Create and return the backup directory path"""
        app_data = Path(os.getenv("APPDATA") or tempfile.gettempdir())
        backup_dir = app_data / "MegaBone" / "backups"
        backup_dir.mkdir(parents=True, exist_ok=True)
        return backup_dir

    def mark_document_dirty(self, doc_id: str) -> None:
        """Schedule a document for autosave"""
        self._dirty_documents.add(doc_id)

    def _perform_autosave(self) -> None:
        current_time = time.time()

        for doc_id in list(self._dirty_documents):
            # Skip if the document was saved recently
            if (
                doc_id in self._last_save_times
                and current_time - self._last_save_times[doc_id]
                < self._MINIMUM_INTERVAL_SECS
            ):
                continue

            document = self.document_manager.get_document(doc_id)
            if not document:
                self._dirty_documents.discard(doc_id)
                continue

            try:
                self._save_backup(doc_id, document)
                self._last_save_times[doc_id] = current_time
                self._dirty_documents.discard(doc_id)
                self.autosaveCompleted.emit(doc_id)
            except Exception as e:
                self.document_manager.on_autosave_failed(doc_id, str(e))

    def _save_backup(self, doc_id: str, document: Document) -> None:
        """Save a backup of the document"""
        backup_file = self._get_backup_path(doc_id)

        # Create the temp file first
        temp_file = backup_file.with_sufix(".tmp")
        document.save(tempfile)

        # Atomic replacement of the backup file
        if backup_file.exists():
            backup_file.with_sufix(".bak").write_bytes(backup_file.read_bytes())
        temp_file.replace(backup_file)

    def _get_backup_path(self, doc_id: str) -> Path:
        """Returns the backup file path for a document"""
        safe_id = "".join(c if c.isalnum() else "_" for c in doc_id)
        return self._backup_path / f"{safe_id}.backup"

    def check_for_backups(self) -> List[str]:
        """Returns a list of document IDs with avalaible backups"""
        return [p.stem for p in self._backup_path.glob("*.backup")]

    def recover_backup(self, doc_id: str) -> Optional[Document]:
        """Attempts to recover a document from backup"""
        backup_file = self._get_backup_path(doc_id)
        if not backup_file.exists():
            return None

        try:
            document = Document.load(backup_file)
            self.backupRecovered.emit(doc_id)
            return document
        except Exception:
            # If main backup fails, try the .bak file
            backup_file = backup_file.with_suffix(".bak")
            if not backup_file.exists():
                return None

            try:
                document = Document.load(backup_file)
                self.backupRecovered.emit(doc_id)
                return document
            except Exception:
                return None

    def _on_document_added(self, doc_id: str) -> None:
        """Handle new document creation"""
        document: Document = self.document_manager.get_document(doc_id)
        if not document:
            return

        # Connect to document changes
        document.documentChanged.connect(lambda: self.mark_document_dirty(doc_id))

    def _on_document_removed(self, doc_id: str) -> None:
        """Clean up when a document is removed"""
        self._dirty_documents.discard(doc_id)
        self._last_save_times.pop(doc_id, None)
