from __future__ import annotations

from typing import TYPE_CHECKING

from megabone.qt import QPointF

from .context_menu import ContextMenuBuilder

if TYPE_CHECKING:
    from megabone.editor.item.bone import BoneItem
    from megabone.editor.item.model_item import ModelBoundItem
    from megabone.editor.item.sprite import SpriteItem


class ItemContextMenuFactory:
    @staticmethod
    def build_for(item: ModelBoundItem, scene_pos: QPointF) -> ContextMenuBuilder:
        from megabone.editor.item.bone import BoneItem
        from megabone.editor.item.sprite import SpriteItem

        builder = ContextMenuBuilder()

        if isinstance(item, BoneItem):
            ItemContextMenuFactory._bone_menu(builder, item, scene_pos)
        elif isinstance(item, SpriteItem):
            ItemContextMenuFactory._sprite_menu(builder, item, scene_pos)

        # Common to all items
        builder.separator().action(
            "Delete",
            lambda: item.request_delete(),
            shortcut="Del",
        )

        return builder

    @staticmethod
    def _bone_menu(
        builder: ContextMenuBuilder,
        bone: BoneItem,
        scene_pos: QPointF,
    ) -> None:
        scene = bone.scene()
        selected_sprites = (
            [
                i
                for i in scene.selectedItems()
                if hasattr(i, "_attachments")  # is a SpriteItem
                and i is not bone
            ]
            if scene
            else []
        )

        builder.section(f'Bone  "{bone.id}"')

        # Attach selected sprites
        builder.action(
            f"Attach {len(selected_sprites)} sprite(s) to this bone",
            lambda: bone.attach_selected_sprites(selected_sprites),
            enabled=len(selected_sprites) > 0,
        )

        # Detach all sprites
        builder.action(
            "Detach all sprites",
            lambda: bone.detach_all_sprites(),
            enabled=len(bone._attachments) > 0,
        )

        builder.separator()

        # Parent chain
        builder.action(
            "Detach from parent bone",
            lambda: bone.request_reparent(None),
            enabled=bone.parent_bone is not None,
        )

        # Children
        if bone.child_bones:
            (
                builder.submenu("Detach child bone").action(
                    "All children", lambda: bone.detach_all_children()
                )
                * ().end()
            )
            sub = builder.submenu("Detach child bone")
            for child in bone.child_bones:
                sub.action(
                    f'"{child.item_id[:8]}"',
                    lambda c=child: bone.request_detach_child(c),
                )
            sub.end()

        builder.separator()
        builder.action(
            "Set as root bone",
            lambda: bone.request_reparent(None),
            enabled=bone.parent_bone is not None,
        )

    @staticmethod
    def _sprite_menu(
        builder: ContextMenuBuilder,
        sprite: SpriteItem,
        scene_pos: QPointF,
    ) -> None:
        scene = sprite.scene()
        selected_bones = (
            [
                i
                for i in scene.selectedItems()
                if hasattr(i, "child_bones")  # is a BoneItem
                and i is not sprite
            ]
            if scene
            else []
        )

        builder.section(
            f'Sprite  "{sprite._path.split("/")[-1] or sprite.item_id[:8]}"'
        )

        builder.action(
            f"Attach to selected bone",
            lambda: sprite.request_attach_to_bone(selected_bones[0]),
            enabled=len(selected_bones) == 1,
        )
        builder.action(
            "Detach from bone",
            lambda: sprite.request_detach_from_bone(),
            enabled=sprite.attached_bone is not None,
        )

        builder.separator()

        builder.action(
            "Flip horizontal",
            lambda: sprite.request_flip_horizontal(),
        )
        builder.action(
            "Flip vertical",
            lambda: sprite.request_flip_vertical(),
        )

        builder.separator()

        # Frame picker submenu — only if sheet has multiple frames
        sheet = sprite._get_sheet()
        if sheet and len(sheet.frames) > 1:
            sub = builder.submenu("Switch frame")
            for frame in sheet.frames:
                sub.action(
                    f"Frame {frame.index}",
                    lambda idx=frame.index: sprite.request_frame_change(idx),
                    enabled=frame.index != sprite._frame_index,
                )
            sub.end()
