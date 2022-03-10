from core.hex import Hex, HexDirection
from config import BOARD_MAXCOLS

class Move:

    def __init__(self, start, end=None, direction=None):
        self.direction = direction
        self._start = start
        self._end = end
        self._pieces = ()

    def __repr__(self):
        return "->".join((
            "..".join((
                str(self.start),
                *([str(self.end)] if self.end and self.end != self.start else [])
            )),
            *([self.direction.name] if self.direction else []),
        ))

    def __hash__(self):
        return (hash(self.start)
             + hash(self.end) * pow(BOARD_MAXCOLS, 2)
             + list(HexDirection).index(self.direction) * pow(BOARD_MAXCOLS, 3))

    @property
    def start(self):
        return self._start

    @start.setter
    def start(self, start):
        self._start = start
        self._pieces = ()

    @property
    def end(self):
        return self._end

    @end.setter
    def end(self, end):
        self._end = end
        self._pieces = ()

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

    def tail(self):
        if self.direction is None:
            return self.start or self.end

        if self.end is None or self.start == self.end:
            return self.start

        disp = Hex.subtract(self.end, self.start)
        normal = Hex(disp.x / (abs(disp.x) or 1), disp.y / (abs(disp.y) or 1))
        if self.direction.value == normal:
            return self.start
        else:
            return self.end

    def pieces(self):
        if not self._pieces:
            if self.end is None or self.end == self.start:
                self._pieces = (self.start,)
                return self._pieces

            for direction in HexDirection:
                pieces = [self.start]
                for i in range(2):
                    pieces.append(Hex.add(pieces[-1], direction.value))
                    if pieces[-1] == self.end:
                        self._pieces = tuple(pieces)
                        return self._pieces

        return self._pieces

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
