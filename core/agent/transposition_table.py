from __future__ import annotations
from enum import Enum, auto
from dataclasses import dataclass
from core.move import Move
from core.board import Board
from core.board_hasher import hash_board


@dataclass
class TranspositionTable:

    class EntryType(Enum):
        PV = auto()
        CUT = auto()
        ALL = auto()

    @dataclass
    class Entry:
        score: float
        depth: int
        move: Move = None
        type: TranspositionTable.EntryType = None

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
