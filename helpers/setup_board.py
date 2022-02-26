from json import loads
from core.board import Board
from core.board_cell_state import BoardCellState
from core.hex import Hex

def resolve_board_layout(board_layout):
    file_name = board_layout.value
    with open(file_name, mode="r") as file:
        file_buffer = file.read()
    return loads(file_buffer)

def apply_board_data(board, board_data):
    for r, line in enumerate(board_data):
        for q, val in enumerate(line):
            board.set(Hex(q, r), BoardCellState(val))
    return board

def setup_board(board_layout):
    board_data = resolve_board_layout(board_layout)
    return apply_board_data(Board(), board_data)
