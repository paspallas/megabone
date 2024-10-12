from enum import Enum, auto


class EditorModeType(Enum):
    Selection = auto()
    CreateBone = auto()
    MoveIkChain = auto()
    CreateIkHandle = auto()
    AttachSprite = auto()
    Animation = auto()
