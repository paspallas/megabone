import random

from megabone.qt import (
    QColor,
    QGraphicsItem,
    QGraphicsPixmapItem,
    QGraphicsScene,
    QImage,
    QPainter,
    QPainterPath,
    QPen,
    QPixmap,
    QPoint,
    QRectF,
    QSize,
    Qt,
    qAlpha,
)


class Image:
    @staticmethod
    def flatten(pixmaps: list[QPixmap], size: QSize) -> QPixmap:
        result = QPixmap(size)
        result.fill(Qt.GlobalColor.transparent)
        painter = QPainter(result)

        for pixmap in pixmaps:
            painter.drawPixmap(0, 0, pixmap)
        painter.end()

        return result

    @staticmethod
    def checker_board(size: QSize, check_size: int = 32) -> QPixmap:
        background = QPixmap(size)
        background.fill(Qt.GlobalColor.transparent)
        painter = QPainter(background)

        dark = QColor("#404040")
        light = QColor("#666666")

        w = size.width()
        h = size.height()
        for x in range(0, w, check_size):
            for y in range(0, h, check_size):
                is_dark = (x / check_size + y / check_size) % 2
                color = dark if is_dark else light
                painter.fillRect(QRectF(x, y, check_size, check_size), color)

        painter.end()
        return background

    @staticmethod
    def grid(
        size: QSize,
        frame_width: int,
        frame_height: int,
        offset_x: int = 0,
        offset_y: int = 0,
        space_x: int = 0,
        space_y: int = 0,
    ) -> QPixmap:
        grid_pixmap = QPixmap(size)
        grid_pixmap.fill(Qt.GlobalColor.transparent)
        painter = QPainter(grid_pixmap)
        pen = QPen(QColor(220, 220, 220), 1, Qt.PenStyle.DashLine)
        pen.setCosmetic(True)
        painter.setPen(pen)

        # Compute number of rows and cols
        img_width = size.width() - offset_x
        img_height = size.height() - offset_y

        total_width = frame_width + space_x
        total_height = frame_height + space_y

        cols = (img_width + space_x) // total_width
        rows = (img_height + space_y) // total_height

        # Draw frame boundaries
        for row in range(rows):
            for col in range(cols):
                x = offset_x + col * total_width
                y = offset_y + row * total_height
                painter.drawRect(x, y, frame_width, frame_height)

        painter.end()
        return grid_pixmap

    @staticmethod
    def remove_background(image: QImage, bg_color: QColor):
        pixmap = QPixmap.fromImage(image)
        pixmap.setMask(pixmap.createMaskFromColor(bg_color))

        return pixmap.toImage()

    @staticmethod
    def is_transparent(image: QImage) -> bool:
        for y in range(image.height()):
            for x in range(image.width()):
                if qAlpha(image.pixel(x, y)) != 0:
                    return False
        return True

    @staticmethod
    def set_alpha(alpha: int, pixmap: QPixmap) -> QPixmap:
        transparent = QPixmap(pixmap.size())
        transparent.fill(Qt.GlobalColor.transparent)

        with QPainter(transparent) as painter:
            painter.setOpacity((100 - alpha) * 0.01)
            painter.drawPixmap(QPoint(), pixmap)

        return transparent

    @staticmethod
    def set_tint(alpha: int, tint: QColor, pixmap: QPixmap) -> QPixmap:
        alpha_mask = Image.set_alpha(alpha, pixmap)
        tinted = QPixmap(alpha_mask)

        with QPainter(alpha_mask) as painter:
            painter.setCompositionMode(
                QPainter.CompositionMode.CompositionMode_SourceIn
            )
            painter.fillRect(pixmap.rect(), tint)

        with QPainter(tinted) as painter:
            painter.setCompositionMode(QPainter.CompositionMode.CompositionMode_Overlay)
            painter.drawPixmap(QPoint(0, 0), alpha_mask, alpha_mask.rect())

        return tinted

    @staticmethod
    def flip_horizontal(item: QGraphicsItem) -> None:
        transform = item.transform()
        m11 = transform.m11()  # Horizontal scaling
        m12 = transform.m12()  # Vertical shearing
        m13 = transform.m13()  # Horizontal Projection
        m21 = transform.m21()  # Horizontal shearing
        m22 = transform.m22()  # vertical scaling
        m23 = transform.m23()  # Vertical Projection
        m31 = transform.m31()  # Horizontal Position (DX)
        m32 = transform.m32()  # Vertical Position (DY)
        m33 = transform.m33()  # Additional Projection Factor

        m31 = 0 if m31 > 0 else item.boundingRect().width() * m11

        transform.setMatrix(-m11, m12, m13, m21, m22, m23, m31, m32, m33)
        item.setTransform(transform)

    @staticmethod
    def flip_vertical(item: QGraphicsItem) -> None:
        transform = item.transform()
        m11 = transform.m11()  # Horizontal scaling
        m12 = transform.m12()  # Vertical shearing
        m13 = transform.m13()  # Horizontal Projection
        m21 = transform.m21()  # Horizontal shearing
        m22 = transform.m22()  # vertical scaling
        m23 = transform.m23()  # Vertical Projection
        m31 = transform.m31()  # Horizontal Position (DX)
        m32 = transform.m32()  # Vertical Position (DY)
        m33 = transform.m33()  # Additional Projection Factor

        m32 = 0 if m32 > 0 else item.boundingRect().height() * m22

        transform.setMatrix(m11, m12, m13, m21, -m22, m23, m31, m32, m33)
        item.setTransform(transform)

    @staticmethod
    def outline(pixmap: QPixmap) -> QPainterPath:
        return QGraphicsPixmapItem(pixmap).shape().simplified()

    @staticmethod
    def thumbnail_from_scene(scene: QGraphicsScene) -> QImage:
        scene.clearSelection()
        image = QImage(QSize(160, 112), QImage.Format.Format_ARGB32)
        image.fill(Qt.GlobalColor.transparent)

        with QPainter(image) as painter:
            painter.setRenderHint(QPainter.RenderHint.Antialiasing)
            scene.render(
                painter,
                QRectF(0, 0, 160, 112),
                scene.itemsBoundingRect(),
                Qt.AspectRatioMode.KeepAspectRatio,
            )

        return image

    @staticmethod
    def random_color() -> QColor:
        color = [
            random.randint(0, 255),
            random.randint(0, 255),
            random.randint(0, 255),
        ]
        return QColor(*color)

    @staticmethod
    def extract_sprites(
        image: QImage,
        frame_width: int,
        frame_height: int,
        offset_x: int = 0,
        offset_y: int = 0,
    ) -> list[QPixmap]:
        cols = (image.width() - offset_x) // frame_width
        rows = (image.height() - offset_y) // frame_height

        sprites = []

        for row in range(rows):
            for col in range(cols):
                x = (col * frame_width) + offset_x
                y = (row * frame_height) + offset_y
                sprite = image.copy(x, y, frame_width, frame_height)
                if not Image.is_transparent(sprite):
                    sprites.append(QPixmap.fromImage(sprite))
        return sprites
