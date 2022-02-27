from dataclasses import dataclass
from enum import Enum

@dataclass(frozen=True)
class Hex:
    x: int
    y: int

    def __eq__(self, other):
        return self and other and self.x == other.x and self.y == other.y

    def astuple(self):
        return (self.x, self.y)

    def add(self, other):
        return Hex(self.x + other.x, self.y + other.y)

    def subtract(self, other):
        return Hex(self.x - other.x, self.y - other.y)

    def invert(self):
        return Hex(-self.x, -self.y)

    def manhattan(self, other):
        return (abs(self.x - other.x)
            + abs(self.x + self.y - other.x - other.y)
            + abs(self.y - other.y)) / 2

    def adjacent(self, other):
        return self.manhattan(other) == 1

    def neighbors(self):
        return [self.add(d.value) for d in HexDirection]

class HexDirection(Enum):
    NW = Hex(0, -1)
    NE = Hex(1, -1)
    W = Hex(-1, 0)
    E = Hex(1, 0)
    SW = Hex(-1, 1)
    SE = Hex(0, 1)

    @staticmethod
    def resolve(direction):
        return next((d for d in HexDirection if d.value == direction), None)
