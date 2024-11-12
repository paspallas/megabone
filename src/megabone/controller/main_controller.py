from pathlib import Path
from typing import Optional

from PyQt5.QtCore import QObject, pyqtSignal
from PyQt5.QtWidgets import QMessageBox

from megabone.dialog import FileDialog
from megabone.manager import AutoSaveManager, DocumentManager, TabManager
from megabone.model.document import Document
from megabone.views import MainEditorView

from .editor_controller import EditorController


class MainController(QObject):
    """Main window controller"""

    requestFullScreen = pyqtSignal()
    requestZenMode = pyqtSignal()
    requestQuit = pyqtSignal()
    documentCreated = pyqtSignal(str, MainEditorView)  # doc_id

    def __init__(self) -> None:
        super().__init__()
        self.active_document: Optional[Document] = None
        self.document_manager = DocumentManager()
        self.autosave = AutoSaveManager(self.document_manager)
        self.edit_controller = EditorController(self.document_manager)

        # Connect signals
        self.edit_controller.activeViewChanged.connect(self.on_active_view_change)

    def get_tab_widget(self) -> TabManager:
        return self.edit_controller.tab_widget

    def on_active_view_change(self, view: MainEditorView) -> None:
        self.active_document = self.document_manager.get_document(view.doc_id)

    def on_new_document(self) -> None:
        doc = Document()
        self.document_manager.add_document(doc)
        view = self.edit_controller.create_editor(doc.id, "Untitled*")
        self.documentCreated.emit(doc.id, view)

    def on_open_document(self) -> None:
        file_path = FileDialog.open_file()
        if file_path:
            try:
                doc = Document.load(file_path)
                self.document_manager.add_document(doc)
                self.edit_controller.create_editor(doc.id, Path(file_path).stem)
            except Exception:
                QMessageBox.critical(
                    None,
                    "Open File Error",
                    f"Unable to open project file: {file_path}",
                    QMessageBox.Ok,
                )

    def _save_error(self) -> None:
        QMessageBox.critical(
            None,
            "Save File Error",
            f"Unable to Save project file: {self.active_document.file_path}",
            QMessageBox.Ok,
        )

    def on_save_document(self) -> None:
        if self.active_document.file_path:
            try:
                self.active_document.save()
            except Exception:
                self._save_error()
        else:
            self.on_save_document_as()

    def on_save_document_as(self) -> None:
        file_path = FileDialog.save_file()
        if file_path:
            try:
                self.active_document.save(file_path)
                self.edit_controller.set_view_title(
                    self.active_document.id, Path(file_path).stem
                )
            except Exception:
                self._save_error()

    def on_undo(self) -> None:
        pass

    def on_redo(self) -> None:
        pass

    def on_about(self) -> None:
        pass

    def on_quit(self) -> None:
        self.requestQuit.emit()

    def on_full_screen(self) -> None:
        self.requestFullScreen.emit()

    def on_zen_mode(self) -> None:
        self.requestZenMode.emit()
