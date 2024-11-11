import sys
from typing import List

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QApplication
from qtmodern import styles

from .ui import MegaBoneMainWindow as Win


def entry(args: List[str]) -> None:
    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)
    app = QApplication(sys.argv)
    styles.dark(app)

    window = Win()
    desktop = QApplication.desktop().screenGeometry(0)
    window.move(desktop.left(), desktop.top())
    window.showMaximized()

    sys.exit(app.exec_())
