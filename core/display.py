from math import sqrt
from tkinter import Tk, Canvas
from helpers.point_to_hex import point_to_hex
from config import (
    BOARD_SIZE, BOARD_MAXCOLS,
    BOARD_CELL_SIZE,
    BOARD_WIDTH, BOARD_HEIGHT,
    MARBLE_SIZE,
)

def point_to_hex_offset(point, radius, board):
    q, r = point_to_hex(point, radius)
    if r > board.height // 2:
        q -= (r - board.height // 2)
    return q, r

def render_board(canvas, board, selection=None, pos=(0, 0)):
    canvas.create_rectangle(0, 0, BOARD_WIDTH, BOARD_HEIGHT, fill="#fff")
    for (q, r), val in board.enumerate():
        x = (q * BOARD_CELL_SIZE
            + (BOARD_MAXCOLS - board.width(r) + 1) * BOARD_CELL_SIZE / 2
            + pos[0])
        y = (r * (BOARD_CELL_SIZE * 7 / 8)
            + BOARD_CELL_SIZE / 2
            + pos[1])
        circle_fill = {
            0: "#ccc",
            1: "#36c",
            2: "#c36",
        }[val]
        circle_outline = ("#9cf"
            if (q, r) == selection
            else "")
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
            rh := BOARD_CELL_SIZE / (sqrt(3) / 2) / 2,
            x := event.x - rw - (BOARD_MAXCOLS - BOARD_SIZE) * rw,
            y := event.y - rw,
            actions["select_cell"](point_to_hex_offset((x, y), rh, app.game_board))
        ))

        self.render(app)
        self._window.mainloop()

    def render(self, app):
        render_board(self._canvas, app.game_board, selection=app.selection)
