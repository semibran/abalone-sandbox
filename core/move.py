from dataclasses import dataclass
from enum import Enum
from core.hex import Hex

class Direction(Enum):
    NW = (0, -1)
    NE = (1, -1)
    W = (-1, 0)
    E = (1, 0)
    SW = (-1, 1)
    SE = (0, 1)

@dataclass
class Move:
    start: tuple[int, int]
    end: tuple[int, int] = None
    direction: Direction = None

    def pieces(self):
        if self.end is None:
            return (self.start,)

        for direction in Direction:
            pieces = [Hex(*self.start)]
            for i in range(2):
                pieces.append(Hex.add(pieces[-1], Hex(*direction.value)))
                if pieces[-1].astuple() == self.end:
                    return tuple([p.astuple() for p in pieces])
        else:
            return None
