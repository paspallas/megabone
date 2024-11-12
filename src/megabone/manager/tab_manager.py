from PyQt5.QtCore import pyqtSignal
from PyQt5.QtWidgets import QTabWidget, QVBoxLayout, QWidget

from megabone.views import MainEditorView


class TabManager(QTabWidget):
    viewClosed = pyqtSignal(MainEditorView)
    viewActivated = pyqtSignal(MainEditorView)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setTabsClosable(True)
        self.setMovable(True)

        # Connect signals
        self.tabCloseRequested.connect(self._on_tab_close)
        self.currentChanged.connect(self._handle_tab_change)

    def add_editor(self, view: MainEditorView, title: str) -> int:
        # Wrap the view in a widget to ensure layout
        container = QWidget()
        layout = QVBoxLayout(container)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(view)

        index = self.addTab(container, title)
        self.setCurrentIndex(index)

        return index

    def set_title(self, index: int, title: str) -> None:
        self.setTabText(index, title)

    def set_view_title(self, doc_id: str, title: str) -> None:
        for i in range(self.count()):
            container = self.widget(i)
            view = container.findChild(MainEditorView)
            if view.doc_id == doc_id:
                self.set_title(i, title)
                break

    def close_view(self, doc_id) -> None:
        for i in range(self.count()):
            container = self.widget(i)
            view = container.findChild(MainEditorView)
            if view.doc_id == doc_id:
                self.removeTab(i)
                break

    def _handle_tab_change(self, index: int) -> None:
        if index >= 0:
            # Get the container widget and find the editor view
            container = self.widget(index)
            view = container.findChild(MainEditorView)
            if view:
                self.viewActivated.emit(view)

    def _on_tab_close(self, index: int) -> None:
        container = self.widget(index)
        view = container.findChild(MainEditorView)
        self.viewClosed.emit(view)
