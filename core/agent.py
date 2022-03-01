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
    num_subtrees_pruned = 0
    num_requests = 0

    @classmethod
    def request_move(cls, board, player_unit):
        start_time = time()
        player_moves = cls._enumerate_player_moves(board, player_unit)
        if not player_moves:
            return None

        if cls._should_use_lookaheads(board, player_unit):
            state_space, _, num_prunes = cls._enumerate_state_space(board, player_unit, depth=2)
        else:
            state_space, _, num_prunes = cls._enumerate_state_space(board, player_unit, depth=1)

        best_node = None
        for max_node in state_space:
            if best_node is None or max_node.score > best_node.score:
                best_node = max_node

        if best_node:
            best_move = best_node.move
            temp_board = deepcopy(board)
            apply_move(temp_board, best_move)

            cls.num_subtrees_pruned += num_prunes
            cls.num_requests += 1

            cls._print_move_deconstruction(
                move=best_move,
                time=(time() - start_time),
                num_subtrees_pruned=num_prunes,
                avg_subtrees_pruned=f"{cls.num_subtrees_pruned / cls.num_requests:.2f}",
                heuristic_score=cls._heuristic_score(temp_board, player_unit),
                heuristic_centralization=cls._heuristic_centralization(temp_board, player_unit),
                heuristic_adjacency=cls._heuristic_adjacency(temp_board, player_unit),
                final_score=f"{best_node.score:.2f}",
            )
            return best_move

    @classmethod
    def _print_move_deconstruction(cls, move, time, **kwargs):
        print("\n".join((
            "-- Heuristic overview",
            f"Found {move} in {time:.4f}s",
            *[f"- {key}: {value}" for key, value in kwargs.items()],
            "",
        )))

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
            return [], max_score - min_score, 0

        num_prunes = 0
        moves = cls._enumerate_player_moves(
            board,
            player_unit=(player_unit
                if is_player
                else BoardCellState.next(player_unit))
        )
        moves.sort(key=lambda move: cls._estimate_move_score(board, move), reverse=True) # 53.35

        if is_player:
            value = -inf
            state_space = []
            for move in moves:
                temp_board = deepcopy(board)
                apply_move(temp_board, move)

                # children -> all non-pruned moves min can make from this state
                # value -> best move value for min
                move_children, move_value, move_prunes = cls._enumerate_state_space(
                    board=temp_board,
                    player_unit=player_unit,
                    depth=depth - 1,
                    alpha=alpha,
                    beta=beta,
                    is_player=False,
                )

                # use this move if better for max
                value = max(value, move_value)
                num_prunes += move_prunes

                # beta prune - this subtree has a move that is worse for min than the best move found for min (min will never go down this subtree!)
                if value >= beta:
                    num_prunes += 1
                    break

                # use as new best move for max
                alpha = max(alpha, value)

                # add this move to the state space with its heuristic value
                state_space.append(StateSpaceNode(move, score=move_value, children=move_children))

            return state_space, value, num_prunes

        else: # find best move for min
            value = inf
            state_space = []
            for move in moves:
                temp_board = deepcopy(board)
                apply_move(temp_board, move)

                # children -> all non-pruned moves max can make from this state
                # value -> value of best move for max
                move_children, move_value, move_prunes = cls._enumerate_state_space(
                    board=temp_board,
                    player_unit=player_unit,
                    depth=depth - 1,
                    alpha=alpha,
                    beta=beta,
                    is_player=True,
                )

                # use this move if better for min
                value = min(value, move_value)
                num_prunes += move_prunes

                # alpha prune - this subtree has a move that is worse for max than the best move found for max (min will always take it!)
                if value <= alpha:
                    num_prunes += 1
                    break

                # use as new best move for min (if max goes down this subtree)
                beta = min(beta, value)

                # add this move to the state space with its heuristic value
                state_space.append(StateSpaceNode(move, score=move_value, children=move_children))

            return state_space, value, num_prunes

    @classmethod
    def _estimate_move_score(cls, board, move):
        WEIGHT_SUMITO = 10 # consider sumitos first
        return (len(move.pieces())
            + WEIGHT_SUMITO * (board[move.target_cell()] != BoardCellState.EMPTY))

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
            board_radius = board.height // 2
            board_center = Hex(board_radius, board_radius)
            score += (board_radius - Hex.manhattan(cell, board_center) - 1) * 2
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
