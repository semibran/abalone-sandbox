from time import time
from math import pow, inf
from copy import deepcopy
from dataclasses import dataclass, field
from core.hex import Hex, HexDirection
from core.move import Move
from core.board_cell_state import BoardCellState
from core.game import apply_move, is_move_legal, find_board_score

@dataclass
class StateSpaceNode:
    move: Move
    score: float = None
    children: list = field(default_factory=list)

class Agent:

    @classmethod
    def request_move(cls, board, player_unit):
        start_time = time()
        player_moves = cls._enumerate_player_moves(board, player_unit)
        if not player_moves:
            return None

        num_adjacent_enemies = False
        for cell, cell_state in board.enumerate():
            if cell_state != player_unit:
                continue
            if next((n for n in Hex.neighbors(cell) if board[n] == BoardCellState.next(player_unit)), False):
                num_adjacent_enemies += 1

        if num_adjacent_enemies >= 3:
            state_space = cls._enumerate_state_space(board, player_unit, depth=2)
            for max_node in state_space:
                max_node.score = min([n.score for n in max_node.children])
        else:
            state_space = cls._enumerate_state_space(board, player_unit, depth=1)

        best_node = None
        for max_node in state_space:
            if best_node is None or max_node.score > best_node.score:
                best_node = max_node

        best_move = best_node.move
        cls._print_move_deconstruction(board, player_unit, best_move, time=(time() - start_time))
        return best_move

    @classmethod
    def _print_move_deconstruction(cls, board, player_unit, move, time):
        temp_board = deepcopy(board)
        apply_move(temp_board, move)
        print(
            "-- Heuristic overview"
            f"\nFound {move} in {time:.4f}s"
            f"\n- heuristic_score: {cls._heuristic_score(board, player_unit)}"
            f"\n- heuristic_centralization: {cls._heuristic_centralization(board, player_unit)}"
            f"\n- heuristic_adjacency: {cls._heuristic_adjacency(board, player_unit)}"
            "\n"
        )

    @classmethod
    def _enumerate_state_space(cls, board, player_unit, depth=inf, inverse=False):
        state_space = []
        moves = cls._enumerate_player_moves(board, player_unit)
        for move in moves:
            temp_board = deepcopy(board)
            apply_move(temp_board, move)
            if depth > 1:
                state_space.append(StateSpaceNode(
                    move,
                    children=cls._enumerate_state_space(
                        board=temp_board,
                        player_unit=BoardCellState.next(player_unit),
                        depth=depth - 1,
                        inverse=not inverse,
                    )
                ))
            else:
                state_space.append(StateSpaceNode(
                    move,
                    score=(cls._heuristic(temp_board, player_unit) - cls._heuristic(temp_board, BoardCellState.next(player_unit))) * (-1 if inverse else 1)
                ))
        return state_space

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
            start, end = shape[0], shape[-1]
            shape = {start, end}
            if shape in known_selection_shapes:
                continue
            known_selection_shapes.append(shape)
            for direction in HexDirection:
                move = (Move(start, end, direction)
                    if start != end
                    else Move(start, direction=direction))
                if is_move_legal(board, move):
                    cell_moves.append(move)
        return cell_moves

    @classmethod
    def _find_selection_shapes(cls, board, origin):
        selection_shapes = [[origin]]
        for direction in HexDirection:
            cell = origin
            shape = [cell]
            while len(shape) < 3:
                cell = Hex.add(cell, direction.value)
                if board[cell] != board[origin]:
                    break
                shape.append(cell)
                if len(shape) > 1:
                    selection_shapes.append(shape.copy())

        return selection_shapes

    @classmethod
    def _heuristic(cls, board, player_unit):
        return (100 * cls._heuristic_score(board, player_unit)
            + cls._heuristic_centralization(board, player_unit)
            + 0.1 * cls._heuristic_adjacency(board, player_unit))

    @classmethod
    def _heuristic_score(cls, board, player_unit):
        return find_board_score(board, player_unit)

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
    def _heuristic_adjacency(cls, board, player_unit):
        score = 0
        for cell, cell_state in board.enumerate():
            if cell_state != player_unit:
                continue
            num_allies = sum([board[n] == cell_state for n in Hex.neighbors(cell)])
            score += pow(num_allies, 2)
        return score
