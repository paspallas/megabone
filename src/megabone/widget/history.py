from megabone.qt import QLabel, QUndoView, QVBoxLayout, QWidget


class HistoryPanel(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(4, 4, 4, 4)
        layout.addWidget(QLabel("Undo History"))

        self._view = QUndoView()
        layout.addWidget(self._view)

    def set_stack(self, stack) -> None:
        self._view.setStack(stack)

    def set_group(self, group) -> None:
        self._view.setGroup(group)
