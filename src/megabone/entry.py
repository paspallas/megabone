import sys

from PyQt5.QtWidgets import QApplication
from typing import List

from .ui import MegaBoneMainWindow


def entry(args: List[str]) -> None:
    app = QApplication(sys.argv)
    window = MegaBoneMainWindow()
    window.show()
    sys.exit(app.exec_())
