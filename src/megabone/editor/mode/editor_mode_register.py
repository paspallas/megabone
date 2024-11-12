import re
from collections import OrderedDict
from enum import Enum
from typing import Optional, OrderedDict, Type

from PyQt5.QtWidgets import QAction, QActionGroup

from megabone.manager.resource_manager import ResourceManager as res

from .abstract_mode import AbstractEditorMode

add_underscore = re.compile(r"(.)([A-Z][a-z]+)")
handle_multi_uppercase = re.compile(r"([a-z0-9])([A-Z])")


def camel_to_snake(name: str) -> str:
    return handle_multi_uppercase.sub(
        r"\1_\2", add_underscore.sub(r"\1_\2", name)
    ).upper()


class EditorModeRegistry:
    """Manages editing modes for the editor"""

    class Mode(Enum):
        @classmethod
        def add_member(cls, name, value):
            setattr(cls, name, value)

    mode_value: int = 0
    mode_classes: OrderedDict[Mode, Type["AbstractEditorMode"]] = OrderedDict()
    mode_instances: OrderedDict[Mode, "AbstractEditorMode"] = OrderedDict()
    actions: OrderedDict[Mode, QAction] = OrderedDict()

    @classmethod
    def register(
        cls, description: str, shortcut: Optional[str], icon_name: Optional[str] = None
    ):
        def decorator(mode_class: Type["AbstractEditorMode"]):
            cls.Mode.add_member(camel_to_snake(mode_class.__name__), cls.mode_value)
            cls.mode_classes[cls.mode_value] = mode_class
            cls.mode_value += 1

            mode_class.description = description
            mode_class.shortcut = shortcut
            mode_class.icon_name = icon_name

            return mode_class

        return decorator

    @classmethod
    def init(cls, controller) -> None:
        for mode, mode_class in cls.mode_classes.items():
            cls.mode_instances[mode] = mode_class(controller)

    @classmethod
    def get_mode(cls, mode: Mode) -> "AbstractEditorMode":
        return cls.mode_instances[mode]

    @classmethod
    def create_actions(cls, controller) -> OrderedDict[Mode, QAction]:
        group = QActionGroup(controller)
        group.setExclusive(True)

        for mode, mode_instance in cls.mode_instances.items():
            action = QAction(controller)
            action.setText(mode_instance.description)
            action.setCheckable(True)

            if mode_instance.shortcut:
                action.setShortcut(mode_instance.shortcut)

            if mode_instance.icon_name:
                action.setIcon(res.get_icon(mode_instance.icon_name))

            action.triggered.connect(
                lambda checked, m=mode: controller.set_edit_mode(m)
            )

            group.addAction(action)
            cls.actions[mode] = action

        return cls.actions
