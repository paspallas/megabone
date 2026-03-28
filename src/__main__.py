import sys

from PyQt6.QtWidgets import QApplication
from qtmodern import styles

from megabone.views import AppMainWindow as Window

if __name__ == "__main__":
    app = QApplication(sys.argv)
    styles.dark(app)

    window = Window()
    desktop = QApplication.screens()[0].geometry()
    window.move(desktop.left(), desktop.top())
    window.showMaximized()

    sys.exit(app.exec())
