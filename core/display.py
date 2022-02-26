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
from colors.transform import darken_color, lighten_color

MARBLE_COLORS = {
    BoardCellState.WHITE: palette.COLOR_BLUE,
    BoardCellState.BLACK: palette.COLOR_RED,
}

def render_marble(canvas, pos, color, size=MARBLE_SIZE, selected=False, focused=False):
    MARBLE_COLOR = darken_color(color) if selected else color

    x, y = pos
    s = size

    # marble body
    canvas.create_oval(
        x - s / 2, y - s / 2,
        x + s / 2, y + s / 2,
        fill=MARBLE_COLOR,
        outline=darken_color(MARBLE_COLOR),
        width=2,
    )

    # marble outline
    if focused:
        RING_WIDTH = 3
        RING_MARGIN = 2
        RING_SIZE = s / 2 + 2
        canvas.create_oval(
            x - RING_SIZE - RING_WIDTH, y - RING_SIZE - RING_WIDTH,
            x + RING_SIZE + RING_MARGIN, y + RING_SIZE + RING_MARGIN,
            fill="",
            outline=lighten_color(color),
            width=RING_WIDTH,
        )

    # marble highlights
    HIGHLIGHT_SIZE = s * 3 / 4
    HIGHLIGHT_X = x - HIGHLIGHT_SIZE / 2
    HIGHLIGHT_Y = y - HIGHLIGHT_SIZE / 2
    canvas.create_oval(
        HIGHLIGHT_X, HIGHLIGHT_Y,
        HIGHLIGHT_X + HIGHLIGHT_SIZE, HIGHLIGHT_Y + HIGHLIGHT_SIZE,
        fill=lighten_color(MARBLE_COLOR),
        outline="",
    )
    HIGHLIGHT_NEGATIVE_SIZE = HIGHLIGHT_SIZE + HIGHLIGHT_SIZE / 32
    canvas.create_oval(
        x - s / 2 + s / 16, y - s / 2 + s / 16,
        x - s / 2 + s / 16 + HIGHLIGHT_NEGATIVE_SIZE, y - s / 2 + s / 16 + HIGHLIGHT_NEGATIVE_SIZE,
        fill=MARBLE_COLOR,
        outline="",
    )
    canvas.create_oval(
        x - s / 2 + s / 4, y - s / 32,
        x + s / 2 - s / 4, y - s / 32 + s / 3,
        fill=darken_color(MARBLE_COLOR),
        outline="",
    )
    HIGHLIGHT_BALANCE_SIZE = HIGHLIGHT_SIZE / 3
    HIGHLIGHT_BALANCE_X = x - HIGHLIGHT_SIZE / 8
    HIGHLIGHT_BALANCE_Y = y - HIGHLIGHT_SIZE / 6
    canvas.create_oval(
        HIGHLIGHT_BALANCE_X, HIGHLIGHT_BALANCE_Y,
        HIGHLIGHT_BALANCE_X + HIGHLIGHT_BALANCE_SIZE, HIGHLIGHT_BALANCE_Y + HIGHLIGHT_BALANCE_SIZE,
        fill=MARBLE_COLOR,
        outline="",
    )

    # marble shine
    SHINE_X = x - s / 4
    SHINE_Y = y - s / 3
    SHINE_SIZE = s / 4
    canvas.create_oval(
        SHINE_X, SHINE_Y,
        SHINE_X + SHINE_SIZE, SHINE_Y + SHINE_SIZE,
        fill=lighten_color(MARBLE_COLOR),
        outline="",
    )

    # marble shine core
    SHINE_CORE_OFFSET = s / 24
    SHINE_CORE_X = SHINE_X + SHINE_CORE_OFFSET * 3 / 4
    SHINE_CORE_Y = SHINE_Y + SHINE_CORE_OFFSET * 3 / 4
    SHINE_CORE_SIZE = SHINE_SIZE - SHINE_CORE_OFFSET * 2
    canvas.create_oval(
        SHINE_CORE_X, SHINE_CORE_Y,
        SHINE_CORE_X + SHINE_CORE_SIZE, SHINE_CORE_Y + SHINE_CORE_SIZE,
        fill=palette.COLOR_WHITE,
        outline="",
    )

    # marble secondary shine
    SHINE_SECONDARY_X = x - s / 3
    SHINE_SECONDARY_Y = y - s / 8
    SHINE_SECONDARY_SIZE = s / 10
    canvas.create_oval(
        SHINE_SECONDARY_X, SHINE_SECONDARY_Y,
        SHINE_SECONDARY_X + SHINE_SECONDARY_SIZE, SHINE_SECONDARY_Y + SHINE_SECONDARY_SIZE,
        fill=lighten_color(MARBLE_COLOR),
        outline="",
    )

def render_board_cell(canvas, pos, cell, cell_state, selection):
    is_cell_selected = selection and selection.pieces() and cell in selection.pieces()
    is_cell_focused = selection and cell == selection.head()

    # draw empty slot
    x, y = pos
    canvas.create_oval(
        x - MARBLE_SIZE / 2, y - MARBLE_SIZE / 2,
        x + MARBLE_SIZE / 2, y + MARBLE_SIZE / 2,
        fill=palette.COLOR_SILVER,
        outline="",
    )

    if cell_state != BoardCellState.EMPTY:
        marble_color = MARBLE_COLORS[cell_state]
        render_marble(canvas, pos, color=marble_color, selected=is_cell_selected, focused=is_cell_focused)

def render_board(canvas, board, turn=None, player_marbles={}, selection=None, pos=(0, 0)):
    canvas.create_rectangle(0, 0, BOARD_WIDTH, BOARD_HEIGHT, fill="#fff")

    if turn and player_marbles:
        render_marble(
            canvas,
            pos=(BOARD_CELL_SIZE / 4, BOARD_CELL_SIZE / 4),
            color=MARBLE_COLORS[player_marbles[turn]],
            size=BOARD_CELL_SIZE / 4,
        )

    board_items = board.enumerate()
    if selection:
        board_items.sort(key=lambda x: x[0] == selection.head())

    for cell, cell_state in board_items:
        q, r = cell.astuple()
        q -= board.offset(r)
        x = (q * BOARD_CELL_SIZE
            + (BOARD_MAXCOLS - board.width(r) + 1) * BOARD_CELL_SIZE / 2
            + pos[0])
        y = (r * (BOARD_CELL_SIZE * 7 / 8)
            + BOARD_CELL_SIZE / 2
            + pos[1])
        render_board_cell(canvas, (x, y), cell, cell_state, selection)

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
        render_board(
            canvas=self._canvas,
            board=app.game_board,
            turn=app.game.turn,
            player_marbles=app.PLAYER_MARBLES,
            selection=app.selection,
        )
