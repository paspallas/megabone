from PyQt5.QtCore import QEvent, QObject, QPoint, Qt
from PyQt5.QtWidgets import QAbstractScrollArea, QApplication, QGraphicsView


class PanControl(QObject):
    """Add panning control with the middle mouse button to any QGraphicsView

    Args:
        view (QGraphicsView): The view
    """

    def __init__(self, view: QGraphicsView):
        super().__init__(view)

        view.viewport().installEventFilter(self)
        view.setDragMode(QGraphicsView.RubberBandDrag)

    def eventFilter(self, obj: QObject, e: QEvent) -> bool:
        scroll_area: QAbstractScrollArea = obj.parent()

        if scroll_area is None:
            return super().eventFilter(obj, e)

        if e.type() == QEvent.MouseButtonPress:
            if e.button() == Qt.MidButton:
                QApplication.setOverrideCursor(Qt.OpenHandCursor)

                self._start_pan_point = QPoint(
                    scroll_area.horizontalScrollBar().value() + e.x(),
                    scroll_area.verticalScrollBar().value() + e.y(),
                )

                return True

        elif e.type() == QEvent.MouseMove:
            if (e.buttons() & Qt.MidButton) == Qt.MidButton:
                scroll_area.horizontalScrollBar().setValue(
                    self._start_pan_point.x() - e.x()
                )
                scroll_area.verticalScrollBar().setValue(
                    self._start_pan_point.y() - e.y()
                )

        elif e.type() == QEvent.MouseButtonRelease:
            if e.button() == Qt.MidButton:
                QApplication.restoreOverrideCursor()

                return True

        return super().eventFilter(obj, e)
