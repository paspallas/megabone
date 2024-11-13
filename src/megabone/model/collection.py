from enum import Enum, auto
from typing import Any, Dict, List, Optional, Type

from PyQt5.QtCore import QObject, pyqtSignal

from .serializable import Serializable


class UpdateSource(Enum):
    MODEL = auto()
    VIEW = auto()
    UNDO = auto()


class BaseCollectionModel(QObject):
    itemAdded = pyqtSignal(str)
    itemRemoved = pyqtSignal(str)
    itemModified = pyqtSignal(str, UpdateSource)

    def __init__(self, data_class: Type[Serializable], key_name: str):
        super().__init__()
        self._items: Dict[str, Serializable] = {}
        self._updating = False
        self._data_class = data_class
        self.key_name = key_name

    def add_item(self, item_id: str, data: Serializable, source: UpdateSource):
        if not self._updating:
            self._updating = True
            self._items[item_id] = data
            self.itemAdded.emit(item_id)
            self._updating = False

    def remove_item(self, item_id: str, source: UpdateSource):
        if not self._updating and item_id in self._items:
            self._updating = True
            del self._items[item_id]
            self.itemRemoved.emit(item_id)
            self._updating = False

    def modify_item(self, item_id: str, data: Serializable, source: UpdateSource):
        if not self._updating and item_id in self._items:
            self._updating = True
            self._items[item_id] = data
            self.itemModified.emit(item_id, source)
            self._updating = False

    def get_item(self, item_id: str) -> Optional[Serializable]:
        return self._items.get(item_id)

    def to_list(self) -> List[Dict[str, Any]]:
        """Serialize all items to list of dictionary"""
        return [item.to_dict() for item in self._items.values()]

    def from_list(self, data: List[Dict[str, Any]]):
        """Load items from list of dictionary"""
        self._items.clear()
        for item_data in data:
            self._items[item_data.get("id", "")] = self._data_class.from_dict(item_data)
