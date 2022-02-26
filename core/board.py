from core.hex import Hex

def generate_empty_board(size):
  board = []
  for i in reversed(range(size)):
    board.insert(0, [0] * (size + i))
    if i < size - 1:
      board.append([0] * (size + i))
  return board

class Board:
    def __init__(self):
        self._data = generate_empty_board(size=5)

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
        return (r >= 0 and r < self.height
            and q >= 0 and q < self.width(r))

    def __getitem__(self, cell):
        if cell not in self:
            return None
        q, r = cell.astuple()
        q -= self.offset(r)
        return self._data[r][q]

    def __setitem__(self, cell, data):
        q, r = cell.astuple()
        q -= self.offset(r)
        if Hex(q, r) in self:
            self._data[r][q] = data

    def enumerate(self):
        items = []
        for r, line in enumerate(self._data):
            for q, val in enumerate(line):
                q += self.offset(r)
                item = (Hex(q, r), val)
                items.append(item)
        return items
