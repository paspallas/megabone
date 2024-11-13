from enum import Enum, auto
from typing import List

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QKeySequence
from PyQt5.QtWidgets import QGraphicsItem, QGraphicsView, QShortcut


class Layer(Enum):
    """Graphic item layer type. Values define the z-order"""

    SPRITE = auto()
    BONE = auto()
    GIZMO = auto()


class LayeredItemMixin:
    _items_per_layer = 100_000

    def __init__(self, *args, layer: Layer, z_index: float = 0, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.layer = layer
        self.z_index = z_index

    def update_z_value(self, z_index: float) -> None:
        """Set actual z-index after layer sorting"""
        self.z_index = z_index
        self.setZValue(self.calculate_value())

    def calculate_value(self) -> float:
        return self.layer.value * self._items_per_layer + self.z_index

    def __repr__(self) -> str:
        return f"Layer item(z-index={self.z_index}, layer={self.layer})"


class LayerManager:
    def __init__(self, view: QGraphicsView) -> None:
        self.items: LayeredItemMixin = []
        self.view = view

        self._setup_shortcuts()

    def add_item(self, item: QGraphicsItem) -> None:
        self.items.append(item)
        # New items are placed on top by default
        item.update_z_value(len(self.items))
        self.sort_layer(item.layer)

    def sort_layer(self, layer: Layer) -> None:
        layer_items = [item for item in self.items if item.layer == layer]
        layer_items.sort(key=lambda x: x.z_index)
        for i, item in enumerate(layer_items):
            item.update_z_value(i)

    def set_layer_visibility(self, layer: Layer, visible: bool) -> None:
        for item in self.items:
            if item.layer == layer:
                item.setVisible(visible)

    def set_layer_selectability(self, layer: Layer, selectable: bool) -> None:
        for item in self.items:
            if item.layer == layer:
                item.setFlag(QGraphicsItem.ItemIsSelectable, selectable)

    def _setup_shortcuts(self) -> None:
        self.item_up = QShortcut(QKeySequence(Qt.Key_Up), self.view)
        self.item_up.activated.connect(self._increase_z_index)

        self.item_down = QShortcut(QKeySequence(Qt.Key_Down), self.view)
        self.item_down.activated.connect(self._decrease_z_index)

    def _get_item(self) -> LayeredItemMixin:
        selected_items = self.view.scene().selectedItems()
        if selected_items:
            # Assume only one item is selected
            return selected_items[0]
        return None

    def _get_layer_items(self, layer: Layer) -> List[LayeredItemMixin]:
        items = [item for item in self.items if item.layer == layer]
        items.sort(key=lambda x: x.z_index)

        return items

    def _increase_z_index(self) -> None:
        if item := self._get_item():
            items = self._get_layer_items(item.layer)
            index = items.index(item)
            if index < len(items) - 1:
                items[index], items[index + 1] = items[index + 1], items[index]
                for i, item in enumerate(items):
                    item.update_z_value(i)

    def _decrease_z_index(self) -> None:
        if item := self._get_item():
            items = self._get_layer_items(item.layer)
            index = items.index(item)
            if index > 0:
                items[index], items[index - 1] = items[index - 1], items[index]
                for i, item in enumerate(items):
                    item.update_z_value(i)
