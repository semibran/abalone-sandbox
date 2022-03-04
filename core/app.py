from time import time, sleep
from threading import Thread, active_count
from queue import Queue, Empty
from core.app_config import AppConfig, ControlMode
from core.board_cell_state import BoardCellState
from core.game import Game, Player, is_move_target_empty, count_marbles_in_line
from core.move import Move
from display import Display
from core.hex import Hex, HexDirection
from core.agent import Agent
from config import (
    APP_NAME, FPS, ENABLED_FPS_DISPLAY,
    AGENT_MAX_SEARCH_SECS, AGENT_SEC_THRESHOLD,
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
        self.selection = None
        self._start_time = time()
        self._config = AppConfig()
        self._display = Display(title=APP_NAME)
        self._agent = Agent()
        self._agent_queue = Queue()
        self._agent_thread = None
        self._agent_time = time()
        self._agent_move = None
        self._agent_done = False

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

    def _setup_agent_thread(self):
        if self._agent_thread:
            self._agent_thread = None

        best_move_gen = self._agent.gen_best_move(
            board=self.game_board,
            player_unit=self.PLAYER_MARBLES[self.game_turn]
        )

        def worker():
            best_move = None
            done_search = False
            while not done_search:
                try:
                    best_move = next(best_move_gen)
                except StopIteration:
                    done_search = True

                if best_move or done_search:
                    print("yield", best_move, done_search)
                    self._agent_queue.put((best_move, done_search))

        thread = Thread(target=worker)
        thread.daemon = True
        thread.start()

        self._agent_thread = thread
        self._agent_time = time()
        self._agent_move = None
        self._agent_done = False

        while self._agent_queue.qsize():
            self._agent_queue.get()
            self._agent_queue.task_done()

        return thread

    def _new_game(self):
        self.selection = None
        self.game = Game(layout=self._config.starting_layout)
        self._display.clear_board()
        self._display.render(self)
        self._start_time = time()

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
                and self._setup_agent_thread()
        ))
        self.game.perform_move(move)

    def update(self):
        if self._display.is_settings_open:
            return

        if not self.game_over and not self._agent_done:
            self._display.update_timer(start_time=self._agent_time)

        if self._agent_done:
            best_move = self._agent_move
            is_search_complete = self._agent_done
        else:
            try:
                best_move, is_search_complete = self._agent_queue.get_nowait()
                self._agent_queue.task_done()
            except Empty:
                best_move, is_search_complete = None, False

            if time() - self._agent_time >= AGENT_MAX_SEARCH_SECS + AGENT_SEC_THRESHOLD:
                if self._agent_move:
                    is_search_complete = True
                    self._agent.interrupt = True

            self._agent_move = best_move or self._agent_move
            self._agent_done = is_search_complete

        if self._display.is_animating:
            return

        if best_move and is_search_complete and self._config.control_modes[self.game_turn.value] == ControlMode.CPU:
            self._agent_move = None
            self._perform_move(best_move)

    def start(self):
        self._display.open(
            on_click=lambda cell: self._select_cell(cell),
            on_reset=lambda: (
                (not self.game.ply or self._display.confirm_reset())
                    and self._new_game()
            ),
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
            self.update()
            self._display.update()
            if self._display.is_animating:
                self._display.render(self)
            sleep(1 / FPS)

        # self._agent_queue.join() # TODO: why does this block closing the app?
