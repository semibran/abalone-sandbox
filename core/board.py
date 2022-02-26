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

    def width(self, r):
        return (len(self._data[r])
            if r >= 0 and r < len(self._data)
            else None)

    @property
    def height(self):
        return len(self._data)

    def __contains__(self, cell):
        q, r = cell
        return (r >= 0 and r < self.height
            and q >= 0 and q < self.width(r))

    def get(self, cell):
        if cell not in self:
            return None
        q, r = cell
        return self._data[r][q]

    def set(self, cell, data):
        if cell in self:
            q, r = cell
            self._data[r][q] = data

    def enumerate(self):
        items = []
        for r, line in enumerate(self._data):
            for q, val in enumerate(line):
                items.append(((q, r), val))
        return items
