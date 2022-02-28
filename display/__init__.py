from math import sqrt
from dataclasses import dataclass
from tkinter import Tk, Canvas
from helpers.point_to_hex import point_to_hex
from core.game import Player, find_board_score, find_marbles_in_line
from core.board_cell_state import BoardCellState
from core.hex import Hex
from display.anims.tween import TweenAnim
from display.anims.hex_tween import HexTweenAnim
from helpers.easing_expo import ease_out, ease_in
import colors.palette as palette
from colors.transform import darken_color, lighten_color
from config import (
    BOARD_SIZE, BOARD_MAXCOLS,
    BOARD_CELL_SIZE,
    BOARD_WIDTH, BOARD_HEIGHT,
    MARBLE_SIZE, MARBLE_COLORS,
)

def hex_to_point(cell, board):
    q, r = cell.astuple()
    size = BOARD_CELL_SIZE / sqrt(3)
    x = size * (sqrt(3) * q + sqrt(3) / 2 * r) - size * 2.6
    y = size * (3 / 2 * r) + size
    # q -= board.offset(r)
    # x = (q * BOARD_CELL_SIZE
    #     + (BOARD_MAXCOLS - board.width(int(r)) + 1) * BOARD_CELL_SIZE / 2)
    # y = (r * (BOARD_CELL_SIZE * 7 / 8)
    #     + BOARD_CELL_SIZE / 2)
    return x, y

def render_marble(canvas, pos, color, size=MARBLE_SIZE, selected=False, focused=False):
    MARBLE_COLOR = darken_color(color) if selected else color

    marble_shape_ids = []
    x, y = pos
    s = size

    # marble body
    marble_shape_ids.append(canvas.create_oval(
        x - s / 2, y - s / 2,
        x + s / 2, y + s / 2,
        fill=MARBLE_COLOR,
        outline=darken_color(MARBLE_COLOR),
        width=2,
    ))

    # marble outline
    if focused:
        RING_WIDTH = 3
        RING_MARGIN = 2
        RING_SIZE = s / 2 + 2
        marble_shape_ids.append(canvas.create_oval(
            x - RING_SIZE - RING_WIDTH, y - RING_SIZE - RING_WIDTH,
            x + RING_SIZE + RING_MARGIN, y + RING_SIZE + RING_MARGIN,
            fill="",
            outline=lighten_color(color),
            width=RING_WIDTH,
        ))

    # marble highlights
    HIGHLIGHT_SIZE = s * 3 / 4
    HIGHLIGHT_X = x - HIGHLIGHT_SIZE / 2
    HIGHLIGHT_Y = y - HIGHLIGHT_SIZE / 2
    marble_shape_ids.append(canvas.create_oval(
        HIGHLIGHT_X, HIGHLIGHT_Y,
        HIGHLIGHT_X + HIGHLIGHT_SIZE, HIGHLIGHT_Y + HIGHLIGHT_SIZE,
        fill=lighten_color(MARBLE_COLOR),
        outline="",
    ))
    HIGHLIGHT_NEGATIVE_SIZE = HIGHLIGHT_SIZE + HIGHLIGHT_SIZE / 32
    marble_shape_ids.append(canvas.create_oval(
        x - s / 2 + s / 16, y - s / 2 + s / 16,
        x - s / 2 + s / 16 + HIGHLIGHT_NEGATIVE_SIZE, y - s / 2 + s / 16 + HIGHLIGHT_NEGATIVE_SIZE,
        fill=MARBLE_COLOR,
        outline="",
    ))
    marble_shape_ids.append(canvas.create_oval(
        x - s / 2 + s / 4, y - s / 32,
        x + s / 2 - s / 4, y - s / 32 + s / 3,
        fill=darken_color(MARBLE_COLOR),
        outline="",
    ))
    HIGHLIGHT_BALANCE_SIZE = HIGHLIGHT_SIZE / 3
    HIGHLIGHT_BALANCE_X = x - HIGHLIGHT_SIZE / 8
    HIGHLIGHT_BALANCE_Y = y - HIGHLIGHT_SIZE / 6
    marble_shape_ids.append(canvas.create_oval(
        HIGHLIGHT_BALANCE_X, HIGHLIGHT_BALANCE_Y,
        HIGHLIGHT_BALANCE_X + HIGHLIGHT_BALANCE_SIZE, HIGHLIGHT_BALANCE_Y + HIGHLIGHT_BALANCE_SIZE,
        fill=MARBLE_COLOR,
        outline="",
    ))

    # marble shine
    SHINE_X = x - s / 4
    SHINE_Y = y - s / 3
    SHINE_SIZE = s / 4
    marble_shape_ids.append(canvas.create_oval(
        SHINE_X, SHINE_Y,
        SHINE_X + SHINE_SIZE, SHINE_Y + SHINE_SIZE,
        fill=lighten_color(MARBLE_COLOR),
        outline="",
    ))

    # marble shine core
    SHINE_CORE_OFFSET = s / 24
    SHINE_CORE_X = SHINE_X + SHINE_CORE_OFFSET * 3 / 4
    SHINE_CORE_Y = SHINE_Y + SHINE_CORE_OFFSET * 3 / 4
    SHINE_CORE_SIZE = SHINE_SIZE - SHINE_CORE_OFFSET * 2
    marble_shape_ids.append(canvas.create_oval(
        SHINE_CORE_X, SHINE_CORE_Y,
        SHINE_CORE_X + SHINE_CORE_SIZE, SHINE_CORE_Y + SHINE_CORE_SIZE,
        fill=palette.COLOR_WHITE,
        outline="",
    ))

    # marble secondary shine
    SHINE_SECONDARY_X = x - s / 3
    SHINE_SECONDARY_Y = y - s / 8
    SHINE_SECONDARY_SIZE = s / 10
    marble_shape_ids.append(canvas.create_oval(
        SHINE_SECONDARY_X, SHINE_SECONDARY_Y,
        SHINE_SECONDARY_X + SHINE_SECONDARY_SIZE, SHINE_SECONDARY_Y + SHINE_SECONDARY_SIZE,
        fill=lighten_color(MARBLE_COLOR),
        outline="",
    ))

    return marble_shape_ids

def render_score(canvas, pos, score, color):
    x, y = pos
    MARBLE_SIZE = BOARD_CELL_SIZE / 4
    MARBLE_MARGIN = MARBLE_SIZE / 4
    for i in range(score):
        render_marble(
            canvas,
            pos=(x + i * (MARBLE_SIZE + MARBLE_MARGIN), y),
            color=color,
            size=MARBLE_SIZE
        )

class MarbleMoveAnim(HexTweenAnim):
    duration = 10

class MarbleShrinkAnim(TweenAnim):
    duration = 7

@dataclass
class Marble:
    cell: tuple[int, int]
    value: BoardCellState

class Display:

    def __init__(self, title):
        self._title = title
        self._window = None
        self._canvas = None
        self._marbles = []
        self._anims = []

    @property
    def anims(self):
        return self._anims

    def open(self, actions):
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

    def _update_anims(self):
        self._anims = [(a.update(), a)[-1] for a in self._anims if not a.done]

    def update(self):
        self._update_anims()
        self._window.update()

    def render(self, app):
        self._canvas.delete("all") # TODO: smart redrawing
        self._render_game(app)

    def _render_game(self, app):
        player_marble = app.PLAYER_MARBLES[app.game_turn]
        if player_marble:
            render_marble(
                canvas=self._canvas,
                pos=(BOARD_WIDTH - BOARD_CELL_SIZE / 4, BOARD_CELL_SIZE / 4),
                color=(palette.COLOR_GRAY
                    if app.game_over
                    else MARBLE_COLORS[player_marble]),
                size=BOARD_CELL_SIZE / 4,
            )

        # P1 score
        render_score(
            canvas=self._canvas,
            pos=(BOARD_CELL_SIZE / 4, BOARD_HEIGHT - BOARD_CELL_SIZE / 4),
            score=find_board_score(app.game_board, app.PLAYER_MARBLES[Player.ONE]),
            color=MARBLE_COLORS[app.PLAYER_MARBLES[Player.TWO]]
        )

        # P2 score
        render_score(
            canvas=self._canvas,
            pos=(BOARD_CELL_SIZE / 4, BOARD_CELL_SIZE / 4),
            score=find_board_score(app.game_board, app.PLAYER_MARBLES[Player.TWO]),
            color=MARBLE_COLORS[app.PLAYER_MARBLES[Player.ONE]]
        )

        self._render_board(app)

    def _render_board(self, app):
        board_items = app.game_board.enumerate()
        if app.selection:
            board_items = sorted(board_items, key=lambda x: x[0] == app.selection.head())

        marbles = []
        for cell, cell_state in board_items:
            x, y = hex_to_point(cell, app.game_board)
            self._canvas.create_oval(
                x - MARBLE_SIZE / 2, y - MARBLE_SIZE / 2,
                x + MARBLE_SIZE / 2, y + MARBLE_SIZE / 2,
                fill=palette.COLOR_SILVER,
                outline="",
            )
            if not self._marbles and cell_state != BoardCellState.EMPTY:
                marbles.append(Marble(cell, value=cell_state))

        if marbles:
            self._marbles = marbles

        for marble in self._marbles:
            marble_cell = marble.cell
            marble_size = MARBLE_SIZE

            marble_anims = [a for a in self._anims if a.target is marble]
            for marble_anim in marble_anims:
                if isinstance(marble_anim, MarbleMoveAnim):
                    marble_cell = marble_anim.cell
                elif isinstance(marble_anim, MarbleShrinkAnim):
                    marble_size *= 1 - marble_anim.pos

            is_cell_selected = app.selection and app.selection.pieces() and marble_cell in app.selection.pieces()
            is_cell_focused = app.selection and marble_cell == app.selection.head()
            render_marble(
                canvas=self._canvas,
                pos=hex_to_point(marble_cell, app.game_board),
                size=marble_size,
                color=(palette.COLOR_GRAY
                    if (app.game_over
                        and marble.value == app.PLAYER_MARBLES[app.game_turn])
                    else MARBLE_COLORS[marble.value]),
                selected=is_cell_selected,
                focused=is_cell_focused,
            )

    def _find_marble_by_cell(self, cell):
        return next((m for m in self._marbles if m.cell == cell), None)

    def perform_move(self, move, board):
        move_cells = list(move.pieces())
        move_target = move.target_cell()
        if board[move_target] != BoardCellState:
            move_cells += find_marbles_in_line(board, move_target, move.direction)

        marble_cells = [(marble, c) for c in move_cells if (marble := self._find_marble_by_cell(c))]
        for marble, cell in marble_cells:
            marble.cell = Hex.add(cell, move.direction.value)
            self._anims.append(MarbleMoveAnim(
                target=marble,
                easing=ease_out,
                src=cell,
                dest=marble.cell,
            ))
            if marble.cell not in board:
                self._anims.append(MarbleShrinkAnim(
                    target=marble,
                    easing=ease_in,
                    delay=MarbleMoveAnim.duration,
                    on_end=lambda: self._marbles.remove(marble)
                ))
