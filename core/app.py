from time import time, sleep
from core.app_config import AppConfig, ControlMode
from core.board_cell_state import BoardCellState
from core.game import Game, Player, is_move_target_empty, count_marbles_in_line
from core.move import Move
from display import Display
from core.hex import Hex, HexDirection
from core.agent import Agent
from config import APP_NAME, FPS

CPU_DELAY = 1

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
        self._done = False

    @property
    def game_board(self):
        return self.game.board

    @property
    def game_turn(self):
        return self.game.turn

    @property
    def game_over(self):
        return self.game.over

    def _new_game(self):
        self.game = Game(layout=self._config.starting_layout)

    def _select_cell(self, cell):
        if self.game_over:
            self._new_game()

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
                num_attackers = len(self.selection.pieces())
                num_defenders = count_marbles_in_line(self.game_board, cell, self.selection.direction)
                if num_attackers > num_defenders:
                    self._apply_selection()
            self.selection = None

        else:
            self.selection = None

        self._display.render(self)

    def _apply_selection(self):
        self._perform_move(self.selection)
        self.selection = None

    def _perform_move(self, move):
        self._display.perform_move(move, self.game_board)
        self.game.perform_move(move)

    def update(self):
        if self._display.anims:
            return

        if self._config.control_modes[self.game.turn.value] == ControlMode.CPU:
            cpu_move = Agent.request_move(
                board=self.game_board,
                player_unit=self.PLAYER_MARBLES[self.game.turn]
            )
            if cpu_move:
                self._perform_move(cpu_move)

    def start(self):
        self._new_game()
        self._display.open(on_click=lambda cell: self._select_cell(cell))
        self._display.render(self)

        start_time = None
        while not self._done:
            start_time and print(f"FPS: {1 / (time() - start_time):.2f}")
            start_time = time()
            self.update()
            self._display.update()
            if self._display.anims:
                self._display.render(self)
            sleep(1 / FPS)
