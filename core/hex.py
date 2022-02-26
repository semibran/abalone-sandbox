from dataclasses import dataclass
from enum import Enum

@dataclass(frozen=True)
class Hex:
    x: int
    y: int

    def __eq__(self, other):
        return self.x == other.x and self.y == other.y

    def astuple(self):
        return (self.x, self.y)

    def add(self, other):
        return Hex(self.x + other.x, self.y + other.y)

class HexDirection(Enum):
    NW = Hex(0, -1)
    NE = Hex(1, -1)
    W = Hex(-1, 0)
    E = Hex(1, 0)
    SW = Hex(-1, 1)
    SE = Hex(0, 1)
