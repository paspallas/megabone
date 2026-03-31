from abc import abstractmethod

from megabone.model.collection import BaseCollectionModel
from megabone.model.document import Document
from megabone.model.serializable import Serializable
from megabone.qt import QGraphicsItem


class ModelBoundItem(QGraphicsItem):
    """
    Base for all scene items bound to a document model record.

    Lifecycle:
      - Created during scene rebuild with data from the model
      - Reads initial state via apply_data_from_model()
      - Writes back to model exclusively through document commands
    """

    def __init__(
        self,
        *args,
        item_id: str,
        model: BaseCollectionModel,
        document: Document,
        **kwargs,
    ):
        super().__init__(*args, **kwargs)
        self.item_id = item_id
        self._model = model
        self._document = document

    def push_command(self, command) -> None:
        """Push an undoable command to the document stack"""

        self._document.push(command)

    def current_data(self) -> Serializable:
        """Fetch the current model record for this item"""

        data = self._model.get_item(self.item_id)
        assert data is not None, f"No model data for item {self.item_id}"
        return data

    @abstractmethod
    def apply_data_from_model(self, data: Serializable) -> None:
        """Populate item state from model data. Called once during scene rebuild."""

        raise NotImplementedError

    @abstractmethod
    def create_data_for_model(self) -> Serializable:
        """Snapshot current item state into a model data object for use in commands."""

        raise NotImplementedError
