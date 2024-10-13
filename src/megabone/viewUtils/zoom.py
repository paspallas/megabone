from PyQt5.QtCore import (
    QEasingCurve,
    QEvent,
    QObject,
    Qt,
    QTimeLine,
    pyqtSlot,
    pyqtSignal,
)
from PyQt5.QtWidgets import QGraphicsView, QStyleOptionGraphicsItem


class ZoomControl(QObject):
    """Add Zoom control with the mouse wheel to any QGraphicsView

    Args:
        view (QGraphicsView): The view
        min_ (float): Minimum zoom level (defaults to 1)
        max_ (float): Maximum zoom level (defaults to 25)
    """

    zoomLevelChanged = pyqtSignal(float)

    def __init__(self, view: QGraphicsView, min_: float = 1, max_: float = 25):
        super().__init__(view)

        self._animation = QTimeLine(160, self)
        self._animation.setEasingCurve(QEasingCurve.InOutCubic)
        self._animation.setUpdateInterval(16)
        self._animation.valueChanged.connect(self._scalingTime)
        self._animation.finished.connect(self._animationFinished)
        self._numScalings = 0
        self._started = False

        self._view = view
        self._zoom_min = min_
        self._zoom_max = max_
        self._eventPos = None

        view.viewport().installEventFilter(self)

    def eventFilter(self, obj: QObject, e: QEvent) -> bool:
        view: QGraphicsView = obj.parent()

        if view is None:
            return super().eventFilter(obj, e)

        if e.type() == QEvent.Wheel:
            if e.modifiers() & (Qt.Modifier.CTRL | Qt.Modifier.ALT):
                return False

            self._eventPos = e.pos()
            self._numDegrees = e.angleDelta().y() / 8
            self._numSteps = self._numDegrees / 15
            self._numScalings += self._numSteps

            if self._numScalings * self._numSteps < 0:
                self._numScalings = self._numSteps

            if not self._started:
                self._started = True
                self._animation.start()

            return True

        return super().eventFilter(obj, e)

    def _zoom(self) -> float:
        return QStyleOptionGraphicsItem.levelOfDetailFromTransform(
            self._view.transform()
        )

    def _translate(self, oldPos: float) -> None:
        newPos = self._view.mapToScene(self._eventPos)
        delta = newPos - oldPos
        self._view.translate(delta.x(), delta.y())

    @pyqtSlot(float)
    def _scalingTime(self, val: float) -> None:
        oldPos = self._view.mapToScene(self._eventPos)

        factor = 1.0 + (self._numScalings / 160.0)
        level = self._zoom() * factor

        if self._zoom_min < level < self._zoom_max:
            level = self._zoom()
        elif level > self._zoom_max:
            factor = self._zoom_max / self._zoom()
            level = self._zoom_max
            self._numScalings = 0
        elif level < self._zoom_min:
            factor = self._zoom_min / self._zoom()
            level = self._zoom_min
            self._numScalings = 0

        self._view.scale(factor, factor)
        self._translate(oldPos)
        self.zoomLevelChanged.emit(level)

    @pyqtSlot(float)
    def setValue(self, value: float) -> None:
        transform = self._view.transform()
        m12 = transform.m12()  # Vertical shearing
        m13 = transform.m13()  # Horizontal Projection
        m21 = transform.m21()  # Horizontal shearing
        m23 = transform.m23()  # Vertical Projection
        m31 = transform.m31()  # Horizontal Position (DX)
        m32 = transform.m32()  # Vertical Position (DY)
        m33 = transform.m33()  # Additional Projection Factor

        if self._eventPos is None:
            self._view.setTransformationAnchor(QGraphicsView.AnchorViewCenter)
            transform.setMatrix(value, m12, m13, m21, value, m23, m31, m32, m33)
            self._view.setTransform(transform)
            self._view.setTransformationAnchor(QGraphicsView.NoAnchor)
        else:
            oldPos = self._view.mapToScene(self._eventPos)
            transform.setMatrix(value, m12, m13, m21, value, m23, m31, m32, m33)
            self._view.setTransform(transform)
            self._translate(oldPos)

    @pyqtSlot()
    def _animationFinished(self) -> None:
        if self._numScalings > 0:
            self._numScalings -= 1
        else:
            self._numScalings += 1

        self._started = False
