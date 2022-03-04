import sys
from os.path import splitext
from copy import deepcopy
from core.board_cell_state import BoardCellState
from core.board import Board
from core.hex import Hex
from core.agent import Agent
from core.game import apply_move

MAP_COLOR = {
  "b": BoardCellState.BLACK,
  "w": BoardCellState.WHITE,
}

def convert_cell_to_hex(cell):
    col = int(cell[1]) - 1
    row = 9 - (ord(cell[0]) - 65) - 1
    return Hex(col, row)

def read_buffer(file_name):
    file_buffer = None
    with open(file_name, mode="r") as file:
        file_buffer = file.read()
    return file_buffer

def write_boards(file_name, boards):
    file_buffer = "\n".join([str(board) for board in boards])
    with open(file_name, mode="w", encoding="utf-8") as file:
        file.write(file_buffer)

def main():
    file_name = sys.argv[1]
    file_buffer = read_buffer(file_name)

    turn_line, pieces_line, _ = file_buffer.split("\n")
    turn = MAP_COLOR[turn_line]

    pieces = []
    piece_strs = pieces_line.split(",")
    for piece_str in piece_strs:
        piece_cell = convert_cell_to_hex(piece_str[0:2])
        piece_color = MAP_COLOR[piece_str[-1]]
        pieces.append((piece_cell, piece_color))

    board = Board()
    board.fill(BoardCellState.EMPTY)
    for piece_cell, piece_color in pieces:
        board[piece_cell] = piece_color

    moves = Agent()._enumerate_player_moves(board, turn)
    print(len(moves), moves)

    boards = [apply_move(deepcopy(board), move) for move in moves]
    write_boards(f"{splitext(file_name)[0]}.board", boards)

if __name__ == "__main__":
    main()
