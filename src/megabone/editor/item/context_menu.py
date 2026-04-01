from __future__ import annotations

from typing import TYPE_CHECKING, Callable

from megabone.qt import QAction, QMenu, QWidget

if TYPE_CHECKING:
    from .model_item import ModelBoundItem


class ContextMenuBuilder:
    """Fluent builder for item context menus"""

    def __init__(self, parent: QWidget | None = None):
        self._menu = QMenu(parent)
        self._item: ModelBoundItem | None = None

    def for_item(self, item: ModelBoundItem) -> "ContextMenuBuilder":
        self._item = item
        return self

    def section(self, title: str) -> "ContextMenuBuilder":
        self._menu.addSection(title)
        return self

    def separator(self) -> "ContextMenuBuilder":
        self._menu.addSeparator()
        return self

    def action(
        self,
        label: str,
        callback: Callable,
        enabled: bool = True,
        shortcut: str = "",
    ) -> "ContextMenuBuilder":
        act = QAction(label, self._menu)
        act.setEnabled(enabled)
        if shortcut:
            act.setShortcut(shortcut)
        act.triggered.connect(callback)
        self._menu.addAction(act)
        return self

    def submenu(self, label: str) -> "SubmenuBuilder":
        sub = QMenu(label, self._menu)
        self._menu.addMenu(sub)
        return SubmenuBuilder(sub, self)

    def build(self) -> QMenu:
        return self._menu


class SubmenuBuilder:
    def __init__(self, menu: QMenu, parent_builder: ContextMenuBuilder):
        self._menu = menu
        self._parent = parent_builder

    def action(
        self,
        label: str,
        callback: Callable,
        enabled: bool = True,
    ) -> "SubmenuBuilder":
        act = QAction(label, self._menu)
        act.setEnabled(enabled)
        act.triggered.connect(callback)
        self._menu.addAction(act)
        return self

    def end(self) -> ContextMenuBuilder:
        return self._parent
