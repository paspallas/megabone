from PyQt5.QtWidgets import QGraphicsItem, QGraphicsOpacityEffect, QGraphicsObject
from PyQt5.QtCore import Qt, QTimer, QPropertyAnimation, QEasingCurve, QRectF, QPoint, pyqtProperty
from PyQt5.QtGui import QPainter, QColor, QFont


class StatusMessage(QGraphicsObject):
    def __init__(self, text: str, editor, duration_ms: int = 3000, fade_time: int = 3000):
        super().__init__()
        self.text = text
        self.editor = editor
        self.effect = QGraphicsOpacityEffect(self)
        self.setGraphicsEffect(self.effect)
        self.setOpacity(1.0)
        self._y_offset = 0

        # Ignore camera zoom and pan
        self.setFlag(QGraphicsItem.ItemIgnoresTransformations)

        self.updatePosition()
        self.editor.scene.addItem(self)

        # Message duration
        #QTimer.singleShot(duration_ms, self.start_fade_animation)

    def boundingRect(self) -> QRectF:
        return QRectF(0, 0, self.editor.width(), 50)

    def paint(self, painter, option, widget):
        painter.setPen(Qt.white)
        painter.setFont(QFont("Arial", 12))
        painter.drawText(self.boundingRect(), Qt.AlignLeft | Qt.AlignBottom, self.text)

    def updatePosition(self):
        view_rect = self.editor.viewport().rect()
        scene_pos = self.editor.mapToScene(view_rect.bottomLeft() + QPoint(10, -20))
        self.setPos(scene_pos)

    def start_fade_animation(self):
        # self.fade_animation = QPropertyAnimation(self.effect, propertyName=b"opacity")
        # self.fade_animation.setDuration(2000)
        # self.fade_animation.setStartValue(1.0)
        # self.fade_animation.setEndValue(0.0)
        # self.fade_animation.setEasingCurve(QEasingCurve.InOutQuad)
        # self.fade_animation.finished.connect(self.remove_from_scene)
        # self.fade_animation.start(QPropertyAnimation.DeleteWhenStopped)

        self.move_animation = QPropertyAnimation(self, b"y_offset")
        self.move_animation.setDuration(1000)
        self.move_animation.setStartValue(0)
        self.move_animation.setEndValue(-5)
        self.move_animation.setEasingCurve(QEasingCurve.InOutQuad)
        self.move_animation.finished.connect(self.remove_from_scene)
        self.move_animation.start()

    def remove_from_scene(self):
        if self.scene():
            self.scene().removeItem(self)

    # def set_opacity(self, opacity):
    #     self._opacity = opacity
    #     self.update()

    @pyqtProperty(float)
    def y_offset(self):
        return self._y_offset

    @y_offset.setter
    def y_offset(self, offset):
        self._y_offset = offset
        self.setY(self.y() + self._y_offset)
        self.update()

    #_opacity = property(fget=lambda self: self._opacity, fset=set_opacity)
    #_y_offset = property(fget=lambda self: self._y_offset, fset=set_y_offset)
