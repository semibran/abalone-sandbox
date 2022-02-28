from tkinter import Tk
from display.game import GameDisplay

class Display:

    def __init__(self, title):
        self._title = title
        self._window = None
        self._closed = False
        self._game_display = None

    @property
    def is_animating(self):
        return self._game_display.is_animating

    @property
    def closed(self):
        return self._closed

    def open(self, on_click):
        self._window = Tk()
        self._window.title(self._title)
        self._window.protocol("WM_DELETE_WINDOW", lambda: setattr(self, "_closed", True))

        self._game_display = GameDisplay()
        canvas = self._game_display.open(self._window, on_click)
        canvas.pack()

    def clear_board(self):
        self._game_display.clear()

    def update(self):
        self._window.update()
        self._game_display.update()

    def update_hud(self, app):
        self._game_display.update_hud(app)

    def render(self, app):
        self._game_display.render(app)

    def perform_move(self, move, board, on_end=None):
        self._game_display.perform_move(move, board, on_end)
