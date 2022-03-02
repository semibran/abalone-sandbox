# WIP - need to figure out how to either:
#   (1) efficiently update sumito hashes
#   (2) make updated hashes line up with generated ones

from random import getrandbits
from core.board import Board
from core.board_cell_state import BoardCellState


def setup_cell_indices():
    cell_indices = {}
    temp_board = Board()
    for i, (cell, _) in enumerate(temp_board.enumerate()):
        cell_indices[cell] = i
    return cell_indices

CELL_INDICES = setup_cell_indices()


def setup_zobrist(bits):
    zobrist_table = {}
    for i in range(2):
        piece_index = i + 1
        for _, cell_index in CELL_INDICES.items():
            zobrist_table[cell_index * piece_index] = getrandbits(bits)
    return zobrist_table

ZOBRIST_BITS = 64
ZOBRIST = setup_zobrist(bits=ZOBRIST_BITS)


def get_piece_mask(cell, cell_state):
    return ZOBRIST[hash_piece(cell, cell_state)]

def hash_piece(cell, cell_state):
    return CELL_INDICES[cell] * cell_state.value

def hash_board(board):
    hash = 0
    for cell, cell_state in board.enumerate():
        if cell_state != BoardCellState.EMPTY:
            hash ^= get_piece_mask(cell, cell_state)
    return hash

def update_hash(hash, board, move):
    move_tail = move.tail()
    hash ^= get_piece_mask(move_tail, board[move_tail])

    move_target = move.target_cell()
    hash ^= get_piece_mask(move_target, board[move_tail])

    return hash
