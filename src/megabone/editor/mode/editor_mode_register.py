from collections import OrderedDict

from megabone.manager.resource import ResourceManager as res
from megabone.qt import QAction, QActionGroup

from .abstract_mode import AbstractEditorMode


class EditorModeRegistry:
    """Register tool edit modes"""

    _mode_instances: dict[type[AbstractEditorMode], AbstractEditorMode | None] = {}
    _actions: OrderedDict[type[AbstractEditorMode], QAction] = OrderedDict()

    @classmethod
    def register(
        cls, description: str, shortcut: str | None, icon_path: str | None = None
    ):
        def decorator(mode_class: type[AbstractEditorMode]):
            cls._mode_instances[mode_class] = None
            mode_class.description = description
            mode_class.shortcut = shortcut
            mode_class.icon_path = icon_path
            return mode_class

        return decorator

    @classmethod
    def init(cls, controller) -> None:
        for mode_class in cls._mode_instances.keys():
            cls._mode_instances[mode_class] = mode_class(controller)

    @classmethod
    def get_mode(cls, mode_class: type[AbstractEditorMode]) -> AbstractEditorMode:
        instance = cls._mode_instances[mode_class]

        assert instance is not None
        return instance

    @classmethod
    def create_actions(
        cls, controller
    ) -> OrderedDict[type[AbstractEditorMode], QAction]:
        group = QActionGroup(controller)
        group.setExclusive(True)

        for mode_class, mode_instance in cls._mode_instances.items():
            assert mode_instance is not None

            action = QAction(controller)
            action.setText(mode_instance.description)
            action.setCheckable(True)

            if mode_instance.shortcut:
                action.setShortcut(mode_instance.shortcut)

            if mode_instance.icon_path:
                action.setIcon(res.get_icon(mode_instance.icon_path))

            action.triggered.connect(
                lambda checked, m=mode_class: controller.set_edit_mode(m)
            )

            group.addAction(action)
            cls._actions[mode_class] = action

        return cls._actions
