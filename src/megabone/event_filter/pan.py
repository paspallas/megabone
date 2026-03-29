from megabone.qt import (
    QAbstractScrollArea,
    QApplication,
    QEvent,
    QGraphicsView,
    QObject,
    QPoint,
    Qt,
)


class PanControl(QObject):
    """Add panning control with the middle mouse button to any QGraphicsView

    Args:
        view (QGraphicsView): The view
    """

    def __init__(self, view: QGraphicsView):
        super().__init__(view)

        viewport = view.viewport()

        assert viewport is not None
        viewport.installEventFilter(self)
        view.setDragMode(QGraphicsView.DragMode.RubberBandDrag)

    def eventFilter(self, a0: QObject | None, a1: QEvent | None) -> bool:
        assert a0 is not None
        scroll_area = a0.parent()

        if scroll_area is None:
            return super().eventFilter(a0, a1)

        assert a1 is not None
        if a1.type() == QEvent.Type.MouseButtonPress:
            if a1.button() == Qt.MouseButton.MiddleButton:
                QApplication.setOverrideCursor(Qt.CursorShape.OpenHandCursor)

                self._start_pan_point = QPoint(
                    scroll_area.horizontalScrollBar().value() + int(a1.position().x()),
                    scroll_area.verticalScrollBar().value() + int(a1.position().y()),
                )

                return True

        elif a1.type() == QEvent.Type.MouseMove:
            if (
                a1.buttons() & Qt.MouseButton.MiddleButton
            ) == Qt.MouseButton.MiddleButton:
                scroll_area.horizontalScrollBar().setValue(
                    self._start_pan_point.x() - int(a1.position().x())
                )
                scroll_area.verticalScrollBar().setValue(
                    self._start_pan_point.y() - int(a1.position().y())
                )

        elif a1.type() == QEvent.Type.MouseButtonRelease:
            if a1.button() == Qt.MouseButton.MiddleButton:
                QApplication.restoreOverrideCursor()

                return True

        return super().eventFilter(a0, a1)
