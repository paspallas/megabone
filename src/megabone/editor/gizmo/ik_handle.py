from PyQt5.QtCore import Qt, QRectF
from PyQt5.QtGui import QColor, QPen
from PyQt5.QtWidgets import QGraphicsItem

from .pole_vector import PoleControl
from .target_control import TargetControl
from megabone.editor.item import BoneGraphicsItem
from megabone.IKSolver import FABRIK


class IKHandle(QGraphicsItem):
    def __init__(
        self, start_bone: BoneGraphicsItem, end_bone: BoneGraphicsItem, parent=None
    ):
        super().__init__(parent)
        self.setFlag(QGraphicsItem.ItemIsMovable)
        self.setFlag(QGraphicsItem.ItemIsSelectable)
        self.setAcceptHoverEvents(True)

        # Store references to bones
        self.start_bone = start_bone
        self.end_bone = end_bone

        # Create IK chain
        self.buildChain()

        # Visual elements
        self.target = TargetControl(self)
        self.pole = PoleControl(self)

        # State
        self.hovering = False
        self.selected = False

    def buildChain(self):
        """Build the IK chain from start to end bone"""
        bones = []
        current = self.end_bone

        while current and current != self.start_bone.parent_bone:
            bones.insert(0, current)
            current = current.parent_bone

        self.chain = FABRIK(bones)

    def boundingRect(self):
        # Return rectangle that encompasses the entire chain
        rect = QRectF()
        for bone in self.chain.bones:
            rect = rect.united(
                QRectF(
                    bone.start_point.x(),
                    bone.start_point.y(),
                    bone.end_point.x() - bone.start_point.x(),
                    bone.end_point.y() - bone.start_point.y(),
                )
            )
        # Add padding for controls
        rect = rect.adjusted(-20, -20, 20, 20)
        return rect

    def paint(self, painter, option, widget):
        # if self.hovering or self.selected:
        # Draw chain influence visualization
        painter.setPen(QPen(QColor(255, 165, 0, 127), 1, Qt.DashLine))
        for bone in self.chain.bones:
            painter.drawLine(bone.start_point, bone.end_point)