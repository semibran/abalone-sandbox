from tkinter import Tk
from core.app_config import AppConfig
from core.board_cell_state import BoardCellState
from core.game import Game
from core.move import Move
from core.display import Display
from config import APP_NAME

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
        if not self.selection and self.game_board.get(cell) != BoardCellState.EMPTY:
            self.selection = Move(cell)
        elif self.selection and self.selection.end is None and self.game_board.get(cell) != BoardCellState.EMPTY:
            self.selection.end = cell
        elif self.selection and self.selection.end:
            self.selection = None

        self._display.render(self)

    def start(self):
        self._new_game()
        self._display.open(self, {
            "select_cell": lambda cell: self._select_cell(cell)
        })
