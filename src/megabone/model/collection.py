from enum import Enum, auto
from typing import Any, Type

from megabone.qt import QObject, Signal

from .serializable import Serializable


class UpdateSource(Enum):
    COMMAND = auto()
    LOAD = auto()
    AUTOSAVE = auto()


class BaseCollectionModel(QObject):
    itemAdded = Signal(str)
    itemRemoved = Signal(str)
    itemModified = Signal(str, UpdateSource)

    def __init__(self, data_class: Type[Serializable], key_name: str):
        super().__init__()
        self._items: dict[str, Serializable] = {}
        self._data_class = data_class
        self.key_name = key_name

    def add_item(self, data: Serializable, source: UpdateSource) -> None:
        self._items[data.id] = data
        self.itemAdded.emit(data.id)

    def remove_item(self, item_id: str, source: UpdateSource) -> None:
        if item_id in self._items:
            del self._items[item_id]
            self.itemRemoved.emit(item_id)

    def modify_item(self, data: Serializable, source: UpdateSource) -> None:
        if data.id in self._items:
            self._items[data.id] = data
            self.itemModified.emit(data.id, source)

    def next_name(self, base: str) -> str:
        existing = {item.name for item in self.get_items()}
        if base not in existing:
            return base
        i = 1
        while f"{base} {i}" in existing:
            i += 1
        return f"{base} {i}"

    def get_item(self, item_id: str) -> Serializable | None:
        return self._items.get(item_id)

    def get_items(self) -> list[Serializable]:
        return list(self._items.values())

    def to_list(self) -> list[dict[str, Any]]:
        return [item.to_dict() for item in self._items.values()]

    def from_list(self, data: list[dict[str, Any]]) -> None:
        self._items.clear()
        for item_data in data:
            self._items[item_data["id"]] = self._data_class.from_dict(item_data)
