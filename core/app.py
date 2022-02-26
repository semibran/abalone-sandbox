from tkinter import Tk
from core.app_config import AppConfig
from core.game import Game
from config import APP_NAME

class App:
    def __init__(self):
        self._config = AppConfig()
        self._game = None
        self._window = None

    def _new_game(self):
        self._game = Game(layout=self._config.starting_layout)

    def _open_window(self):
        self._window = Tk()
        self._window.title(APP_NAME)
        self._window.mainloop()

    def start(self):
        self._new_game()
        self._open_window()
