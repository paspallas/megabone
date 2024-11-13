from dataclasses import dataclass, fields
from typing import Type, TypeVar

T = TypeVar("T", bound="Serializable")


@dataclass
class Serializable:
    id: str

    def to_dict(self) -> dict:
        """Serialize instance to dictionary"""
        result = {}
        for field in fields(self):
            value = getattr(self, field.name)
            # Handle type conversion
            if isinstance(value, tuple):
                value = list(value)
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
                    value = tuple(value)
            converted_data[key] = value

        return cls(**converted_data)
