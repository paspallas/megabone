from pathlib import Path
from typing import Dict

from PyQt5.QtCore import QObject, pyqtSignal
from PyQt5.QtWidgets import QMessageBox

from megabone.dialog import FileDialog
from megabone.manager import AutoSaveManager, DocumentManager, TabManager
from megabone.model.document import Document
from megabone.views.editor_view import MainEditorView

from .editor_controller import EditorController


class MainController(QObject):
    """Main window controller"""

    requestFullScreen = pyqtSignal()
    requestZenMode = pyqtSignal()
    requestQuit = pyqtSignal()
    documentCreated = pyqtSignal()

    def __init__(self, editor_area: TabManager) -> None:
        super().__init__()

        self._editor_area = editor_area

        self._document_manager = DocumentManager()
        self._autosave = AutoSaveManager(self._document_manager)

        self._editors: Dict[int, str] = {}
        self.active_document = None

        # Connect signals
        self._autosave.autosaveFailed.connect(self._document_manager.on_autosave_failed)
        # self._editor_area.currentChanged.connect(self._on_editor_select)
        # self._editor_area.tabClosed.connect(self._on_editor_close)

    def on_active_document_change(self) -> None:
        index = self._editor_area.currentIndex()
        self.active_document = self._document_manager.get_document(
            self._editors.get(index)
        )

    def on_new_document(self) -> None:
        doc = Document()
        self._document_manager.add_document(doc)

        index = self._editor_area.addTab(MainEditorView(), "Untitled.mgb*")
        self._editor_area.select(index)
        self._editors[index] = doc.id

        self.on_active_document_change()
        self.documentCreated.emit()

        # actions = EditorModeRegistry.create_actions(editor)
        # for action in actions.values():
        #     self.main_window.toolbar.addAction(action)

    # def _on_editor_select(self, index: int) -> None:
    #     doc_id = self._editors.get(index)
    #     self._active_document = self._document_manager.get_document(doc_id)

    # def _on_editor_close(self, index: int) -> None:
    #     if index in self._editors.keys():
    #         self._editors.pop(index)

    def on_open_document(self) -> None:
        file_path = FileDialog.open_file()
        if file_path:
            try:
                doc = Document.load(file_path)
                self._document_manager.add_document(doc)
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
