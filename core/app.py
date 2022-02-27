from core.app_config import AppConfig, ControlMode
from core.board_cell_state import BoardCellState
from core.game import Game, Player, is_move_target_empty, count_marbles_in_line
from core.move import Move
from core.display import Display
from core.hex import Hex, HexDirection
from core.agent import Agent
from config import APP_NAME

def offset_true_hex(board, cell):
    q, r = cell.astuple()
    q += board.height // 2
    return Hex(q, r)

class App:

    PLAYER_MARBLES = {
        Player.ONE: BoardCellState.WHITE,
        Player.TWO: BoardCellState.BLACK
    }

    def __init__(self):
        self.game = None
        self.selection = None
        self._config = AppConfig()
        self._display = Display(title=APP_NAME)
        self._cpu_countdown = 0

    @property
    def game_board(self):
        return self.game.board

    def _new_game(self):
        self.game = Game(layout=self._config.starting_layout)

    def _select_cell(self, cell):
        cell = offset_true_hex(self.game_board, cell)

        if (not self.selection
        and self.game_board[cell] == App.PLAYER_MARBLES[self.game.turn]
        and self._config.control_modes[self.game.turn.value] != ControlMode.CPU):
            self.selection = Move(cell)

        elif self.selection and self.game_board[cell] == BoardCellState.EMPTY:
            if Hex.adjacent(cell, self.selection.head()):
                normal = Hex.subtract(cell, self.selection.head())
                self.selection.direction = HexDirection.resolve(normal)
                if is_move_target_empty(self.game_board, self.selection):
                    self._apply_selection()
            self.selection = None

        elif (self.selection and self.selection.end is None
        and self.game_board[cell] == self.game_board[self.selection.head()]):
            self.selection.end = cell
            selection_pieces = self.selection.pieces()
            if (not selection_pieces
            or next((c for c in selection_pieces if self.game_board[c] != self.game_board[self.selection.head()]), None)):
                self.selection = None

        elif (self.selection and self.selection.end
        and self.game_board[cell] == self.game_board[self.selection.head()]):
            self.selection.start = self.selection.end
            self.selection.end = cell
            selection_pieces = self.selection.pieces()
            if (not selection_pieces
            or next((c for c in selection_pieces if self.game_board[c] != self.game_board[self.selection.head()]), None)):
                self.selection = None

        elif (self.selection and self.selection.end
        and Hex.adjacent(cell, self.selection.head())
        and self.game_board[cell] != self.game_board[self.selection.head()]):
            normal = Hex.subtract(cell, self.selection.head())
            self.selection.direction = HexDirection.resolve(normal)
            if self.selection.is_inline():
                attackers = len(self.selection.pieces())
                defenders = count_marbles_in_line(self.game_board, cell, self.selection.direction)
                if attackers > defenders:
                    self._apply_selection()
            self.selection = None

        else:
            self.selection = None

    def _apply_selection(self):
        self.game.perform_move(self.selection)
        self.selection = None
        self._cpu_countdown = 15

    def update(self):
        if self._cpu_countdown:
            self._cpu_countdown -= 1
        elif self.game.turn == Player.TWO:
            cpu_move = Agent.request_move(
                board=self.game_board,
                player_unit=self.PLAYER_MARBLES[self.game.turn]
            )
            if cpu_move:
                self.game.perform_move(cpu_move)

    def start(self):
        self._new_game()
        self._display.open(self, {
            "select_cell": lambda cell: self._select_cell(cell)
        })
