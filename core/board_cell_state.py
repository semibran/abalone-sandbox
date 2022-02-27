from enum import Enum

class BoardCellState(Enum):
    EMPTY = 0
    WHITE = 1
    BLACK = 2

    def next(cell_state):
        return (BoardCellState.BLACK
            if cell_state == BoardCellState.WHITE
            else BoardCellState.WHITE)
