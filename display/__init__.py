from time import time
from tkinter import Tk, messagebox
from tkinter.ttk import Frame, Button, Label
from helpers.format_secs import format_secs
from display.game import GameDisplay
from display.settings import SettingsWindow

class Display:

    def __init__(self, title):
        self._title = title
        self._window = None
        self._closed = False
        self._game_display = None
        self._is_settings_open = False

    @property
    def is_animating(self):
        return self._game_display.is_animating

    @property
    def is_settings_open(self):
        return self._is_settings_open

    @property
    def closed(self):
        return self._closed

    def open(self, on_click, on_reset, on_settings):
        self._window = Tk()
        self._window.title(self._title)
        self._window.protocol("WM_DELETE_WINDOW", lambda: setattr(self, "_closed", True))

        header = Frame(self._window)
        header.pack(fill="x", expand=True, ipady=8)

        reset_button = Button(header, text="Reset", command=on_reset)
        reset_button.pack(anchor="w", side="left", padx=8)

        timer_label = Label(header, text="0")
        timer_label.pack(anchor="w", side="left", padx=0)
        self._timer_label = timer_label

        settings_button = Button(header, text="Settings", command=on_settings)
        settings_button.pack(anchor="e", side="right", fill="x", padx=8)

        self._game_display = GameDisplay()
        canvas = self._game_display.open(self._window, on_click)
        canvas.pack()

    def open_settings(self, current_config, on_close=None):
        if self._is_settings_open:
            return
        self._is_settings_open = True
        SettingsWindow.open(current_config, lambda *args: (
            on_close and on_close(*args),
            setattr(self, "_is_settings_open", False)
        ))

    def confirm_reset(self):
        return messagebox.askokcancel("Confirm reset", "Reset the game? All unsaved progress will be lost.")

    def confirm_settings(self):
        return messagebox.askokcancel("Confirm open settings menu", "Change game settings? The game board will be reset.")

    def clear_board(self):
        self._game_display.clear()

    def update(self):
        self._window.update()
        self._game_display.update()

    def update_hud(self, app):
        self._game_display.update_hud(app)

    def update_timer(self, start_time):
        self._timer_label.config(text=format_secs(time() - start_time))

    def render(self, app):
        self._game_display.render(app)

    def perform_move(self, move, board, on_end=None):
        self._game_display.perform_move(move, board, on_end)
