from dataclasses import dataclass, fields
from typing import Type, TypeVar
from uuid import uuid4

from PyQt5.QtCore import QPointF

T = TypeVar("T", bound="Serializable")


@dataclass
class Serializable:
    id: str = ""

    def __post_init__(self):
        if not self.id:
            self.id = uuid4().hex

    def to_dict(self) -> dict:
        """Serialize instance to dictionary"""
        result = {}
        for field in fields(self):
            value = getattr(self, field.name)
            # Handle type conversion
            if isinstance(value, tuple):
                value = list(value)
            elif isinstance(value, QPointF):
                value = tuple([value.x(), value.y()])
            result[field.name] = value
        return result

    @classmethod
    def from_dict(cls: Type[T], data: dict) -> T:
        """Deserialize instance from dictionary"""
        field_types = {field.name: field.type for field in fields(cls)}
        converted_data = {}

        for key, value in data.items():
            if key in field_types:
                if field_types[key] == tuple and isinstance(value, (list, tuple)):
                    value = QPointF(value[0], value[1])
            converted_data[key] = value

        return cls(**converted_data)
