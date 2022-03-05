from math import pow, inf
from copy import deepcopy
from dataclasses import dataclass, field
from core.hex import Hex, HexDirection
from core.move import Move
from core.board import Board
from core.board_cell_state import BoardCellState
from core.board_hasher import hash_board, update_hash
from core.game import apply_move, is_move_legal, find_board_score

@dataclass
class StateSpace:
    board: Board
    hash: int
    move: Move = None
    score: float = None
    children: list = field(default_factory=list)

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
            state_space = self._board_cache[board_hash] = StateSpace(board, hash=board_hash)

        best_score = -inf
        best_move = None
        best_board = None
        depth = 1
        self.interrupt = False
        while not self.interrupt:
            alpha = -inf
            beta = inf
            for move in self._enumerate_player_moves(board, player_unit):
                move_board = apply_move(board=deepcopy(board), move=move)
                move_hash = update_hash(board_hash, board, move)
                move_score = -self._negamax(
                    board=move_board,
                    board_hash=move_hash,
                    color=player_unit,
                    perspective=-1,
                    depth=depth,
                    alpha=-beta,
                    beta=-alpha,
                )
                child_space = self._board_cache[move_hash]
                child_space.move = move
                if child_space not in state_space.children:
                    state_space.children.append(child_space)

                alpha = max(alpha, move_score)

                print(f"move {move} for max has score {move_score:.2f}")
                if move_score >= best_score:
                    best_score = move_score
                    best_move = move
                    best_board = move_board
                    print(f"new best move {best_move} for max has score {best_score:.2f}")
                    yield best_move

                if self.interrupt:
                    break
            depth += 1
            not self.interrupt and print(f"completed search at depth {depth}")

        node = self._board_cache[board]
        line = []
        is_max = True
        while node.children:
            num_children = len(node.children)
            node = sorted(node.children, key=lambda child: child.score, reverse=not is_max)[0]
            line.append((len(line), node.move, num_children))
            is_max = not is_max
        print(f"main line is {line}")

        self._num_prunes_total += self._num_prunes_last
        print(f"pruned {self._num_prunes_last} subtrees ({self._num_prunes_total / self._num_requests:.2f} avg)")

    def _negamax(self, board, board_hash, color, perspective, depth, alpha, beta):
        if board_hash in self._board_cache:
            state_space = self._board_cache[board_hash]
        else:
            state_space = self._board_cache[board_hash] = StateSpace(board, hash=board_hash)

        if depth == 0:
            terminal_score = state_space.score = self._heuristic(board, color if perspective == 1 else BoardCellState.next(color))
            return terminal_score

        best_score = -inf
        # if state_space.children:
        #     for child in state_space.children:
        #         if self.interrupt:
        #             return best_score

        #         move_score = -self._negamax(
        #             board=child.board,
        #             board_hash=child.hash,
        #             color=color,
        #             perspective=-perspective,
        #             depth=depth - 1,
        #             alpha=-beta,
        #             beta=-alpha,
        #         )
        #         child_space = self._board_cache[child.hash]
        #         child_space.score = move_score
        #         if child_space not in state_space.children:
        #             state_space.children.append(child_space)

        #         best_score = state_space.score = max(best_score, move_score)
        #         alpha = max(alpha, best_score)
        #         if alpha >= beta:
        #             self._num_prunes_last += 1
        #             break
        # else:

        moves = self._enumerate_player_moves(
            board,
            player_unit=(color
                if perspective == 1
                else BoardCellState.next(color))
        )
        print(color if perspective == 1 else BoardCellState.next(color),
            f"enumerate {len(moves)}",
            "alpha", f"{alpha:.2f}",
            "beta", f"{beta:.2f}",)

        for move in moves:
            if self.interrupt:
                return best_score

            move_board = apply_move(board=deepcopy(board), move=move)
            move_hash = update_hash(board_hash, board, move)
            move_score = -self._negamax(
                board=move_board,
                board_hash=move_hash,
                color=color,
                perspective=-perspective,
                depth=depth - 1,
                alpha=-beta,
                beta=-alpha,
            )
            child_space = self._board_cache[move_hash]
            child_space.score = -move_score
            child_space.move = move
            if child_space not in state_space.children:
                state_space.children.append(child_space)

            best_score = state_space.score = max(best_score, move_score)
            alpha = max(alpha, best_score)
            if alpha >= beta:
                self._num_prunes_last += 1
                break

        print(color if perspective == 1 else BoardCellState.next(color),
            f"enumerate {sorted([(child_space.move, round(child_space.score * 100) / 100 if abs(child_space.score) != inf else child_space.score) for child_space in state_space.children], key=lambda node: node[1], reverse=True)}",
            "alpha", f"{alpha:.2f}",
            "beta", f"{beta:.2f}",)

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

    def _enumerate_player_moves(self, board, player_unit):
        player_moves = []
        selection_shapes = self._enumerate_selection_shapes(board, player_unit)
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

    def _enumerate_selection_shapes(self, board, player_unit):
        selection_shapes = []
        for cell, cell_state in board.enumerate():
            if cell_state is not player_unit:
                continue
            cell_selection_shapes = self._enumerate_cell_selection_shapes(board, cell)
            selection_shapes += [shape for shape in cell_selection_shapes if shape not in selection_shapes]
        return selection_shapes

    def _enumerate_cell_selection_shapes(self, board, origin):
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

    def _heuristic(self, board, player_unit):
        max_score = self._heuristic_total(board, player_unit)
        min_score = self._heuristic_total(board, BoardCellState.next(player_unit))
        return max_score - min_score

    def _heuristic_total(self, board, player_unit):
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
