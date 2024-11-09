from dataclasses import dataclass
from typing import Callable, Dict, Optional, Union

from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QAction, QMenu


@dataclass
class MenuItemState:
    enabled: bool = True
    visible: bool = True
    checked: bool = False
    text: Optional[str] = None


class MenuBuilder:
    def __init__(self, title: str, parent=None) -> None:
        self.menu = QMenu(title, parent)
        self.current_submenu = None
        self.parent = parent
        self._actions: Dict[str, QAction] = {}
        self._state_handlers: Dict[str, Callable[[], bool]] = {}

    def add_action(
        self,
        identifier: str,
        text: str,
        triggered: Optional[Callable] = None,
        shortcut: Optional[str] = None,
        icon: Optional[Union[QIcon, str]] = None,
        checkable: bool = False,
        state_handler: Optional[Callable[[], bool]] = None,
    ) -> "MenuBuilder":
        """Add an action to the menu"""
        target_menu = self.current_submenu or self.menu

        action = QAction(text, self.parent)

        if triggered:
            action.triggered.connect(triggered)
        if shortcut:
            action.setShortcut(shortcut)
        if icon:
            if isinstance(icon, str):
                action.setIcon(QIcon(icon))
            else:
                action.setIcon(icon)
        if checkable:
            action.setCheckable(True)

        if state_handler:
            self._state_handlers[identifier] = state_handler

        target_menu.addAction(action)
        self._actions[identifier] = action
        return self

    def update_item_state(self, identifier: str, state: MenuItemState) -> None:
        """Update the state of a specific menu item"""
        if action := self._actions.get(identifier):
            action.setEnabled(state.enabled)
            action.setVisible(state.visible)
            if action.isCheckable():
                action.setChecked(state.checked)
            if state.text:
                action.setText(state.text)

    def enable_items(self, *identifiers: str) -> None:
        """Enable specified menu items"""
        for identifier in identifiers:
            if action := self._actions.get(identifier):
                action.setEnabled(True)

    def disable_items(self, *identifiers: str) -> None:
        """Disable specified menu items"""
        for identifier in identifiers:
            if action := self._actions.get(identifier):
                action.setEnabled(False)

    def update_all_states(self) -> None:
        """Update all menu items with registered state handlers"""
        for identifier, handler in self._state_handlers.items():
            if action := self._actions.get(identifier):
                action.setEnabled(handler())

    def get_action(self, identifier: str) -> Optional[QAction]:
        """Get an action by its identifier"""
        return self._actions.get(identifier)

    def add_separator(self) -> "MenuBuilder":
        """Add a separator line to the menu"""
        target_menu = self.current_submenu or self.menu
        target_menu.addSeparator()
        return self

    def begin_submenu(self, title: str) -> "MenuBuilder":
        """Start creating a submenu"""
        self.current_submenu = QMenu(title, self.parent)
        return self

    def end_submenu(self) -> "MenuBuilder":
        """Finish creating a submenu and add it to the parent menu"""
        if self.current_submenu:
            target_menu = self.menu
            if hasattr(self, "_submenu_stack"):
                if self._submenu_stack:
                    target_menu = self._submenu_stack[-1]

            target_menu.addMenu(self.current_submenu)
            self.current_submenu = None
        return self

    def build(self) -> QMenu:
        """Return the constructed menu"""
        return self.menu
