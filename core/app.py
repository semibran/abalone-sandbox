from helpers.point_to_hex import point_to_hex
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
    unit = board.get(move.head())

    for cell in move.pieces():
        board.set(cell, BoardCellState.EMPTY)

    for cell in move.targets():
        board.set(cell, unit)

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

        if not self.selection and self.game_board.get(cell) != BoardCellState.EMPTY:
            self.selection = Move(cell)

        elif self.selection and self.game_board.get(cell) == BoardCellState.EMPTY:
            if Hex.adjacent(cell, self.selection.head()):
                self.selection.direction = Hex.subtract(cell, self.selection.head())
                apply_move(self.game_board, self.selection)
            self.selection = None

        elif self.selection and self.selection.end is None:
            self.selection.end = cell
            if not self.selection.pieces():
                self.selection = None

        self._display.render(self)

    def start(self):
        self._new_game()
        self._display.open(self, {
            "select_cell": lambda cell: self._select_cell(cell)
        })
