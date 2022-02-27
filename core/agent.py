from random import random
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

        if cls._should_use_lookaheads(board, player_unit):
            state_space, _ = cls._enumerate_state_space(board, player_unit, depth=2)
        else:
            state_space, _ = cls._enumerate_state_space(board, player_unit, depth=1)

        best_node = None
        for max_node in state_space:
            if best_node is None or max_node.score > best_node.score:
                best_node = max_node

        if best_node:
            best_move = best_node.move
            cls._print_move_deconstruction(board, player_unit, best_move, best_node.score, time=(time() - start_time))
            return best_move

    @classmethod
    def _print_move_deconstruction(cls, board, player_unit, move, score, time):
        temp_board = deepcopy(board)
        apply_move(temp_board, move)
        print(
            "-- Heuristic overview"
            f"\nFound {move} in {time:.4f}s"
            f"\n- heuristic_score: {cls._heuristic_score(board, player_unit)}"
            f"\n- heuristic_centralization: {cls._heuristic_centralization(board, player_unit)}"
            f"\n- heuristic_adjacency: {cls._heuristic_adjacency(board, player_unit)}"
            f"\n- final heuristic value: {score:.3f}"
            "\n"
        )

    @classmethod
    def _should_use_lookaheads(cls, board, player_unit):
        num_adjacent_enemies = 0
        for cell, cell_state in board.enumerate():
            if cell_state != player_unit:
                continue
            if next((n for n in Hex.neighbors(cell) if board[n] == BoardCellState.next(player_unit)), False):
                num_adjacent_enemies += 1
        return num_adjacent_enemies >= 2

    @classmethod
    def _enumerate_state_space(cls, board, player_unit, depth=inf, alpha=-inf, beta=inf, is_player=True):
        if depth <= 0:
            max_score = cls._heuristic(board, player_unit)
            min_score = cls._heuristic(board, BoardCellState.next(player_unit))
            return [], max_score - min_score

        moves = cls._enumerate_player_moves(
            board,
            player_unit=(player_unit
                if is_player
                else BoardCellState.next(player_unit))
        )

        if is_player:
            value = -inf
            state_space = []
            for move in moves:
                temp_board = deepcopy(board)
                apply_move(temp_board, move)

                # children -> all non-pruned moves min can make from this state
                # value -> best move value for min
                move_children, move_value = cls._enumerate_state_space(
                    board=temp_board,
                    player_unit=player_unit,
                    depth=depth - 1,
                    alpha=alpha,
                    beta=beta,
                    is_player=False,
                )

                # use this move if better for max
                value = max(value, move_value)

                # beta prune - this subtree has a move that is worse for min than the best move found for min (min will never go down this subtree!)
                if value >= beta:
                    break

                # use as new best move for max
                alpha = max(alpha, value)

                # add this move to the state space with its heuristic value
                state_space.append(StateSpaceNode(move, score=move_value, children=move_children))

            return state_space, value

        else: # find best move for min
            value = inf
            state_space = []
            for move in moves:
                temp_board = deepcopy(board)
                apply_move(temp_board, move)

                # children -> all non-pruned moves max can make from this state
                # value -> value of best move for max
                move_children, move_value = cls._enumerate_state_space(
                    board=temp_board,
                    player_unit=player_unit,
                    depth=depth - 1,
                    alpha=alpha,
                    beta=beta,
                    is_player=True,
                )

                # use this move if better for min
                value = min(value, move_value)

                # alpha prune - this subtree has a move that is worse for max than the best move found for max (min will always take it!)
                if value <= alpha:
                    break

                # use as new best move for min (if max goes down this subtree)
                beta = min(beta, value)

                # add this move to the state space with its heuristic value
                state_space.append(StateSpaceNode(move, score=move_value, children=move_children))

            return state_space, value

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
