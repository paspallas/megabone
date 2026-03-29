from enum import StrEnum


class PropertyType(StrEnum):
    POSITION = "position"
    ROTATION = "rotation"
    SCALE = "scale"
    IK_TARGET = "ik_target"
    IK_POLE = "ik_pole"
    SPRITE_OFFSET = "sprite_offset"
