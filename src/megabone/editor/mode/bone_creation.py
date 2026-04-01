from megabone.command.bone import CreateBoneCommand
from megabone.editor.item import BoneItem
from megabone.model.bone import BoneData
from megabone.qt import QPointF, Qt
from megabone.util.types import Point

from .abstract_mode import AbstractEditorMode
from .editor_mode_register import EditorModeRegistry


@EditorModeRegistry.register("Create a new bone", "B")
class CreateBoneMode(AbstractEditorMode):
    def __init__(self, controller):
        super().__init__(controller)
        self._ghost: BoneItem | None = None
        self._start_point: Point | None = Point(0, 0)

    def activate(self):
        self.view.setCursor(Qt.CursorShape.CrossCursor)

    def deactivate(self):
        self._cancel_ghost()
        self.view.setCursor(Qt.CursorShape.ArrowCursor)

    def mousePressEvent(self, event, scene_pos):
        if event.button() == Qt.MouseButton.LeftButton:
            if self._ghost is None:
                self._start_ghost(scene_pos, event.modifiers())
            else:
                self._commit()

        elif event.button() == Qt.MouseButton.RightButton:
            self._cancel_ghost()

    def mouseMoveEvent(self, event, scene_pos):
        if self._ghost:
            self._ghost.end_point = Point.from_qpointf(scene_pos)
            self._ghost.update()

    def mouseReleaseEvent(self, event, scene_pos):
        pass

    def _start_ghost(self, scene_pos: QPointF, modifiers) -> None:
        self._start_point = Point.from_qpointf(scene_pos)
        parent_bone = None

        if modifiers & Qt.KeyboardModifier.ShiftModifier:
            hit = self.scene.itemAt(scene_pos, self.view.transform())
            if isinstance(hit, BoneItem):
                parent_bone = hit
                parent_bone.setSelected(False)

        self._ghost = BoneItem.create_ghost(
            self.document,
            self._start_point,
            self._start_point + Point(1, 1),
        )

        if parent_bone:
            self._ghost.set_parent_bone(parent_bone)

        self.scene.add_item(self._ghost)

    def _commit(self) -> None:
        assert self._ghost is not None
        start_point: Point = self._ghost.start_point
        end_point: Point = self._ghost.end_point
        parent_id = self._ghost.parent_bone.id if self._ghost.parent_bone else ""

        # Remove ghost before pushing command
        self.scene.removeItem(self._ghost)
        self._ghost = None
        self._start_point = None

        bone_data = BoneData(
            start_point=start_point,
            end_point=end_point,
            parent_id=parent_id,
            name=self.document.bones.next_name("Bone"),
        )
        self.document.push(CreateBoneCommand(self.document, bone_data))

    def _cancel_ghost(self) -> None:
        if self._ghost:
            self.scene.remove_item(self._ghost)
            self._ghost = None
            self._start_point = None
