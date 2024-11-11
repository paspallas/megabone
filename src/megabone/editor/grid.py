from PyQt5.QtCore import QLineF, QPointF, QRectF, QSize, Qt
from PyQt5.QtGui import QBrush, QColor, QPainter, QPen
from PyQt5.QtWidgets import QGraphicsView


class EditorGrid:
    __backGridColor = QColor("#080808")
    __foreGridColor = QColor(210, 210, 210, 200)
    __darkColor = QColor("#404040")
    __lightColor = QColor("#666666")

    def __init__(self, view: QGraphicsView, size: int = 32) -> None:
        self.view = view
        self.megadrive_res = QSize(320, 224)
        self.grid_size = size
        self.view.drawForeground = self.drawForeground
        self.view.drawBackground = self.drawBackground

    def drawBackground(self, painter: QPainter, rect: QRectF) -> None:
        painter.setPen(QPen(Qt.NoPen))

        left = int(rect.left() - rect.left() % self.grid_size)
        top = int(rect.top() - rect.top() % self.grid_size)

        for y in range(top, int(rect.bottom()), self.grid_size):
            for x in range(left, int(rect.right()), self.grid_size):
                is_dark = (x / self.grid_size + y / self.grid_size) % 2

                color = self.__darkColor if is_dark else self.__lightColor
                painter.fillRect(
                    QRectF(x, y, self.grid_size, self.grid_size), QBrush(color)
                )

        l = rect.left()
        r = rect.right()
        t = rect.top()
        b = rect.bottom()

        # center visual indicator
        lines = [QLineF(l, 0, r, 0), QLineF(0, t, 0, b)]

        pen = QPen(self.__backGridColor, 0, Qt.SolidLine)
        pen.setCosmetic(True)
        painter.setPen(pen)
        painter.drawLines(*lines)
        pen.setColor(self.__foreGridColor)
        painter.setPen(pen)

        # Viewport rectangle
        painter.drawRect(
            QRectF(
                -self.megadrive_res.width() / 2,
                -self.megadrive_res.height() / 2,
                self.megadrive_res.width(),
                self.megadrive_res.height(),
            )
        )

    def drawForeground(self, painter: QPainter, rect) -> None:
        start = 6
        end = 2
        lines = [
            QLineF(-start, 0, -end, 0),
            QLineF(0, -start, 0, -end),
            QLineF(end, 0, start, 0),
            QLineF(0, start, 0, end),
        ]

        painter.setRenderHint(QPainter.Antialiasing)
        pen = QPen(self.__foreGridColor, 2, Qt.SolidLine)
        pen.setCosmetic(True)
        painter.setPen(pen)
        painter.drawLines(*lines)
        painter.drawEllipse(QPointF(0, 0), 1, 1)
