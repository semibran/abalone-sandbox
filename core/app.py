from tkinter import Tk
from core.app_config import AppConfig
from core.game import Game
from core.display import Display
from config import APP_NAME

class App:
    def __init__(self):
        self._config = AppConfig()
        self._game = None
        self._display = Display(title=APP_NAME)

    def _new_game(self):
        self._game = Game(layout=self._config.starting_layout)

    def start(self):
        self._new_game()
        self._display.open(self._game.board)
