from PyQt5.QtWidgets import QLabel, QStatusBar
from PyQt5.QtCore import Qt, QTimer


class StatusBarManager:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(StatusBarManager, cls).__new__(cls)
            cls._instance.status_bar = None
            cls._instance.regions = {}
            cls._instance.timer = QTimer()
            cls._instance.timer.timeout.connect(cls._instance.clear_status)
        return cls._instance

    def initialize(self, status_bar: QStatusBar) -> None:
        self.status_bar = status_bar

    def add_region(self, name: str, width: int = 0) -> None:
        if self.status_bar and name not in self.regions:
            label = QLabel("", self.status_bar)
            if width > 0:
                label.setFixedWidth(width)
            self.status_bar.addPermanentWidget(label)
            self.regions[name] = label

    def set_status(self, message: str, region: str = None, timeout: int = 0) -> None:
        if self.status_bar:
            if region and region in self.regions:
                self.regions[region].setText(message)
                self.regions[region].setStyleSheet("")
            else:
                self.status_bar.showMessage(message)
            if timeout > 0:
                self.timer.start(timeout)

    def set_html_status(self, html_message: str, region: str) -> None:
        if self.status_bar and region in self.regions:
            self.regions[region].setText(html_message)
            self.regions[region].setTextFormat(Qt.RichText)

    def clear_status(self, region: str = None) -> None:
        if self.status_bar:
            if region and region in self.regions:
                self.regions[region].clear()
            else:
                self.status_bar.clearMessage()
        self.timer.stop()

    def clear_temp_status(self) -> None:
        self.clear_status()
