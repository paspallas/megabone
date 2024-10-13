import sys

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QApplication
from typing import List

from .ui import MegaBoneMainWindow


def entry(args: List[str]) -> None:
    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)
    app = QApplication(sys.argv)
    
    window = MegaBoneMainWindow()
    desktop = QApplication.desktop().screenGeometry(0)
    window.move(desktop.left(), desktop.top())
    window.showMaximized()
    
    sys.exit(app.exec_())
