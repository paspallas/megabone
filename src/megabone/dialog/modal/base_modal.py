from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QDialog, QWidget


class BaseModalDialog(QDialog):
    def __init__(self, parent: QWidget):
        super().__init__(parent)

        self.setWindowFlags(Qt.Dialog | Qt.FramelessWindowHint)
        self.setModal(True)
        self.setMinimumWidth(300)
        self.setFocusPolicy(Qt.StrongFocus)
