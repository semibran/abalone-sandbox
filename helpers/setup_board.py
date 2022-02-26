from json import loads
from core.board import Board

def resolve_board_layout(board_layout):
    file_name = board_layout.value
    with open(file_name, mode="r") as file:
        file_buffer = file.read()
    return loads(file_buffer)

def apply_board_data(board, board_data):
    for r, line in enumerate(board_data):
        for q, val in enumerate(line):
            board.set((q, r), val)
    return board

def setup_board(board_layout):
    board_data = resolve_board_layout(board_layout)
    return apply_board_data(Board(), board_data)
