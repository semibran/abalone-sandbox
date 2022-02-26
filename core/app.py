from core.app_config import AppConfig
from core.board_cell_state import BoardCellState
from core.game import Game
from core.move import Move
from core.display import Display
from core.hex import Hex
from config import APP_NAME

def offset_true_hex(board, cell):
    q, r = cell.astuple()
    q += board.height // 2
    return Hex(q, r)

def apply_move(board, move):
    unit = board[move.head()]

    for cell in move.pieces():
        board[cell] = BoardCellState.EMPTY

    for cell in move.targets():
        board[cell] = unit

def is_move_target_empty(board, move):
    move_pieces = move.pieces()
    return next((False for t in move.targets() if (
        t not in move_pieces
        and board[t] != BoardCellState.EMPTY
    )), True)

def count_marbles_in_line(board, cell, direction):
    count = 0
    unit = board[cell]
    if unit == BoardCellState.EMPTY:
        return count

    while board[cell] == unit:
        count += 1
        cell = Hex.add(cell, direction)
    return count

class App:
    def __init__(self):
        self.game = None
        self.selection = None
        self._config = AppConfig()
        self._display = Display(title=APP_NAME)

    @property
    def game_board(self):
        return self.game.board

    def _new_game(self):
        self.game = Game(layout=self._config.starting_layout)

    def _select_cell(self, cell):
        cell = offset_true_hex(self.game_board, cell)

        if not self.selection and self.game_board[cell] != BoardCellState.EMPTY:
            self.selection = Move(cell)

        elif self.selection and self.game_board[cell] == BoardCellState.EMPTY:
            if Hex.adjacent(cell, self.selection.head()):
                self.selection.direction = Hex.subtract(cell, self.selection.head())
                if is_move_target_empty(self.game_board, self.selection):
                    apply_move(self.game_board, self.selection)
            self.selection = None

        elif (self.selection and self.selection.end is None
        and self.game_board[cell] == self.game_board[self.selection.head()]):
            self.selection.end = cell
            if not self.selection.pieces():
                self.selection = None

        elif (self.selection and self.selection.end
        and Hex.adjacent(cell, self.selection.head())
        and self.game_board[cell] != self.game_board[self.selection.head()]):
            self.selection.direction = Hex.subtract(cell, self.selection.head())
            if self.selection.is_inline():
                attackers = len(self.selection.pieces())
                defenders = count_marbles_in_line(self.game_board, cell, self.selection.direction)
                if attackers > defenders:
                    apply_move(self.game_board, self.selection)
            self.selection = None

        else:
            self.selection = None

        self._display.render(self)

    def start(self):
        self._new_game()
        self._display.open(self, {
            "select_cell": lambda cell: self._select_cell(cell)
        })
