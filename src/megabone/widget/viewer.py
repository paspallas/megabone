from megabone.qt import (
    QColor,
    QFont,
    QGraphicsDropShadowEffect,
    QImage,
    QLabel,
    QPainter,
    QPainterPath,
    QPen,
    QPixmap,
    QPoint,
    QPointF,
    QRect,
    QScrollArea,
    Qt,
    QTransform,
    QWidget,
    Signal,
)


class Magnifier(QWidget):
    """Magnifiying lens"""

    def __init__(self, parent=None, zoom_factor: int = 8, radius: int = 64):
        super().__init__(parent)

        self.lens_size = radius * 2
        self.magnified_pos = QPoint()
        self.zoom_factor = zoom_factor
        self.lens_rect_size = int(self.lens_size / self.zoom_factor)

        self.source_pixmap: QPixmap | None = None

        self.setFixedSize(self.lens_size, self.lens_size)
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint
            | Qt.WindowType.Tool
            | Qt.WindowType.WindowStaysOnTopHint
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

    def set_source_pixmap(self, pixmap: QPixmap):
        self.source_pixmap = pixmap

    def update_magnified_area(self, pos: QPoint):
        self.magnified_pos = pos
        self.update()

    def paintEvent(self, event):
        if not self.source_pixmap:
            return

        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        # Create clipping path
        path = QPainterPath()
        path.addEllipse(0, 0, self.lens_size, self.lens_size)
        painter.setClipPath(path)

        # Source Rectangle top-left x,y with center at mouse coords
        src_x = self.magnified_pos.x() - self.lens_rect_size // 2
        src_y = self.magnified_pos.y() - self.lens_rect_size // 2
        src_rect = QRect(src_x, src_y, self.lens_rect_size, self.lens_rect_size)

        # Validate rectangle
        pixmap_rect = self.source_pixmap.rect()
        valid_src_rect = src_rect.intersected(pixmap_rect)

        # Offset from original source rectangle
        x_offset = valid_src_rect.x() - src_rect.x()
        y_offset = valid_src_rect.y() - src_rect.y()

        # Scale the offset by zoom factor to get the lens offset
        lens_x_offset = int(x_offset * self.zoom_factor)
        lens_y_offset = int(y_offset * self.zoom_factor)

        # Get the src rect magnified size
        src_width = int(valid_src_rect.width() * self.zoom_factor)
        src_height = int(valid_src_rect.height() * self.zoom_factor)

        # Destination rectangle in the lens widget at the correct offset and size
        dst_rect = QRect(lens_x_offset, lens_y_offset, src_width, src_height)

        # Copy and scale the valid portion of the source pixmap
        area = self.source_pixmap.copy(valid_src_rect).scaled(
            self.lens_size,
            self.lens_size,
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.FastTransformation,
        )

        # Compose the final image
        result = QPixmap(self.lens_size, self.lens_size)
        result.fill(Qt.GlobalColor.black)
        pix = QPainter(result)
        pix.drawPixmap(dst_rect, area)
        pix.end()

        painter.drawPixmap(0, 0, result)

        # Draw Crosshair
        center = self.lens_size // 2

        pen = QPen(Qt.GlobalColor.black, 3)
        pen.setCosmetic(True)
        painter.setPen(pen)

        # Horizontal
        painter.drawLine(
            QPointF(center - 10, center + 0.5), QPointF(center + 10, center + 0.5)
        )
        # Vertical
        painter.drawLine(
            QPointF(center + 0.5, center - 10), QPointF(center + 0.5, center + 10)
        )

        pen = QPen(Qt.GlobalColor.white, 1)
        pen.setCosmetic(True)
        painter.setPen(pen)

        # Horizontal
        painter.drawLine(
            QPointF(center - 10, center + 0.5), QPointF(center + 10, center + 0.5)
        )
        # Vertical
        painter.drawLine(
            QPointF(center + 0.5, center - 10), QPointF(center + 0.5, center + 10)
        )

        # Draw coordinates
        painter.setFont(QFont("Arial", 8))
        text = f"({self.magnified_pos.x()}, {self.magnified_pos.y()})"

        metrics = painter.fontMetrics()
        text_width = metrics.horizontalAdvance(text)
        text_height = metrics.height()
        text_x = (self.lens_size - text_width) // 2
        text_y = self.lens_size - 20

        # Text background
        painter.fillRect(
            text_x - 2,
            text_y - text_height,
            text_width + 4,
            text_height + 2,
            QColor(0, 0, 0, 127),
        )

        # Draw text
        painter.setPen(Qt.GlobalColor.white)
        painter.drawText(text_x, text_y, text)

        # Draw border
        painter.setPen(QPen(Qt.GlobalColor.black, 2))
        painter.drawEllipse(0, 0, self.lens_size, self.lens_size)


class ImageViewer(QLabel):
    clicked = Signal(object)
    zoomChanged = Signal(float)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.can_click = False

        # Zoom parameters
        self.zoom_factor = 1.0
        self.min_zoom = 1.0
        self.max_zoom = 12
        self.zoom_step = 0.1

        # Original pixmap
        self.original_pixmap: QPixmap | None = None

        # Magnifier setup
        self.magnifier = Magnifier(self)
        self.magnifier.hide()

        # Hover and zoom tracking
        self.setMouseTracking(True)

        # Shadow fx
        self.shadow = QGraphicsDropShadowEffect(self)
        self.shadow.setBlurRadius(20)
        self.shadow.setColor(QColor(0, 0, 0, 128))
        self.shadow.setOffset(8, 8)
        self.setGraphicsEffect(self.shadow)
        self.shadow.setEnabled(True)

    def toggle_click(self):
        self.can_click = not self.can_click
        if self.can_click:
            self.setCursor(Qt.CursorShape.CrossCursor)
        else:
            self.setCursor(Qt.CursorShape.ArrowCursor)

    def setPixmap(self, pixmap: QPixmap | QImage):
        """Set the original pixmap"""

        assert isinstance(pixmap, QPixmap)
        self.original_pixmap = pixmap
        self._update_displayed_pixmap()

        if self.magnifier:
            self.magnifier.set_source_pixmap(pixmap)

    def set_zoom(self, zoom_level: float):
        self.zoom_factor = max(self.min_zoom, min(self.max_zoom, zoom_level))
        self._update_displayed_pixmap()

    def _update_displayed_pixmap(self):
        """Apply zoom and update pixmap"""

        if not self.original_pixmap:
            return

        # Scale the pixmap
        transform = QTransform()
        transform.scale(self.zoom_factor, self.zoom_factor)

        # Apply zoom
        zoomed_pixmap = self.original_pixmap.transformed(transform)
        super().setPixmap(zoomed_pixmap)
        self.setFixedSize(zoomed_pixmap.size())

        self.zoomChanged.emit(self.zoom_factor)

    def mousePressEvent(self, event):
        if self.can_click and event.button() == Qt.MouseButton.LeftButton:
            original_pos = self._map_to_original_coords(event.pos())

            if original_pos:
                self.clicked.emit(original_pos)
                self.magnifier.hide()

        elif event.button() == Qt.MouseButton.RightButton:
            self.magnifier.hide()
            self.toggle_click()
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if not self.can_click:
            return

        scaled_pos = self._map_to_original_coords(event.pos())

        if scaled_pos is None:
            self.magnifier.hide()
            return

        global_pos = self.mapToGlobal(event.pos())
        self.magnifier.move(global_pos + QPoint(16, -16))
        self.magnifier.update_magnified_area(scaled_pos)
        self.magnifier.show()

    def leaveEvent(self, event):
        self.magnifier.hide()

    def _map_to_original_coords(self, pos) -> QPoint | None:
        """Map mouse widget coordinates to original image coordinates"""

        if not self.original_pixmap:
            return None

        pixmap_pos = pos - self._get_pixmap_offset()

        # Account for scaling
        point = QPoint(
            int(pixmap_pos.x() / self.zoom_factor),
            int(pixmap_pos.y() / self.zoom_factor),
        )

        # Point within image bounds?
        if self.original_pixmap.rect().contains(point):
            return point
        return None

    def _get_pixmap_offset(self) -> QPoint:
        if not self.pixmap():
            return QPoint(0, 0)

        # Get the scaled size
        scaled_size = self.pixmap().size()

        # Offset to center
        return QPoint(
            (self.width() - scaled_size.width()) // 2,
            (self.height() - scaled_size.height()) // 2,
        )


class ScrollImageViewer(QScrollArea):
    clicked = Signal(object)
    zoomChanged = Signal(float)

    def __init__(self, parent=None):
        super().__init__(parent)

        self.image_viewer = ImageViewer(self)
        self.setWidget(self.image_viewer)
        self.setWidgetResizable(True)
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setStyleSheet("background-color: rgba(80, 80, 80, 255);")

        self.image_viewer.clicked.connect(self.clicked)
        self.image_viewer.zoomChanged.connect(self.zoomChanged)

    def set_zoom(self, zoom_factor: float):
        self.image_viewer.set_zoom(zoom_factor)

    def setPixmap(self, pixmap: QPixmap):
        self.image_viewer.setPixmap(pixmap)

    def toggle_click(self):
        self.image_viewer.toggle_click()
