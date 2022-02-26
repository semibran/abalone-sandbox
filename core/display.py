from math import sqrt
from helpers.point_to_hex import point_to_hex
from tkinter import Tk, Canvas
from core.board_cell_state import BoardCellState
from core.hex import Hex
from config import (
    BOARD_SIZE, BOARD_MAXCOLS,
    BOARD_CELL_SIZE,
    BOARD_WIDTH, BOARD_HEIGHT,
    MARBLE_SIZE,
)
import colors.palette as palette
from colors.darken import darken_color

def render_board(canvas, board, selection=None, pos=(0, 0)):
    canvas.create_rectangle(0, 0, BOARD_WIDTH, BOARD_HEIGHT, fill="#fff")
    for cell, val in board.enumerate():
        q, r = cell.astuple()
        q += r * (r <= board.height // 2)
        x = (q * BOARD_CELL_SIZE
            + (BOARD_MAXCOLS - board.width(r) + 1) * BOARD_CELL_SIZE / 2
            + pos[0])
        y = (r * (BOARD_CELL_SIZE * 7 / 8)
            + BOARD_CELL_SIZE / 2
            + pos[1])

        is_cell_selected = selection and selection.pieces() and cell in selection.pieces()
        circle_fill = {
            BoardCellState.EMPTY: palette.COLOR_SILVER,
            BoardCellState.WHITE: palette.COLOR_BLUE,
            BoardCellState.BLACK: palette.COLOR_RED,
        }[val]
        if is_cell_selected:
            circle_fill = darken_color(circle_fill)
        circle_outline = (palette.COLOR_CYAN if is_cell_selected else "")
        canvas.create_oval(
            x - MARBLE_SIZE / 2, y - MARBLE_SIZE / 2,
            x + MARBLE_SIZE / 2, y + MARBLE_SIZE / 2,
            fill=circle_fill,
            outline=circle_outline,
            width=4,
        )

class Display:
    def __init__(self, title):
        self._title = title
        self._window = None
        self._canvas = None

    def open(self, app, actions):
        self._window = Tk()
        self._window.title(self._title)

        self._canvas = Canvas(self._window, width=BOARD_WIDTH, height=BOARD_HEIGHT, highlightthickness=0)
        self._canvas.pack()
        self._canvas.bind("<Button-1>", lambda event: (
            rw := BOARD_CELL_SIZE / 2,
            rh := BOARD_CELL_SIZE / sqrt(3),
            x := event.x - rw - (BOARD_MAXCOLS - BOARD_SIZE) * rw,
            y := event.y - rw,
            actions["select_cell"](Hex(*point_to_hex((x, y), rh)))
        ))

        self.render(app)
        self._window.mainloop()

    def render(self, app):
        render_board(self._canvas, app.game_board, selection=app.selection)
