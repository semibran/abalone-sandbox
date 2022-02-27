from copy import deepcopy
from math import pow
from core.hex import Hex, HexDirection
from core.move import Move
from core.game import apply_move, is_move_legal, find_board_score

class Agent:

    @classmethod
    def request_move(cls, board, player_unit):
        player_moves = cls._enumerate_player_moves(board, player_unit)
        if not player_moves:
            return None

        return sorted(player_moves, key=lambda move: (
            temp_board := deepcopy(board),
            apply_move(temp_board, move),
            cls._heuristic(temp_board, player_unit)
        )[-1])[-1]

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

    @classmethod
    def _heuristic(cls, board, player_unit):
        return (cls._heuristic_centralization(board, player_unit)
            + 10 * cls._heuristic_score(board, player_unit))

    @classmethod
    def _heuristic_centralization(cls, board, player_unit):
        score = 0
        for cell, cell_state in board.enumerate():
            if cell_state != player_unit:
                continue
            board_center = Hex(board.height // 2, board.height // 2)
            score += pow(board.height // 2 - Hex.manhattan(cell, board_center), 2)
        return score

    @classmethod
    def _heuristic_score(cls, board, player_unit):
        return find_board_score(board, player_unit)
