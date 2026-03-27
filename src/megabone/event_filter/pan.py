from PyQt6.QtCore import QEvent, QObject, QPoint, Qt
from PyQt6.QtWidgets import QAbstractScrollArea, QApplication, QGraphicsView


class PanControl(QObject):
    """Add panning control with the middle mouse button to any QGraphicsView

    Args:
        view (QGraphicsView): The view
    """

    def __init__(self, view: QGraphicsView):
        super().__init__(view)

        view.viewport().installEventFilter(self)
        view.setDragMode(QGraphicsView.DragMode.RubberBandDrag)

    def eventFilter(self, obj: QObject, e: QEvent) -> bool:
        scroll_area: QAbstractScrollArea = obj.parent()

        if scroll_area is None:
            return super().eventFilter(obj, e)

        if e.type() == QEvent.Type.MouseButtonPress:
            if e.button() == Qt.MouseButton.MiddleButton:
                QApplication.setOverrideCursor(Qt.CursorShape.OpenHandCursor)

                self._start_pan_point = QPoint(
                    scroll_area.horizontalScrollBar().value() + e.position().x(),
                    scroll_area.verticalScrollBar().value() + e.position().y(),
                )

                return True

        elif e.type() == QEvent.Type.MouseMove:
            if (
                e.buttons() & Qt.MouseButton.MiddleButton
            ) == Qt.MouseButton.MiddleButton:
                scroll_area.horizontalScrollBar().setValue(
                    self._start_pan_point.x() - e.position().x()
                )
                scroll_area.verticalScrollBar().setValue(
                    self._start_pan_point.y() - e.position().y()
                )

        elif e.type() == QEvent.Type.MouseButtonRelease:
            if e.button() == Qt.MouseButton.MiddleButton:
                QApplication.restoreOverrideCursor()

                return True

        return super().eventFilter(obj, e)
