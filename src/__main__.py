import sys

from PyQt6.QtWidgets import QApplication
from qtmodern import styles

from megabone.views import MegaBoneMainWindow as Win

if __name__ == "__main__":
    app = QApplication(sys.argv)
    styles.dark(app)

    window = Win()
    desktop = QApplication.screens()[0].geometry()
    window.move(desktop.left(), desktop.top())
    window.showMaximized()

    sys.exit(app.exec())
