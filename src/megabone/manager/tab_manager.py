from PyQt5.QtCore import pyqtSignal, pyqtSlot
from PyQt5.QtWidgets import QTabWidget


class TabManager(QTabWidget):
    tabClosed = pyqtSignal(int)

    def __init__(self, parent):
        super().__init__(parent)

        self.setTabsClosable(True)
        self.setMovable(True)

        # Connect signals
        self.tabCloseRequested.connect(self.on_tab_close)

    def select(self, index: int) -> None:
        self.setCurrentIndex(index)

    def set_title(self, index: int, title: str) -> None:
        self.setTabText(index, title)

    @pyqtSlot(int)
    def on_tab_close(self, index: int) -> None:
        self.removeTab(index)
        self.tabClosed.emit(index)
