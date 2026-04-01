from megabone.qt import QTabWidget, QVBoxLayout, QWidget, Signal
from megabone.views.editor_scene import ModalEditorScene
from megabone.views.editor_view import MainEditorView
from megabone.widget import WelcomeWidget


class TabManager(QTabWidget):
    viewClosed = Signal(MainEditorView)
    viewActivated = Signal(MainEditorView)

    _WELCOME_INDEX = 0

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setTabsClosable(True)
        self.setMovable(True)

        self.tabCloseRequested.connect(self._on_tab_close)
        self.currentChanged.connect(self._handle_tab_change)

        self._add_welcome_tab()

    def _add_welcome_tab(self) -> None:
        self._welcome = WelcomeWidget()
        index = self.addTab(self._welcome, "Welcome")

        # Not closable — hide the close button on this tab only
        self.tabBar().setTabButton(index, self.tabBar().ButtonPosition.RightSide, None)
        self.tabBar().setTabButton(index, self.tabBar().ButtonPosition.LeftSide, None)

    def _is_welcome_tab(self, index: int) -> bool:
        return self.widget(index) is self._welcome

    def show_welcome(self) -> None:
        """Switch back to welcome when all documents are closed"""

        for i in reversed(range(self.count())):
            if not self._is_welcome_tab(i):
                self.removeTab(i)
        self.setCurrentIndex(self._WELCOME_INDEX)

    def add_editor(self, view: MainEditorView, title: str) -> int:
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
        view = self._find_view(doc_id)
        if view:
            index = self._index_of_view(view)
            if index >= 0:
                self.set_title(index, title)

    def close_view(self, doc_id: str) -> None:
        view = self._find_view(doc_id)
        if not view:
            return

        index = self._index_of_view(view)
        if index >= 0:
            self.removeTab(index)

        # All editor tabs gone — show welcome
        if self._only_welcome_remains():
            self.setCurrentIndex(self._WELCOME_INDEX)

    def _handle_tab_change(self, index: int) -> None:
        if index < 0 or self._is_welcome_tab(index):
            return

        view = self._view_at(index)
        if view:
            self.viewActivated.emit(view)

    def _on_tab_close(self, index: int) -> None:
        if self._is_welcome_tab(index):
            return  # welcome tab is not closable

        view = self._view_at(index)
        if view:
            self.viewClosed.emit(view)

    def _view_at(self, index: int) -> MainEditorView | None:
        container = self.widget(index)
        if container is None:
            return None
        return container.findChild(MainEditorView)

    def _find_view(self, doc_id: str) -> MainEditorView | None:
        for i in range(self.count()):
            if self._is_welcome_tab(i):
                continue
            view = self._view_at(i)
            if view:
                scene = view.scene()

                assert isinstance(scene, ModalEditorScene)
                if scene.document.doc_id == doc_id:
                    return view
        return None

    def _index_of_view(self, view: MainEditorView) -> int:
        for i in range(self.count()):
            if self._view_at(i) is view:
                return i
        return -1

    def _only_welcome_remains(self) -> bool:
        return all(self._is_welcome_tab(i) for i in range(self.count()))
