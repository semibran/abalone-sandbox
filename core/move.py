from dataclasses import dataclass
from enum import Enum
from core.hex import Hex, HexDirection

@dataclass
class Move:
    start: Hex
    end: Hex = None
    direction: HexDirection = None

    def pieces(self):
        if self.end is None:
            return (self.start,)

        for direction in HexDirection:
            pieces = [self.start]
            for i in range(2):
                pieces.append(Hex.add(pieces[-1], direction.value))
                if pieces[-1] == self.end:
                    return pieces
