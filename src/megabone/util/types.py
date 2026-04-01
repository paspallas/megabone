from __future__ import annotations

from dataclasses import dataclass
from typing import NamedTuple


class Size(NamedTuple):
    w: int
    h: int


@dataclass
class Point:
    x: float = 0.0
    y: float = 0.0

    def to_qpointf(self):
        from megabone.qt import QPointF

        return QPointF(self.x, self.y)

    @classmethod
    def from_qpointf(cls, point) -> "Point":
        return cls(x=point.x(), y=point.y())

    def __add__(self, other: "Point") -> "Point":
        return Point(self.x + other.x, self.y + other.y)

    def __sub__(self, other: "Point") -> "Point":
        return Point(self.x - other.x, self.y - other.y)

    def __mul__(self, scalar: float) -> "Point":
        return Point(self.x * scalar, self.y * scalar)

    def __rmul__(self, scalar: float) -> "Point":
        return self.__mul__(scalar)

    def __truediv__(self, scalar: float) -> "Point":
        if scalar == 0:
            raise ZeroDivisionError("Point division by zero")
        return Point(self.x / scalar, self.y / scalar)

    def __floordiv__(self, scalar: float) -> "Point":
        if scalar == 0:
            raise ZeroDivisionError("Point floor division by zero")
        return Point(self.x // scalar, self.y // scalar)

    def __neg__(self) -> "Point":
        return Point(-self.x, -self.y)

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Point):
            return NotImplemented
        return self.x == other.x and self.y == other.y

    def length(self) -> float:
        import math

        return math.sqrt(self.x**2 + self.y**2)

    def normalized(self) -> "Point":
        length = self.length()
        if length == 0:
            return Point(0.0, 0.0)
        return Point(self.x / length, self.y / length)

    def dot(self, other: "Point") -> float:
        return self.x * other.x + self.y * other.y

    def distance_to(self, other: "Point") -> float:
        return (self - other).length()

    def __iter__(self):
        yield self.x
        yield self.y

    def __repr__(self) -> str:
        return f"Point({self.x:.3f}, {self.y:.3f})"
