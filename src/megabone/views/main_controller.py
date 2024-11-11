from PyQt5.QtCore import QObject, pyqtSignal
from PyQt5.QtWidgets import QMainWindow

from megabone.dialog import FileDialog
from megabone.editor import SkeletonEditor
from megabone.editor.mode import EditorModeRegistry
from megabone.manager.document_manager import DocumentManager


class MainController(QObject):
    enterFullScreen = pyqtSignal()
    enterZenMode = pyqtSignal()
    documentCreated = pyqtSignal()

    def __init__(self, main_window: QMainWindow) -> None:
        super().__init__()

        self.main_window = main_window

        # Manage all operations on the document model
        self.active_document = None
        self.document_manager = DocumentManager()

    def on_new(self):
        id = self.document_manager.create_document()
        editor = SkeletonEditor()
        actions = EditorModeRegistry.create_actions(editor)
        for action in actions.values():
            self.main_window.toolbar.addAction(action)

        index = self.main_window.tabs.addTab(editor, id)
        editor.showModalDialog()
        self.documentCreated.emit()

    def on_open(self):
        file = FileDialog.open_file()
        if file:
            pass

    def on_save(self):
        file = FileDialog.save_file()
        if file:
            pass

    def on_undo(self):
        pass

    def on_redo(self):
        pass

    def on_about(self):
        pass

    def on_quit(self):
        self.main_window.close()

    def on_full_screen(self):
        self.main_window.toggle_full_screen()

    def on_zen_mode(self):
        self.main_window.toggle_zen_mode()
