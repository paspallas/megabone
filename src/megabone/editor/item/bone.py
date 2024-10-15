import math

from PyQt5.QtCore import Qt, QPointF, QRectF
from PyQt5.QtGui import (
    QBrush,
    QColor,
    QLinearGradient,
    QPainter,
    QPainterPath,
    QPen,
    QTransform,
)
from PyQt5.QtWidgets import QGraphicsItem


class BoneItem(QGraphicsItem):
    def __init__(self, start_point, end_point, parent=None):
        super().__init__(parent)
        self.start_point = start_point
        self.end_point = end_point
        self.setAcceptHoverEvents(True)
        self.setFlag(QGraphicsItem.ItemIsSelectable)

        self.parent_bone = None
        self.child_bones = []
        self.connected_sprites = []

        # Store the initial local transform
        self.local_length = self.calculateLength()
        self.local_angle = self.calculateAngle()

        self.is_hovered = False
        self.is_selected = False

        # Custom properties
        self.bone_width_start = 6
        self.bone_width_end = 2
        self.primary_color = QColor(230, 230, 230)
        self.hover_color = QColor(200, 200, 255)
        self.selected_color = QColor(100, 150, 255)

    def boundingRect(self) -> QRectF:
        return self.shape().boundingRect()

    def shape(self) -> QPainterPath:
        # Calculate bone direction and perpendicular vectors
        dx = self.end_point.x() - self.start_point.x()
        dy = self.end_point.y() - self.start_point.y()
        length = math.sqrt(dx**2 + dy**2)

        if length < 1e-6:
            return

        # Normalized perpendicular vector
        nx = -dy / length
        ny = dx / length

        # Calculate corner points for the bone shape
        start_left = QPointF(
            self.start_point.x() + nx * self.bone_width_start / 2,
            self.start_point.y() + ny * self.bone_width_start / 2,
        )
        start_right = QPointF(
            self.start_point.x() - nx * self.bone_width_start / 2,
            self.start_point.y() - ny * self.bone_width_start / 2,
        )
        end_left = QPointF(
            self.end_point.x() + nx * self.bone_width_end / 2,
            self.end_point.y() + ny * self.bone_width_end / 2,
        )
        end_right = QPointF(
            self.end_point.x() - nx * self.bone_width_end / 2,
            self.end_point.y() - ny * self.bone_width_end / 2,
        )

        # Draw the bone shape
        path = QPainterPath()
        path.moveTo(start_left)
        path.lineTo(end_left)
        path.lineTo(end_right)
        path.lineTo(start_right)
        path.closeSubpath()

        return path

    def calculateLength(self):
        return math.sqrt(
            (self.end_point.x() - self.start_point.x()) ** 2
            + (self.end_point.y() - self.start_point.y()) ** 2
        )

    def calculateAngle(self):
        dx = self.end_point.x() - self.start_point.x()
        dy = self.end_point.y() - self.start_point.y()

        return math.atan2(dy, dx)

    def detachParentBone(self):
        if self.parent_bone:
            self.parent_bone.child_bones.remove(self)

    def setParentBone(self, parent_bone):
        self.detachParentBone()
        self.parent_bone = parent_bone

        if parent_bone:
            parent_bone.child_bones.append(self)
            # Update start point to parent's end point
            self.start_point = parent_bone.end_point
            self.update()

    def updateChildrenTransform(self):
        for child in self.child_bones:
            # Update child's start point to match parent's end point
            child.start_point = self.end_point
            child.update()
            # Recursively update all descendants
            child.updateChildrenTransform()

    def updateSpriteTransform(self, sprite):
        """Update the transform of an attached sprite based on bone position"""

        # TODO separate model from view
        # rotation = self.calculateAngle()
        # pos = self.start_point + sprite.bone_offset.rotated(rotation)
        # sprite.initial_rotation = rotation

        # sprite.setPos(pos)
        # sprite.setRotation(sprite.rotation)
        # Create transform
        transform = QTransform()

        # Move to bone start position
        transform.translate(self.start_pos.x(), self.start_pos.y())

        # Apply bone rotation
        bone_angle = self.calculateAngle()
        transform.rotate(math.degrees(bone_angle))

        # Apply local position offset
        transform.translate(sprite.pos().x(), sprite.pos().y())

        # Apply local rotation
        transform.rotate(sprite.rotation())

        # Set the sprite's transform
        sprite.setTransform(transform)

    def updateAllSpritessprites(self):
        """Update all attached sprites when bone moves"""
        for sprite in self.attached_sprites:
            self.updateSpriteTransform(sprite)

    def itemChange(self, change, value):
        """Handle bone movement and update sprites"""
        if change == QGraphicsItem.ItemPositionChange:
            # Update sprites when bone moves
            self.update_all_sprites()
        return super().itemChange(change, value)

    def paint(self, painter, option, widget):
        painter.setRenderHint(QPainter.Antialiasing)

        # Create gradient for 3D effect
        gradient = QLinearGradient(self.start_point, self.end_point)

        # Set colors based on state
        if self.is_selected:
            base_color = self.selected_color
        elif self.is_hovered:
            base_color = self.hover_color
        else:
            base_color = self.primary_color

        gradient.setColorAt(0, base_color.lighter(120))
        gradient.setColorAt(1, base_color.darker(120))

        # Draw the bone
        path = self.shape()
        painter.setPen(QPen(base_color.darker(150), 1))
        painter.setBrush(QBrush(gradient))
        painter.drawPath(path)

        # Add joint circles at the ends
        joint_radius = min(self.bone_width_start, self.bone_width_end) * 0.6
        painter.setBrush(QBrush(base_color.darker(120)))
        painter.drawEllipse(self.start_point, joint_radius, joint_radius)

    def hoverEnterEvent(self, event):
        self.is_hovered = True
        self.update()
        super().hoverEnterEvent(event)

    def hoverLeaveEvent(self, event):
        self.is_hovered = False
        self.update()
        super().hoverLeaveEvent(event)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.is_selected = not self.is_selected
            self.update()
        super().mousePressEvent(event)
