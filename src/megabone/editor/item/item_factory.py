from megabone.model.document import Document
from megabone.model.serializable import Serializable


class ItemFactory:
    """Create scene items from document model data"""

    _registry: dict[type, type] = {}

    @classmethod
    def register(cls, data_type):
        def decorator(item_cls):
            cls._registry[data_type] = item_cls
            return item_cls

        return decorator

    @classmethod
    def create_items(cls, document: Document):
        created: dict[str, tuple[Serializable, object]] = {}

        for collection in document.get_all_collections():
            for data in collection.get_items():
                item_cls = cls._registry[data.__class__]

                item = item_cls(model=collection)
                item.apply_data_from_model(data)

                created[data.id] = (data, item)

        return created

    @classmethod
    def add_items_from_document(cls, document: Document, view):
        created = cls.create_items(document)

        # resolve relationships
        for _, item in created.values():
            if hasattr(item, "resolve_references"):
                item.resolve_references(created)

        view.add_items(*[item for _, item in created.values()])
