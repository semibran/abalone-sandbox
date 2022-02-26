from dataclasses import dataclass

@dataclass(frozen=True)
class Hex:
    x: int
    y: int

    def astuple(self):
        return (self.x, self.y)

    def add(self, other):
        return Hex(self.x + other.x, self.y + other.y)
