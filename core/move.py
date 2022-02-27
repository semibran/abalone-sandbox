from dataclasses import dataclass
from core.hex import Hex, HexDirection
from config import BOARD_MAXCOLS

def format_cell(cell):
    return f"{chr(cell.x + 65)}{BOARD_MAXCOLS - cell.y}"

@dataclass
class Move:
    start: Hex
    end: Hex = None
    direction: HexDirection = None

    def __str__(self):
        return "(" + ", ".join([
            self.direction.name,
            format_cell(self.start),
            *([format_cell(self.end)] if self.end else [])
        ]) + ")"

    def head(self):
        if self.direction is None:
            return self.end or self.start

        if self.end is None or self.end == self.start:
            return self.start

        disp = Hex.subtract(self.end, self.start)
        normal = Hex(disp.x / (abs(disp.x) or 1), disp.y / (abs(disp.y) or 1))
        if self.direction.value == normal:
            return self.end
        else:
            return self.start

    def pieces(self):
        if self.end is None or self.end == self.start:
            return (self.start,)

        for direction in HexDirection:
            pieces = [self.start]
            for i in range(2):
                pieces.append(Hex.add(pieces[-1], direction.value))
                if pieces[-1] == self.end:
                    return pieces

        return ()

    def targets(self):
        return [Hex.add(p, self.direction.value) for p in self.pieces()]

    def target_cell(self):
        return Hex.add(self.head(), self.direction.value)

    def is_inline(self):
        if self.end is None or self.end == self.start:
            return False
        normal = Hex.subtract(self.pieces()[1], self.start)
        return (normal == self.direction.value
            or normal == self.direction.value.invert())
