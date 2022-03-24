from math import pow, inf
from core.hex import Hex
from core.board_cell_state import BoardCellState
from core.game import find_board_score
from config import NUM_EJECTED_MARBLES_TO_WIN


def heuristic(board, player_unit):
    max_score = _heuristic_total(board, player_unit)
    min_score = _heuristic_total(board, BoardCellState.next(player_unit))
    return max_score - min_score

def _heuristic_total(board, player_unit):
    return (
        (WEIGHT_SCORE := 50) * _heuristic_score(board, player_unit)
        + (WEIGHT_CENTRALIZATION := 1) * _heuristic_centralization(board, player_unit)
        + (WEIGHT_ADJACENCY := 0.1) * _heuristic_adjacency(board, player_unit)
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
