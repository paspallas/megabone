from megabone.qt import (
    QBrush,
    QColor,
    QGraphicsView,
    QLineF,
    QPainter,
    QPen,
    QPointF,
    QRect,
    QRectF,
    Qt,
)


class EditorGrid:
    __backGridColor = QColor("#00FFFF")
    __foreGridColor = QColor(210, 210, 210, 200)
    __darkColor = QColor("#404040")
    __lightColor = QColor("#666666")

    def __init__(self, view: QGraphicsView, size: int = 32) -> None:
        self.view = view
        self.grid_size = size
        self.view.drawForeground = self.drawForeground
        self.view.drawBackground = self.drawBackground

    def drawBackground(self, painter: QPainter, rect: QRectF | QRect) -> None:
        painter.setPen(QPen(Qt.PenStyle.NoPen))

        left = int(rect.left() - rect.left() % self.grid_size)
        top = int(rect.top() - rect.top() % self.grid_size)

        for y in range(top, int(rect.bottom()), self.grid_size):
            for x in range(left, int(rect.right()), self.grid_size):
                is_dark = (x / self.grid_size + y / self.grid_size) % 2

                color = self.__darkColor if is_dark else self.__lightColor
                painter.fillRect(
                    QRectF(x, y, self.grid_size, self.grid_size), QBrush(color)
                )

        left = rect.left()
        right = rect.right()
        top = rect.top()
        bottom = rect.bottom()

        lines = [QLineF(left, 0, right, 0), QLineF(0, top, 0, bottom)]

        pen = QPen(self.__backGridColor, 0, Qt.PenStyle.SolidLine)
        pen.setWidth(1)
        pen.setCosmetic(True)
        painter.setPen(pen)
        painter.drawLines(lines)

    def drawForeground(self, painter: QPainter, rect: QRectF | QRect) -> None:
        start = 6
        end = 2
        lines = [
            QLineF(-start, 0, -end, 0),
            QLineF(0, -start, 0, -end),
            QLineF(end, 0, start, 0),
            QLineF(0, start, 0, end),
        ]

        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        pen = QPen(self.__foreGridColor, 2, Qt.PenStyle.SolidLine)
        pen.setCosmetic(True)
        painter.setPen(pen)
        painter.drawLines(lines)
        painter.drawEllipse(QPointF(0, 0), 1, 1)
