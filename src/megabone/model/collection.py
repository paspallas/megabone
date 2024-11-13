from enum import Enum, auto
from typing import Dict, Optional, Type

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

    def __init__(self, data_class: Type[Serializable]):
        super().__init__()
        self._items: Dict[str, Serializable] = {}
        self._updating = False
        self._data_class = data_class

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

    def to_dict(self) -> dict:
        """Serialize all items to dictionary"""
        return {
            "items": {item_id: item.to_dict() for item_id, item in self._items.items()}
        }

    def from_dict(self, data: dict):
        """Load items from dictionary"""
        self._items.clear()
        for item_id, item_data in data.get("items", {}).items():
            self._items[item_id] = self._data_class.from_dict(item_data)
