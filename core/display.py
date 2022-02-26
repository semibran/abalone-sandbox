from math import sqrt
from tkinter import Tk, Canvas
from helpers.point_to_hex import point_to_hex
from config import (
    BOARD_SIZE, BOARD_MAXCOLS,
    BOARD_CELL_SIZE,
    BOARD_WIDTH, BOARD_HEIGHT,
    MARBLE_SIZE,
)

def render_board(canvas, board, pos=(0, 0)):
    for (q, r), val in board.enumerate():
        x = (q * BOARD_CELL_SIZE
            + (BOARD_MAXCOLS - board.width(r) + 1) * BOARD_CELL_SIZE / 2
            + pos[0])
        y = (r * (BOARD_CELL_SIZE * 7 / 8)
            + BOARD_CELL_SIZE / 2
            + pos[1])
        circle_color = {
            0: "#ccc",
            1: "#c36",
            2: "#36c",
        }[val]
        canvas.create_oval(
            x - MARBLE_SIZE / 2, y - MARBLE_SIZE / 2,
            x + MARBLE_SIZE / 2, y + MARBLE_SIZE / 2,
            fill=circle_color, outline=""
        )

class Display:
    def __init__(self, title):
        self._title = title
        self._window = None
        self._canvas = None

    def open(self, board):
        self._window = Tk()
        self._window.title(self._title)

        self._canvas = Canvas(self._window, width=BOARD_WIDTH, height=BOARD_HEIGHT, highlightthickness=0)
        self._canvas.pack()
        self._canvas.bind("<Button-1>", lambda event: (
            rw := BOARD_CELL_SIZE / 2,
            rh := BOARD_CELL_SIZE / (sqrt(3) / 2) / 2,
            x := event.x - rw - (BOARD_MAXCOLS - BOARD_SIZE) * rw,
            y := event.y - rw,
            print(point_to_hex((x, y), rh))
        ))
        render_board(self._canvas, board)

        self._window.mainloop()
