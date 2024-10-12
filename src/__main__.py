import sys

from PyQt5.QtWidgets import QApplication
from megabone import MegaBoneMainWindow

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MegaBoneMainWindow()
    window.show()
    sys.exit(app.exec_())
