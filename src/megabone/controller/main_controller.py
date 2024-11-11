from pathlib import Path
from typing import Dict

from PyQt5.QtCore import QObject, pyqtSignal

from megabone.dialog import FileDialog
from megabone.manager import AutoSaveManager, DocumentManager, TabManager
from megabone.views.editor_view import MainEditor


class MainController(QObject):
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
        self._active_document = None

        # Connect signals
        self._autosave.autosaveFailed.connect(self._document_manager.on_autosave_failed)
        self._editor_area.currentChanged.connect(self._on_editor_select)
        self._editor_area.tabClosed.connect(self._on_editor_close)

    def on_new(self) -> None:
        doc_id = self._document_manager.create_document()
        self._active_document = self._document_manager.get_document(doc_id)
        index = self._editor_area.addTab(MainEditor(), "Untitled.mgb*")
        self._editor_area.select(index)
        self._editors[index] = doc_id

        self.documentCreated.emit()

        # actions = EditorModeRegistry.create_actions(editor)
        # for action in actions.values():
        #     self.main_window.toolbar.addAction(action)

    def _on_editor_select(self, index: int) -> None:
        doc_id = self._editors.get(index)
        self._active_document = self._document_manager.get_document(doc_id)

    def _on_editor_close(self, index: int) -> None:
        if index in self._editors.keys():
            self._editors.pop(index)

    def on_open(self) -> None:
        file_path = FileDialog.open_file()
        if file_path:
            doc_id = self._document_manager.load_document(Path(file_path))

    def on_save(self) -> None:
        file_path = FileDialog.save_file()
        if file_path is not None:
            path = Path(file_path)

            index = self._editor_area.currentIndex()
            doc = self._document_manager.get_document(self._editors.get(index))
            doc.name = path.stem

            self._editor_area.set_title(index, path.stem + ".mgb")

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
