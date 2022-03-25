from math import pow, inf
from core.hex import Hex
from core.board_cell_state import BoardCellState
from core.game import find_board_score
from config import BOARD_SIZE, NUM_EJECTED_MARBLES_TO_WIN
from debug.profiler import MeanProfiler


WEIGHT_SCORE = 50
WEIGHT_CENTRALIZATION = 1
WEIGHT_CENTRALIZATION_OPPONENT = 0.5
WEIGHT_ADJACENCY = 0.1
WEIGHT_ADJACENCY_OPPONENT = 0.05

profiler = MeanProfiler()


def heuristic(board, player_unit):
    # profiler.start()
    score = _heuristic_optimized(board, player_unit)
    # profiler.stop(label="avg heuristic speed")
    return score

def _heuristic_optimized(board, color):
    MAX_MARBLES = 14
    BOARD_RADIUS = BOARD_SIZE - 1
    BOARD_CENTER = Hex(BOARD_RADIUS, BOARD_RADIUS)

    heuristic_score = MAX_MARBLES
    heuristic_centralization = 0
    heuristic_centralization_opponent = 0
    heuristic_adjacency = 0
    heuristic_adjacency_opponent = 0

    for cell, cell_color in board.enumerate_nonempty():
        if cell_color == BoardCellState.EMPTY:
            continue

        cell_centralization = BOARD_RADIUS - Hex.manhattan(cell, BOARD_CENTER) - 1
        cell_adjacency = sum([board[n] == cell_color for n in Hex.neighbors(cell)])

        if cell_color == color:
            heuristic_centralization += cell_centralization
            heuristic_adjacency += cell_adjacency
        else:
            heuristic_centralization_opponent += cell_centralization
            heuristic_adjacency_opponent += cell_adjacency
            heuristic_score -= 1

    return (
        WEIGHT_SCORE * heuristic_score
        + WEIGHT_CENTRALIZATION * heuristic_centralization
        + WEIGHT_CENTRALIZATION_OPPONENT * heuristic_centralization_opponent
        + WEIGHT_ADJACENCY * heuristic_adjacency
        + WEIGHT_ADJACENCY_OPPONENT * heuristic_adjacency_opponent
    )

def _heuristic_total(board, player_unit):
    return (
        (WEIGHT_SCORE := 50) * _heuristic_score(board, player_unit)
        + (WEIGHT_CENTRALIZATION := 1) * _heuristic_centralization(board, player_unit)
        + (WEIGHT_CENTRALIZATION := 0.5) * -_heuristic_centralization(board, BoardCellState.next(player_unit))
        + (WEIGHT_ADJACENCY := 0.1) * _heuristic_adjacency(board, player_unit)
        + (WEIGHT_CENTRALIZATION := 0.05) * -_heuristic_adjacency(board, BoardCellState.next(player_unit))
    )

def _heuristic_score(board, player_unit):
    score = find_board_score(board, player_unit)
    if score >= NUM_EJECTED_MARBLES_TO_WIN:
        return inf
    return score

def _heuristic_centralization(board, player_unit):
    score = 0
    for cell, cell_state in board.enumerate():
        if cell_state != player_unit:
            continue
        board_radius = board.height // 2
        board_center = Hex(board_radius, board_radius)
        score += (board_radius - Hex.manhattan(cell, board_center) - 1) * 2
    return score

def _heuristic_adjacency(board, player_unit):
    score = 0
    for cell, cell_state in board.enumerate():
        if cell_state != player_unit:
            continue
        num_allies = sum([board[n] == cell_state for n in Hex.neighbors(cell)])
        score += pow(num_allies, 2)
    return score
