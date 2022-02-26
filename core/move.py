from dataclasses import dataclass
from core.hex import Hex, HexDirection

@dataclass
class Move:
    start: Hex
    end: Hex = None
    direction: HexDirection = None

    def head(self):
        return self.end or self.start

    def pieces(self):
        if self.end is None:
            return (self.start,)

        for direction in HexDirection:
            pieces = [self.start]
            for i in range(2):
                pieces.append(Hex.add(pieces[-1], direction.value))
                if pieces[-1] == self.end:
                    return pieces

    def targets(self):
        return [Hex.add(p, self.direction) for p in self.pieces()]

    def is_inline(self):
        if self.end is None:
            return False
        return Hex.subtract(self.pieces()[1], self.start) == self.direction
