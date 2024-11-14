from typing import Dict, Tuple

from megabone.model.bone import BoneData
from megabone.model.document import Document
from megabone.model.sprite import SpriteData

from .bone import BoneItem
from .sprite import SpriteItem


class ItemFactory:
    @staticmethod
    def add_items_from_document(document: Document, view):
        bones: Dict[str, Tuple[BoneData, BoneItem]] = {}

        for data in document.bones.get_items():
            # First pass, create all bones
            item = BoneItem(model=document.bones)
            item.apply_data_from_model(data)
            bones[data.id] = (data, item)

        for data, item in bones.values():
            # Second pass, rebuild parent child hierarchy
            if data.parent_id:
                item.set_parent_bone(bones[data.parent_id][1])

        view.add_items(*[item for _, item in bones.values()])
