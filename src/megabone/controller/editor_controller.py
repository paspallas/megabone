from typing import Dict

from PyQt5.QtCore import QObject, pyqtSignal

from megabone.editor.mode import *
from megabone.manager import DocumentManager
from megabone.views import MainEditorView


class EditorController(QObject):
    """Manage all operations on the active document and
    Orchestrates the different views.
    """

    def __init__(self, doc_manager: DocumentManager) -> None:
        super().__init__()
        self.doc_manager = doc_manager
        self.views: Dict[int, MainEditorView] = {}

        # Register and init all edit modes
        EditorModeRegistry.init()
