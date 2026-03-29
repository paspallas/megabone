from megabone.qt import QObject, Signal


class MainController(QObject):
    """Main window controller"""

    requestFullScreen = Signal()
    requestZenMode = Signal()
    requestQuit = Signal()

    def __init__(self) -> None:
        super().__init__()

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
