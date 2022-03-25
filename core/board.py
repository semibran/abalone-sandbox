from core.hex import Hex
from core.board_cell_state import BoardCellState
from config import BOARD_SIZE

def generate_empty_board(size):
  board = []
  for i in reversed(range(size)):
    board.insert(0, [0] * (size + i))
    if i < size - 1:
      board.append([0] * (size + i))
  return board

class Board:

    def __init__(self, layout=None):
        self._layout = layout
        self._data = generate_empty_board(size=BOARD_SIZE)
        self.__items = None
        self.__items_nonempty = None

    def __repr__(self):
        STATE_MAP = {
            1: "b",
            2: "w",
        }
        pieces = [str(cell) + STATE_MAP[cell_state.value]
            for cell, cell_state in self.enumerate()
                if cell_state != BoardCellState.EMPTY]
        pieces.sort(key=lambda piece: ord(piece[-1]) * 26 + ord(piece[0]) - 65)
        return ",".join(pieces)

    @property
    def layout(self):
        return self._layout

    def offset(self, r):
        return (self.height // 2 - r) * (r <= self.height // 2)

    def width(self, r):
        return (len(self._data[r])
            if r >= 0 and r < len(self._data)
            else None)

    @property
    def height(self):
        return len(self._data)

    def __contains__(self, cell):
        q, r = cell.astuple()
        q -= self.offset(r)
        return (r >= 0 and r < self.height
            and q >= 0 and q < self.width(r))

    def __getitem__(self, cell):
        if cell not in self:
            return None
        q, r = cell.astuple()
        q -= self.offset(r)
        return self._data[r][q]

    def __setitem__(self, cell, data):
        if cell in self:
            q, r = cell.astuple()
            q -= self.offset(r)
            self._data[r][q] = data
            self.__items = None
            self.__items_nonempty = None

    def enumerate(self):
        if not self.__items:
            items = []
            for r, line in enumerate(self._data):
                for q, val in enumerate(line):
                    q += self.offset(r)
                    item = (Hex(q, r), val)
                    items.append(item)
            self.__items = items
        return self.__items

    def enumerate_nonempty(self):
        if not self.__items_nonempty:
            items = []
            for r, line in enumerate(self._data):
                for q, val in enumerate(line):
                    if val == BoardCellState.EMPTY:
                        continue
                    q += self.offset(r)
                    item = (Hex(q, r), val)
                    items.append(item)
            self.__items_nonempty = items
        return self.__items_nonempty

    def fill(self, data):
        for cell, _ in self.enumerate():
            self[cell] = data
