from math import inf
from enum import Enum
from core.board_cell_state import BoardCellState
from core.hex import Hex
from helpers.setup_board import setup_board

def apply_move(board, move):
    num_ejected = 0
    unit = board[move.head()]

    for cell in move.pieces():
        board[cell] = BoardCellState.EMPTY

    # attempt sumito
    move_targets = move.targets()
    defender_cell = move_targets[-1]
    defender_unit = board[defender_cell]
    if defender_unit not in (BoardCellState.EMPTY, unit):
        num_defenders = count_marbles_in_line(board, defender_cell, move.direction)
        for _ in range(num_defenders):
            defender_cell = Hex.add(defender_cell, move.direction.value)
            if defender_cell not in board:
                num_ejected += 1
                break
            board[defender_cell] = defender_unit

    for cell in move_targets:
        board[cell] = unit

    return num_ejected

def is_move_legal(board, move):
    if is_move_target_empty(board, move):
        return True

    target_cell = move.targets()[-1]
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
    count = 0
    unit = board[cell]
    if unit == BoardCellState.EMPTY:
        return count

    while board[cell] == unit:
        count += 1
        cell = Hex.add(cell, direction.value)

    if board[cell] not in (None, BoardCellState.EMPTY):
        return inf

    return count

def find_board_score(board, player_unit):
    score = 0
    for _, cell_state in board.enumerate():
        if cell_state == player_unit:
            score += 1
        elif cell_state != BoardCellState.EMPTY:
            score -= 1
    return score

class Player(Enum):
    ONE = 0
    TWO = 1

    def next(player):
        return Player((player.value + 1) % len(Player))

class Game:
    def __init__(self, layout):
        self.board = setup_board(layout)
        self.turn = Player.ONE

    def perform_move(self, move):
        apply_move(self.board, move)
        self.turn = Player.next(self.turn)
