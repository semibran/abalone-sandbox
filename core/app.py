from time import time, sleep
from core.agent.operator import AgentOperator as Agent
from core.app_config import AppConfig, ControlMode
from core.board_cell_state import BoardCellState
from core.game import Game, Player, is_move_target_empty, count_marbles_in_line
from core.game_history import GameHistory, GameHistoryItem
from core.move import Move
from display import Display
from core.hex import Hex, HexDirection
from config import (
    APP_NAME, FPS, ENABLED_FPS_DISPLAY,
)

CPU_DELAY = 1

def offset_true_hex(board, cell):
    q, r = cell.astuple()
    q += board.height // 2
    return Hex(q, r)

class App:

    PLAYER_MARBLES = {
        Player.ONE: BoardCellState.BLACK,
        Player.TWO: BoardCellState.WHITE
    }

    def __init__(self):
        self.game = None
        self._game_history = GameHistory()
        self.selection = None
        self._start_time = time()
        self._config = AppConfig()
        self._display = Display(title=APP_NAME)
        self._agent = Agent()

    @property
    def game_board(self):
        return self.game.board

    @property
    def game_turn(self):
        return self.game.turn

    @property
    def game_over(self):
        return self.game.over

    @property
    def game_winner(self):
        return self.game.winner

    @property
    def theme(self):
        return self._config.theme

    def _start_agent_search(self):
        self._agent.start_search(
            board=self.game_board,
            color=self.PLAYER_MARBLES[self.game_turn]
        )

    def _stop_agent_search(self):
        self._agent.stop_search()

    def _new_game(self):
        self.selection = None
        self.game = Game(layout=self._config.starting_layout)
        self._display.clear_board()
        self._display.render(self)
        self._start_time = time()

    def _undo_move(self):
        if not self._game_history:
            print("game history is empty")
            return

        game = Game(layout=self._config.starting_layout)
        self._game_history.pop()
        for action in self._game_history:
            game.perform_move(action.move)
            print(action.move)
        self.game = game
        self._display.clear_board()
        self._display.render(self)
        if self._config.control_modes[self.game_turn.value] == ControlMode.CPU:
            self._start_agent_search()

        self._stop_agent_search()

    def _select_cell(self, cell):
        if self.game_over:
            self._new_game()
            return

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
        if self.game_over:
            return

        self._display.perform_move(move, self.game_board, on_end=lambda: (
            self._display.update_hud(self),
            not self.game_over
            and self._config.control_modes[self.game_turn.value] == ControlMode.CPU
                and self._start_agent_search()
        ))
        self.game.perform_move(move)
        self._game_history.append(GameHistoryItem(move))

    def _update(self):
        if self._display.is_settings_open:
            return

        self._update_agent()

    def _update_agent(self):
        if not self.game_over and not self._agent.done:
            self._display.update_timer(start_time=self._agent.time)

        if self._display.is_animating or self._config.control_modes[self.game_turn.value] != ControlMode.CPU:
            return

        best_move = self._agent.update()
        if best_move:
            self._perform_move(best_move)

    def start(self):
        self._display.open(
            on_click=lambda cell: self._select_cell(cell),
            on_reset=lambda: (
                (not self.game.ply or self._display.confirm_reset())
                    and self._new_game()
            ),
            on_undo=self._undo_move,
            on_settings=lambda: (
                (not self.game.ply or self._display.confirm_settings())
                    and self._display.open_settings(self._config, on_close=lambda config: (
                        config != self._config and (
                            setattr(self, "_config", config),
                            self._new_game(),
                        )
                    ))
            )
        )
        self._new_game()

        start_time = None
        while not self._display.closed:
            start_time and ENABLED_FPS_DISPLAY and print(f"FPS: {1 / (time() - start_time):.2f}")
            start_time = time()
            self._update()
            self._display.update()
            if self._display.is_animating:
                self._display.render(self)
            sleep(1 / FPS)
