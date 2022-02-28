from math import inf
from enum import Enum
from core.board_cell_state import BoardCellState
from core.board_layout import BoardLayout
from core.hex import Hex
from config import NUM_EJECTED_MARBLES_TO_WIN

def apply_move(board, move):
    num_ejected = 0
    unit = board[move.head()]

    for cell in move.pieces():
        board[cell] = BoardCellState.EMPTY

    # attempt sumito
    defender_cell = move.target_cell()
    defender_unit = board[defender_cell]
    if defender_unit not in (BoardCellState.EMPTY, unit):
        num_defenders = count_marbles_in_line(board, defender_cell, move.direction)
        for _ in range(num_defenders):
            defender_cell = Hex.add(defender_cell, move.direction.value)
            if defender_cell not in board:
                num_ejected += 1
                break
            board[defender_cell] = defender_unit

    move_targets = move.targets()
    for cell in move_targets:
        board[cell] = unit

    return num_ejected

def is_move_legal(board, move):
    if is_move_target_empty(board, move):
        return True

    target_cell = move.target_cell()
    if (target_cell not in board
    or board[move.head()] == board[target_cell]
    or board[move.head()] == BoardCellState.EMPTY):
        return False

    num_attackers = len(move.pieces())
    num_defenders = count_marbles_in_line(board, target_cell, move.direction)
    return move.is_inline() and num_attackers > num_defenders

def is_move_target_empty(board, move):
    move_pieces = move.pieces()
    return next((False for t in move.targets() if (
        t not in move_pieces
        and board[t] != BoardCellState.EMPTY
    )), True)

def count_marbles_in_line(board, cell, direction):
    marbles = find_marbles_in_line(board, cell, direction)
    unit = board[cell]
    if next((m for m in marbles if board[m] != unit), None):
        return inf
    return len(marbles)

def find_marbles_in_line(board, cell, direction):
    marbles = []
    unit = board[cell]
    if unit == BoardCellState.EMPTY:
        return marbles

    while board[cell] not in (None, BoardCellState.EMPTY):
        marbles.append(cell)
        cell = Hex.add(cell, direction.value)

    return marbles

def find_board_score(board, player_unit):
    enemy_unit = BoardCellState.next(player_unit)
    max_enemy_marbles = BoardLayout.num_units(board.layout, enemy_unit)
    num_enemy_marbles = 0
    for _, cell_state in board.enumerate():
        if cell_state == enemy_unit:
            num_enemy_marbles += 1
    return max_enemy_marbles - num_enemy_marbles

class Player(Enum):
    ONE = 0
    TWO = 1

    def next(player):
        return Player((player.value + 1) % len(Player))

class Game:
    def __init__(self, layout):
        self.board = BoardLayout.setup_board(layout)
        self.turn = Player.ONE
        self._over = False

    @property
    def over(self):
        return self._over

    def perform_move(self, move):
        if self._over:
            return False

        player_unit = self.board[move.head()]
        apply_move(self.board, move)
        score = find_board_score(self.board, player_unit)
        if score >= NUM_EJECTED_MARBLES_TO_WIN:
            self._over = True

        self.turn = Player.next(self.turn)
        return True
