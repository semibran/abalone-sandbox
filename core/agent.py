from random import choice
from core.hex import Hex, HexDirection
from core.move import Move
from core.game import is_move_legal

class Agent:

    @classmethod
    def request_move(cls, board, player_unit):
        player_moves = cls._enumerate_player_moves(board, player_unit)
        return choice(player_moves)

    @classmethod
    def _enumerate_player_moves(cls, board, player_unit):
        player_moves = []
        known_selection_shapes = []
        for cell, cell_state in board.enumerate():
            if cell_state is not player_unit:
                continue
            cell_moves = cls._enumerate_cell_moves(board, cell, known_selection_shapes)
            player_moves += cell_moves
        return player_moves

    @classmethod
    def _enumerate_cell_moves(cls, board, cell, known_selection_shapes):
        cell_moves = []
        selection_shapes = cls._find_selection_shapes(board, cell)
        for shape in selection_shapes:
            if shape in known_selection_shapes:
                continue
            known_selection_shapes.append(shape)
            shape = list(shape)
            start, end = shape[0], shape[-1]
            for direction in HexDirection:
                move = Move(start, end, direction)
                if is_move_legal(board, move):
                    cell_moves.append(move)
        return cell_moves

    @classmethod
    def _find_selection_shapes(cls, board, origin):
        selection_shapes = [{origin}]
        for direction in HexDirection:
            cell = origin
            shape = set()
            while len(shape) < 3 and board[cell] == board[origin]:
                shape.add(cell)
                if len(shape) > 1:
                    selection_shapes.append(shape.copy())
                cell = Hex.add(cell, direction.value)

        return selection_shapes
