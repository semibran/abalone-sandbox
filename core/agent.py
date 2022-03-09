from math import pow, inf
from copy import deepcopy
from enum import Enum, auto
from dataclasses import dataclass, field
from core.hex import Hex, HexDirection
from core.move import Move
from core.board import Board
from core.board_cell_state import BoardCellState
from core.board_hasher import hash_board, update_hash
from core.game import apply_move, is_move_legal, find_board_score
from config import NUM_EJECTED_MARBLES_TO_WIN

def heuristic(board, player_unit):
    max_score = heuristic_total(board, player_unit)
    min_score = heuristic_total(board, BoardCellState.next(player_unit))
    return max_score - min_score

def heuristic_total(board, player_unit):
    return (
        (WEIGHT_SCORE := 50) * heuristic_score(board, player_unit)
        + (WEIGHT_CENTRALIZATION := 1) * heuristic_centralization(board, player_unit)
        + (WEIGHT_ADJACENCY := 0.1) * heuristic_adjacency(board, player_unit)
    )

def heuristic_score(board, player_unit):
    score = find_board_score(board, player_unit)
    if score >= NUM_EJECTED_MARBLES_TO_WIN:
        return inf
    return score

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


def estimate_move_score(board, move):
    WEIGHT_SUMITO = 10 # consider sumitos first
    return (len(move.pieces())
        + WEIGHT_SUMITO * (board[move.target_cell()] != BoardCellState.EMPTY))


def _traverse_main_line(state_space):
    best_node = state_space
    best_line = []
    best_children = []
    is_max = True
    while best_node.children:
        num_children = len(best_node.children)
        child = sorted(best_node.children.items(), key=lambda child: child[1].score, reverse=is_max)[0]
        best_move, best_node = child
        best_line.append((len(best_line), best_move, f"{best_node.score:.2f}", num_children))
        is_max = not is_max

        if best_node not in best_children:
            best_children.append(best_node)
        else:
            print("cycle!")
            break

    return best_line


@dataclass
class TranspositionTableEntry:

    class Type(Enum):
        PV = auto()
        CUT = auto()
        ALL = auto()

    score: float
    depth: int
    type: Type = None

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
        self._interrupted = False
        self._num_requests = 0
        self._num_prunes_total = 0
        self._num_prunes_last = 0
        self._board_cache = TranspositionTable()

    @property
    def interrupted(self):
        return self._interrupted

    def interrupt(self):
        self._interrupted = True

    def gen_best_move(self, board, player_unit):
        moves = enumerate_player_moves(board, player_unit)

        if not self._should_use_lookaheads(board, player_unit):
            moves.sort(
                key=lambda move: heuristic(apply_move(deepcopy(board), move), player_unit),
                reverse=True
            )
            yield moves[0] if moves else None
            return

        depth = 2
        alpha = -inf
        for move in moves:
            move_board = apply_move(deepcopy(board), move)
            move_score = -self._negamax(move_board, player_unit, depth - 1, -inf, -alpha, -1)
            if move_score > alpha:
                alpha = move_score
                best_move = move
                yield best_move

    def _negamax(self, board, perspective, depth, alpha, beta, color):
        board_hash = hash_board(board)
        if board_hash in self._board_cache and self._board_cache[board_hash].depth >= depth:
            cached_entry = self._board_cache[board_hash]
            if cached_entry.type == TranspositionTableEntry.Type.PV:
                return cached_entry.score
            elif cached_entry.type == TranspositionTableEntry.Type.CUT:
                alpha = max(alpha, cached_entry.score)
            elif cached_entry.type == TranspositionTableEntry.Type.ALL:
                beta = min(beta, cached_entry.score)

        if depth == 0:
            return heuristic(board, perspective) * color

        best_score = -inf
        alpha_old = alpha
        player_unit = perspective if color == 1 else BoardCellState.next(perspective)
        moves = enumerate_player_moves(board, player_unit)
        for move in moves:
            move_board = apply_move(deepcopy(board), move)
            move_score = -self._negamax(move_board, perspective, depth - 1, -beta, -alpha, -color)
            best_score = max(best_score, move_score)
            if alpha >= beta:
                break
            alpha = max(alpha, best_score)

        cached_entry = (self._board_cache[board_hash]
            if board_hash in self._board_cache
            else TranspositionTableEntry(
                score=best_score,
                depth=depth,
            ))

        if board_hash not in self._board_cache:
            self._board_cache[board_hash] = cached_entry

        if best_score <= alpha_old:
            cached_entry.type = TranspositionTableEntry.Type.ALL
        elif best_score >= beta:
            cached_entry.type = TranspositionTableEntry.Type.CUT
        else:
            cached_entry.type = TranspositionTableEntry.Type.PV

        return best_score

    def _should_use_lookaheads(self, board, player_unit):
        num_adjacent_enemies = 0
        for cell, cell_state in board.enumerate():
            if cell_state != player_unit:
                continue
            if next((n for n in Hex.neighbors(cell) if board[n] == BoardCellState.next(player_unit)), False):
                num_adjacent_enemies += 1
        return num_adjacent_enemies >= 2
