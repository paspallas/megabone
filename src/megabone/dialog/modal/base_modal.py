from megabone.qt import QDialog, Qt, QWidget


class BaseModalDialog(QDialog):
    def __init__(self, parent: QWidget):
        super().__init__(parent)

        self.setWindowFlags(Qt.WindowType.Dialog | Qt.WindowType.FramelessWindowHint)
        self.setModal(True)
        self.setMinimumWidth(300)
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
