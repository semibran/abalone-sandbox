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
        board_cell = offset_true_hex(self.game_board, cell)
        if not self.selection and self.game_board.get(board_cell) != BoardCellState.EMPTY:
            self.selection = Move(board_cell)
        elif self.selection and self.selection.end is None:
            if self.game_board.get(board_cell) == BoardCellState.EMPTY:
                self.selection = None
            else:
                self.selection.end = board_cell
                if not self.selection.pieces():
                    self.selection = None
        elif self.selection and self.selection.end:
            self.selection = None

        self._display.render(self)

    def start(self):
        self._new_game()
        self._display.open(self, {
            "select_cell": lambda cell: self._select_cell(cell)
        })
