from math import inf
from copy import deepcopy
from time import time
from helpers.format_secs import format_secs
from core.agent.heuristic import heuristic
from core.agent.state_generator import enumerate_player_moves
from core.agent.transposition_table import TranspositionTable
from core.hex import Hex
from core.board_cell_state import BoardCellState
from core.board_hasher import hash_board, update_hash
from core.game import apply_move


class TimerInterrupt(Exception):
    pass


def _estimate_move_score(board, move):
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


class Agent:

    def __init__(self):
        self._interrupted = False
        self._num_requests = 0
        self._num_prunes_total = 0
        self._num_prunes_last = 0
        self._num_plies_expanded = 0
        self._num_branches_explored = 0
        self._num_branches_enumerated = 0
        self._board_cache = TranspositionTable()
        self._best_move_gen = None

    @property
    def interrupted(self):
        return self._interrupted

    def interrupt(self):
        print("call interrupt")
        self._interrupted = True

    def start(self, board, color):
        self._best_move_gen = self.gen_best_move(board, color)

    def find_next_best_move(self):
        try:
            best_move = next(self._best_move_gen)
            done_search = False
        except StopIteration:
            best_move = None
            done_search = True
        return best_move, done_search

    def gen_best_move(self, board, player_unit):
        moves = enumerate_player_moves(board, player_unit)

        if not self._should_use_lookaheads(board, player_unit):
            moves.sort(
                key=lambda move: heuristic(apply_move(deepcopy(board), move), player_unit),
                reverse=True
            )
            yield moves[0] if moves else None
            return

        depth = 1
        best_move = None
        board_hash = hash_board(board)
        time_start = time()
        self._interrupted = False
        while not self._interrupted:
            print(f"init search at depth {depth}")
            alpha = -inf
            if best_move is None:
                moves.sort(key=lambda move: _estimate_move_score(board, move))
            elif best_move in moves:
                moves.remove(best_move)
                moves.insert(0, best_move)

            self._num_plies_expanded += 1
            self._num_branches_explored += len(moves)
            self._num_branches_enumerated += len(moves)

            for move in moves:
                move_board = apply_move(deepcopy(board), move)
                move_hash = update_hash(board_hash, board, move)

                try:
                    if move == moves[0]:
                        move_score = -self._inverse_search(move_board, move_hash, player_unit, depth - 1, -inf, -alpha, -1)
                    else:
                        move_score = -self._inverse_search(move_board, move_hash, player_unit, depth - 1, -alpha - 1, -alpha, -1)
                        if move_score > alpha:
                            move_score = -self._inverse_search(move_board, move_hash, player_unit, depth - 1, -inf, -move_score, -1)
                except TimerInterrupt:
                    return

                if move_score > alpha:
                    alpha = move_score
                    best_move = move
                    yield best_move
                    print(f"average effective branching factor: {self._num_branches_explored / self._num_plies_expanded:.2f}/{self._num_branches_enumerated / self._num_plies_expanded:.2f}")

            print(f"complete search at depth {depth} in {format_secs(time() - time_start)}")
            depth += 1


    def _inverse_search(self, board, board_hash, perspective, depth, alpha, beta, color):
        if self._interrupted:
            print("receive interrupt")
            raise TimerInterrupt()

        if board_hash in self._board_cache and self._board_cache[board_hash].depth >= depth:
            cached_entry = self._board_cache[board_hash]
            if cached_entry.type == TranspositionTable.EntryType.PV:
                return cached_entry.score
            elif cached_entry.type == TranspositionTable.EntryType.CUT:
                alpha = max(alpha, cached_entry.score)
            elif cached_entry.type == TranspositionTable.EntryType.ALL:
                beta = min(beta, cached_entry.score)
        else:
            cached_entry = None

        if depth == 0:
            return heuristic(board, perspective) * color

        best_score = -inf
        best_move = cached_entry.move if cached_entry else None
        alpha_old = alpha
        player_unit = perspective if color == 1 else BoardCellState.next(perspective)
        moves = enumerate_player_moves(board, player_unit)
        if best_move and best_move in moves:
            moves.remove(best_move)
            moves.insert(0, best_move)

        self._num_plies_expanded += 1
        self._num_branches_enumerated += len(moves)

        for move in moves:
            move_board = apply_move(deepcopy(board), move)
            move_hash = update_hash(board_hash, board, move)

            if move == moves[0]:
                move_score = -self._inverse_search(move_board, move_hash, perspective, depth - 1, -beta, -alpha, -color)
            else:
                move_score = -self._inverse_search(move_board, move_hash, perspective, depth - 1, -alpha - 1, -alpha, -color)
                if move_score > alpha or move_score < beta:
                    move_score = -self._inverse_search(move_board, move_hash, perspective, depth - 1, -beta, -move_score, -color)

            if move_score > best_score:
                best_score = move_score
                best_move = move

            alpha = max(alpha, best_score)
            if alpha >= beta:
                self._num_branches_explored += moves.index(move) + 1
                break
        else:
            self._num_branches_explored += len(moves)

        cached_entry = (self._board_cache[board_hash]
            if board_hash in self._board_cache
            else TranspositionTable.Entry(
                score=best_score,
                move=best_move,
                depth=depth,
            ))

        if board_hash not in self._board_cache:
            self._board_cache[board_hash] = cached_entry

        if best_score <= alpha_old:
            cached_entry.type = TranspositionTable.EntryType.ALL
        elif best_score >= beta:
            cached_entry.type = TranspositionTable.EntryType.CUT
        else:
            cached_entry.type = TranspositionTable.EntryType.PV

        return best_score

    def _should_use_lookaheads(self, board, player_unit):
        num_adjacent_enemies = 0
        for cell, cell_state in board.enumerate():
            if cell_state != player_unit:
                continue
            if next((n for n in Hex.neighbors(cell) if board[n] == BoardCellState.next(player_unit)), False):
                num_adjacent_enemies += 1
        return num_adjacent_enemies >= 2
