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

    def __init__(self):
        self._num_requests = 0
        self._num_prunes_total = 0
        self._num_prunes_last = 0

    def gen_best_move(self, board, player_unit):
        start_time = time()
        self._num_prunes_last = 0
        self._num_requests += 1

        # search_depth = 1 + self._should_use_lookaheads(board, player_unit)
        # state_space_gen = self._enumerate_state_space(board, player_unit, depth=search_depth)

        best_move = None
        best_score = -inf
        for move in self._enumerate_player_moves(board, player_unit):
            move_board = apply_move(board=deepcopy(board), move=move)
            move_score = self._find_board_score_for_min(
                board=move_board,
                player_unit=player_unit,
                depth=1,
                alpha=best_score,
            )
            if move_score > best_score:
                best_score = move_score
                best_move = move
                yield best_move

        self._num_prunes_total += self._num_prunes_last
        if best_move is None:
            return

        best_board = apply_move(board=deepcopy(board), move=best_move)
        self._print_move_deconstruction(
            move=best_move,
            time=(time() - start_time),
            num_subtrees_pruned=self._num_prunes_last,
            avg_subtrees_pruned=f"{self._num_prunes_total / self._num_requests:.2f}",
            heuristic_score=self._heuristic_score(best_board, player_unit),
            heuristic_centralization=self._heuristic_centralization(best_board, player_unit),
            heuristic_adjacency=self._heuristic_adjacency(best_board, player_unit),
            final_score=f"{best_score:.2f}",
        )

    def _find_board_score_for_max(self, board, player_unit, depth=0, alpha=-inf, beta=inf):
        if depth == 0:
            max_score = self._heuristic(board, player_unit)
            min_score = self._heuristic(board, BoardCellState.next(player_unit))
            return max_score - min_score

        best_score = -inf
        for move in self._enumerate_player_moves(board, player_unit):
            move_board = apply_move(board=deepcopy(board), move=move)
            move_score = self._find_board_score_for_min(
                board=move_board,
                player_unit=player_unit,
                depth=depth - 1,
                alpha=alpha,
                beta=beta,
            )
            best_score = max(best_score, move_score)
            if best_score >= beta:
                break
            alpha = max(alpha, best_score)
        return best_score

    def _find_board_score_for_min(self, board, player_unit, depth=0, alpha=-inf, beta=inf):
        if depth == 0:
            max_score = self._heuristic(board, player_unit)
            min_score = self._heuristic(board, BoardCellState.next(player_unit))
            return max_score - min_score

        best_score = inf
        for move in self._enumerate_player_moves(board, player_unit):
            move_board = apply_move(board=deepcopy(board), move=move)
            move_score = self._find_board_score_for_max(
                board=move_board,
                player_unit=player_unit,
                depth=depth - 1,
                alpha=alpha,
                beta=beta,
            )
            best_score = min(best_score, move_score)
            if best_score <= alpha:
                break
            beta = min(beta, best_score)
        return best_score

    def _print_move_deconstruction(self, move, time, **kwargs):
        print("\n".join((
            "\n-- Heuristic overview",
            f"Found {move} in {time:.4f}s",
            *[f"- {key}: {value}" for key, value in kwargs.items()],
            "",
        )))

    def _should_use_lookaheads(self, board, player_unit):
        num_adjacent_enemies = 0
        for cell, cell_state in board.enumerate():
            if cell_state != player_unit:
                continue
            if next((n for n in Hex.neighbors(cell) if board[n] == BoardCellState.next(player_unit)), False):
                num_adjacent_enemies += 1
        return num_adjacent_enemies >= 2

    def _enumerate_state_space(self, board, player_unit, depth=inf, alpha=-inf, beta=inf, is_player=True):
        if depth <= 0:
            max_score = self._heuristic(board, player_unit)
            min_score = self._heuristic(board, BoardCellState.next(player_unit))
            return [], max_score - min_score

        moves = self._enumerate_player_moves(
            board,
            player_unit=(player_unit
                if is_player
                else BoardCellState.next(player_unit))
        )
        moves.sort(key=lambda move: self._estimate_move_score(board, move), reverse=True) # best avg: 53.35

        if is_player:
            value = -inf
            state_space = []
            for move in moves:
                temp_board = deepcopy(board)
                apply_move(temp_board, move)

                # children -> all non-pruned moves min can make from this state
                # value -> best move value for min
                move_children, move_value = self._enumerate_state_space(
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
                    self._num_prunes_last += 1
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
                move_children, move_value = self._enumerate_state_space(
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
                    self._num_prunes_last += 1
                    break

                # use as new best move for min (if max goes down this subtree)
                beta = min(beta, value)

                # add this move to the state space with its heuristic value
                state_space.append(StateSpaceNode(move, score=move_value, children=move_children))

            return state_space, value

    def _estimate_move_score(self, board, move):
        WEIGHT_SUMITO = 10 # consider sumitos first
        return (len(move.pieces())
            + WEIGHT_SUMITO * (board[move.target_cell()] != BoardCellState.EMPTY))

    def _enumerate_player_moves(self, board, player_unit):
        player_moves = []
        known_selection_shapes = []
        for cell, cell_state in board.enumerate():
            if cell_state is not player_unit:
                continue
            cell_moves = self._enumerate_cell_moves(board, cell, known_selection_shapes)
            player_moves += cell_moves
        return player_moves

    def _enumerate_cell_moves(self, board, cell, known_selection_shapes):
        cell_moves = []
        selection_shapes = self._find_selection_shapes(board, cell)
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

    def _find_selection_shapes(self, board, origin):
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

    def _heuristic(self, board, player_unit):
        return (100 * self._heuristic_score(board, player_unit)
            + self._heuristic_centralization(board, player_unit)
            + 0.1 * self._heuristic_adjacency(board, player_unit))

    def _heuristic_score(self, board, player_unit):
        return find_board_score(board, player_unit)

    def _heuristic_centralization(self, board, player_unit):
        score = 0
        for cell, cell_state in board.enumerate():
            if cell_state != player_unit:
                continue
            board_radius = board.height // 2
            board_center = Hex(board_radius, board_radius)
            score += (board_radius - Hex.manhattan(cell, board_center) - 1) * 2
        return score

    def _heuristic_adjacency(self, board, player_unit):
        score = 0
        for cell, cell_state in board.enumerate():
            if cell_state != player_unit:
                continue
            num_allies = sum([board[n] == cell_state for n in Hex.neighbors(cell)])
            score += pow(num_allies, 2)
        return score
