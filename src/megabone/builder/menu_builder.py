from collections import deque
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
    def __init__(self, title: str) -> None:
        self._menu = QMenu(title)
        self._menu_stack: deque = deque([self._menu])

        self._actions: Dict[str, QAction] = {}
        self._sub_menus: Dict[str, QMenu] = {}
        self._state_handlers: Dict[str, Callable[[], bool]] = {}

        style = self.current_menu().styleSheet()
        self.current_menu().setStyleSheet(
            f""" 
                {style}
                QMenu::separator {{
                    height: 15px;
                    margin: 0px;
                    background: transparent;
                }}
            """
        )

    def disable(self) -> "MenuBuilder":
        """Disable the current menu"""
        self.current_menu().setDisabled(True)
        return self

    def enable(self, submenu: str) -> None:
        """Enable a submenu"""
        self._sub_menus.get(submenu, None).setEnabled(True)

    def action(
        self,
        name: str,
        callback: Optional[Callable] = None,
        shortcut: Optional[str] = None,
        icon: Optional[Union[QIcon, str]] = None,
        checkable: bool = False,
        tooltip: Optional[str] = None,
        state_handler: Optional[Callable[[], bool]] = None,
    ) -> "MenuBuilder":
        """Add an action to the current menu"""
        action = QAction(name)

        if tooltip:
            action.setToolTip(tooltip)
        if callback:
            action.triggered.connect(callback)
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
            self._state_handlers[name] = state_handler

        self.current_menu().addAction(action)
        self._actions[name] = action
        return self

    def separator(self) -> "MenuBuilder":
        """Add spacing to the current menu"""
        self.current_menu().addSeparator()
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

    def enable_items(self, *identifiers: str) -> "MenuBuilder":
        """Enable specified menu items"""
        for identifier in identifiers:
            if action := self._actions.get(identifier):
                action.setEnabled(True)
        return self

    def disable_items(self, *identifiers: str) -> "MenuBuilder":
        """Disable specified menu items"""
        for identifier in identifiers:
            if action := self._actions.get(identifier):
                action.setEnabled(False)
        return self

    def update_all_states(self) -> None:
        """Update all menu items with registered state handlers"""
        for identifier, handler in self._state_handlers.items():
            if action := self._actions.get(identifier):
                action.setEnabled(handler())

    def get_action(self, identifier: str) -> Optional[QAction]:
        """Get an action by its identifier"""
        return self._actions.get(identifier)

    def current_menu(self) -> QMenu:
        """Return the current menu context"""
        return self._menu_stack[-1]

    def submenu(self, title: str) -> "MenuBuilder":
        """Start creating a submenu"""
        submenu = QMenu(title, self.current_menu())
        self.current_menu().addMenu(submenu)
        self._menu_stack.append(submenu)
        self._sub_menus[title] = submenu
        return self

    def back(self) -> "MenuBuilder":
        """Go back to the parent menu"""
        if len(self._menu_stack) > 1:
            self._menu_stack.pop()
        return self

    def get_submenu(self, name: str) -> QMenu:
        """Get a submenu by name"""
        return self._sub_menus.get(name, None)

    def build(self) -> QMenu:
        """Return the constructed menu"""
        return self._menu
