from dataclasses import dataclass, field, fields
from typing import Self, get_type_hints
from uuid import uuid4

from megabone.util.types import Point


@dataclass
class Serializable:
    id: str = field(default_factory=lambda: uuid4().hex)
    name: str = ""
    z_index: int = -1

    def to_dict(self) -> dict:
        result = {}
        for f in fields(self):
            value = getattr(self, f.name)
            if isinstance(value, tuple):
                value = list(value)
            elif isinstance(value, Point):
                value = (value.x, value.y)
            result[f.name] = value
        return result

    @classmethod
    def from_dict(cls, data: dict) -> Self:
        hints = get_type_hints(cls)
        converted_data = {}

        for key, value in data.items():
            if hints.get(key) is Point:
                value = Point(value[0], value[1])
            converted_data[key] = value

        return cls(**converted_data)
