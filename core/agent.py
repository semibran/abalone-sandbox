from math import pow, inf
from copy import deepcopy
from dataclasses import dataclass, field
from core.hex import Hex, HexDirection
from core.move import Move
from core.board import Board
from core.board_cell_state import BoardCellState
from core.board_hasher import hash_board, update_hash
from core.game import apply_move, is_move_legal, find_board_score

def heuristic(board, player_unit):
    max_score = heuristic_total(board, player_unit)
    min_score = heuristic_total(board, BoardCellState.next(player_unit))
    return max_score - min_score

def heuristic_total(board, player_unit):
    return (100 * heuristic_score(board, player_unit)
        + heuristic_centralization(board, player_unit)
        + 0.1 * heuristic_adjacency(board, player_unit))

def heuristic_score(board, player_unit):
    return find_board_score(board, player_unit)

def heuristic_centralization(board, player_unit):
    score = 0
    for cell, cell_state in board.enumerate():
        if cell_state != player_unit:
            continue
        board_radius = board.height // 2
        board_center = Hex(board_radius, board_radius)
        score += (board_radius - Hex.manhattan(cell, board_center) - 1) * 2
    return score

def heuristic_adjacency(board, player_unit):
    score = 0
    for cell, cell_state in board.enumerate():
        if cell_state != player_unit:
            continue
        num_allies = sum([board[n] == cell_state for n in Hex.neighbors(cell)])
        score += pow(num_allies, 2)
    return score


def enumerate_player_moves(board, player_unit):
    player_moves = []
    selection_shapes = enumerate_selection_shapes(board, player_unit)
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

def enumerate_selection_shapes(board, player_unit):
    selection_shapes = []
    for cell, color in board.enumerate():
        if color is not player_unit:
            continue
        cell_selection_shapes = enumerate_cell_selection_shapes(board, cell)
        selection_shapes += [shape for shape in cell_selection_shapes if shape not in selection_shapes]
    return selection_shapes

def enumerate_cell_selection_shapes(board, origin):
    selection_shapes = [{origin, origin}]
    for direction in HexDirection:
        cell = origin
        shape = [cell]
        while len(shape) < 3:
            cell = Hex.add(cell, direction.value)
            if board[cell] != board[origin]:
                break
            shape.append(cell)
            if len(shape) > 1:
                selection_shapes.append({shape[0], shape[-1]})

    return selection_shapes


@dataclass
class StateSpace:
    board: Board
    hash: int
    turn: BoardCellState
    score: float = None
    children: dict = field(default_factory=dict)

@dataclass
class TranspositionTable:

    def __init__(self):
        self._table = {}
        self._cache_hash = None, None

    def _hash_board(self, board):
        """
        Uses the most recently calculated hash if existent.
        """
        cached_hash, cached_board = self._cache_hash
        if board is cached_board:
            hash = cached_hash
        else:
            hash = hash_board(board)
            self._cache_hash = (hash, board)
        return hash

    def __contains__(self, hash):
        # TODO: do we even want to input boards?
        if type(hash) is Board:
            hash = self._hash_board(hash)
        return hash in self._table

    def __getitem__(self, hash):
        if type(hash) is Board:
            hash = self._hash_board(hash)
        return self._table[hash]

    def __setitem__(self, hash, node):
        if type(hash) is Board:
            hash = self._hash_board(hash)
        self._table[hash] = node

class Agent:

    def __init__(self):
        self.interrupt = False
        self._num_requests = 0
        self._num_prunes_total = 0
        self._num_prunes_last = 0
        self._board_cache = TranspositionTable()

    def gen_best_move(self, board, player_unit):
        self._num_prunes_last = 0
        self._num_requests += 1

        board_hash = hash_board(board)
        if board_hash in self._board_cache:
            state_space = self._board_cache[board_hash]
        else:
            state_space = self._board_cache[board_hash] = StateSpace(board, hash=board_hash, turn=player_unit)

        best_score = -inf
        best_move = None
        depth = 1
        self.interrupt = False
        while not self.interrupt:
            if state_space.children:
                for move, child in state_space.children.items():
                    move_score = self._expand_state_space(child, player_unit, depth - 1, alpha=best_score, beta=inf)
                    if move_score > best_score:
                        best_score = move_score
                        best_move = move
                        yield best_move

                    if self.interrupt:
                        break
            else:
                moves = enumerate_player_moves(board, player_unit)
                for move in moves:

                    move_hash = update_hash(board_hash, board, move)
                    next_turn = BoardCellState.next(state_space.turn)
                    if move_hash in self._board_cache and self._board_cache[move_hash].turn == next_turn:
                        child = self._board_cache[move_hash]
                    else:
                        move_board = apply_move(deepcopy(board), move)
                        child = self._board_cache[move_hash] = StateSpace(
                            board=move_board,
                            hash=move_hash,
                            turn=next_turn
                        )

                    if move not in state_space.children:
                        state_space.children[move] = child

                    move_score = self._expand_state_space(child, player_unit, depth - 1, alpha=best_score, beta=inf)
                    if move_score > best_score:
                        best_score = move_score
                        best_move = move
                        yield best_move

                    if self.interrupt:
                        break

            not self.interrupt and print("complete search at depth", depth)
            depth += 1

        self._num_prunes_total += self._num_prunes_last
        print(f"pruned {self._num_prunes_last} subtrees ({self._num_prunes_total / self._num_requests:.2f} avg)")

    def _expand_state_space(self, state_space, perspective, depth, alpha, beta):
        if depth == 0:
            score = state_space.score = heuristic(state_space.board, perspective)
            return score

        is_max = perspective == state_space.turn
        best_score = -inf if is_max else inf
        if state_space.children:
            for move, child in state_space.children.items():
                if self.interrupt:
                    return best_score

                move_score = self._expand_state_space(child, perspective, depth - 1, alpha, beta)
                if is_max:
                    best_score = max(best_score, move_score)
                    if best_score >= beta:
                        self._num_prunes_last += 1
                        break
                    alpha = max(alpha, move_score)
                else:
                    best_score = min(best_score, move_score)
                    if move_score <= alpha:
                        self._num_prunes_last += 1
                        break
                    beta = min(beta, move_score)
        else:
            moves = enumerate_player_moves(state_space.board, state_space.turn)
            for move in moves:
                if self.interrupt:
                    state_space.children.clear()
                    return -inf if is_max else inf

                move_hash = update_hash(state_space.hash, state_space.board, move)
                next_turn = BoardCellState.next(state_space.turn)
                if move_hash in self._board_cache and self._board_cache[move_hash].turn == next_turn:
                    child = self._board_cache[move_hash]
                else:
                    move_board = apply_move(deepcopy(state_space.board), move)
                    child = self._board_cache[move_hash] = StateSpace(
                        board=move_board,
                        hash=move_hash,
                        turn=next_turn,
                    )

                if move not in state_space.children:
                    state_space.children[move] = child

                move_score = self._expand_state_space(child, perspective, depth - 1, alpha, beta)
                if is_max:
                    best_score = max(best_score, move_score)
                    if best_score >= beta:
                        self._num_prunes_last += 1
                        break
                    alpha = max(alpha, move_score)
                else:
                    best_score = min(best_score, move_score)
                    if move_score <= alpha:
                        self._num_prunes_last += 1
                        break
                    beta = min(beta, move_score)

        state_space.score = best_score
        return best_score

    def _should_use_lookaheads(self, board, player_unit):
        num_adjacent_enemies = 0
        for cell, cell_state in board.enumerate():
            if cell_state != player_unit:
                continue
            if next((n for n in Hex.neighbors(cell) if board[n] == BoardCellState.next(player_unit)), False):
                num_adjacent_enemies += 1
        return num_adjacent_enemies >= 2

    def _estimate_move_score(self, board, move):
        WEIGHT_SUMITO = 10 # consider sumitos first
        return (len(move.pieces())
            + WEIGHT_SUMITO * (board[move.target_cell()] != BoardCellState.EMPTY))
