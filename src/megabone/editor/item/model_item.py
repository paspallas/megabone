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
        """Update model with current view state"""
        if not self._updating:
            data = self.create_model_data()
            self._model.modify_item(self.item_id, data, UpdateSource.VIEW)

    def update_from_model(self):
        """Update view with current model state"""
        data = self._model.get_item(self.item_id)
        if data:
            self.apply_model_data(data)

    def create_model_data(self) -> Serializable:
        """Override to create data object"""
        raise NotImplementedError()

    def apply_model_data(self, data: Serializable):
        """Override to apply data object"""
        raise NotImplementedError()
