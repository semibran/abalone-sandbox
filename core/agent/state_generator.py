from core.hex import Hex, HexDirection
from core.move import Move
from core.game import is_move_legal


def enumerate_player_moves(board, player_unit):
    player_moves = []
    selection_shapes = _enumerate_selection_shapes(board, player_unit)
    for selection_shape in selection_shapes:
        selection_shape = tuple(selection_shape)
        if len(selection_shape) == 1:
            start = end = selection_shape[0]
        else:
            start, end = selection_shape
        for direction in HexDirection:
            move = Move(start, end, direction)
            if is_move_legal(board, move):
                player_moves.append(move)
    return player_moves

def _enumerate_selection_shapes(board, player_unit):
    selection_shapes = []
    for cell, color in board.enumerate():
        if color is not player_unit:
            continue
        cell_selection_shapes = _enumerate_cell_selection_shapes(board, cell)
        selection_shapes += [shape for shape in cell_selection_shapes if shape not in selection_shapes]
    return selection_shapes

def _enumerate_cell_selection_shapes(board, origin):
    selection_shapes = [{origin, origin}]
    for direction in HexDirection:
        origin_color = board[origin]
        cell = origin
        shape = [cell]
        while len(shape) < 3:
            cell = Hex.add(cell, direction.value)
            if board[cell] != origin_color:
                break
            shape.append(cell)
            if len(shape) > 1:
                selection_shapes.append({shape[0], shape[-1]})

    return selection_shapes
