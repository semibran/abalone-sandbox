"""
Generic interface for game history.
"""

from dataclasses import dataclass, field
from core.move import Move


@dataclass
class GameHistoryItem:
    """
    A game history item.
    """

    move: Move
    time_start: float = None
    time_end: float = None

@dataclass
class GameHistory:
    """
    A simple interface around the game history stack.

    Game history unlocks a non-negligible chunk of the application's core
    functionality:
    - The current game turn may be deduced via Color.next(history[-1].color)
    - The current game ply may be deduced via floor(len(history))
    - The time taken for a move is the delta of `time_start` and `time_end`
    - Total aggregate time for a given player may be determined via the
    summation of all `time_end` - `time_start` deltas
    - "Time-travel" undo logic may be achieved by reconstructing the game board
    using all moves within history[:-1] starting from the starting layout
    (i.e. the more space-efficient implementation)
    """

    def __init__(self):
        self._actions = []

    def __getitem__(self, index):
        """
        Gets the item at the specified index.
        :param index: an int
        :return: a HistoryItem
        """
        return self._actions[index]

    def __len__(self):
        """
        Determines the length of the history stack.
        :return: an int
        """
        return len(self._actions)

    def __iter__(self):
        return self._actions.__iter__()

    def __next__(self):
        return self._actions.__next__()

    def append(self, action):
        """
        Appends an action to the history stack.
        :param action: a HistoryItem
        :return: None
        """
        self._actions.append(action)

    def pop(self):
        """
        Pops an action off the history stack.
        :return: a HistoryItem
        """
        return self._actions.pop()
