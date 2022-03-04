from enum import Enum

class BoardCellState(Enum):
    EMPTY = 0
    BLACK = 1
    WHITE = 2

    def next(cell_state):
        return (BoardCellState.BLACK
            if cell_state == BoardCellState.WHITE
            else BoardCellState.WHITE)
