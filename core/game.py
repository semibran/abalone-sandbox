from core.board import Board
from helpers.setup_board import setup_board

class Game:
    def __init__(self, layout):
        self._board = setup_board(layout)
