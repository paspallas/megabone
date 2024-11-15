from abc import abstractmethod
from dataclasses import fields

from PyQt5.QtWidgets import QGraphicsItem

from megabone.model.collection import BaseCollectionModel, UpdateSource
from megabone.model.serializable import Serializable


class ModelBoundItem(QGraphicsItem):
    def __init__(self, *args, item_id: str, model: BaseCollectionModel, **kwargs):
        super().__init__(*args, **kwargs)
        self.item_id = item_id
        self._model = model
        self._updating = False

        # Connect to model signals
        self._model.itemModified.connect(self._on_model_update)

    def _on_model_update(self, item_id: str, source: UpdateSource):
        if item_id == self.item_id and source != UpdateSource.VIEW:
            self._updating = True
            self.update_from_model()
            self._updating = False

    def update_model(self):
        """Update model with current item state"""
        if not self._updating:
            data = self.create_data_for_model()
            self._model.modify_item(data, UpdateSource.VIEW)

    def update_from_model(self):
        """Update item with current model state"""
        data = self._model.get_item(self.item_id)
        if data:
            self.apply_data_from_model(data)

    def itemChange(self, change, value):
        self.update_model()
        return super().itemChange(change, value)

    @abstractmethod
    def create_data_for_model(self) -> Serializable:
        raise NotImplementedError()

    def apply_data_from_model(self, data: Serializable):
        """Populate the item with data from the model"""
        for field in fields(data):
            if hasattr(self, field.name):
                setattr(self, field.name, getattr(data, field.name))
