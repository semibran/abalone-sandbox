from math import sqrt
from dataclasses import dataclass
from tkinter import Tk, Canvas
from helpers.point_to_hex import point_to_hex
from helpers.hex_to_point import hex_to_point
from core.game import Player, find_board_score, find_marbles_in_line
from core.board_cell_state import BoardCellState
from core.hex import Hex
from display.anims.tween import TweenAnim
from display.anims.hex_tween import HexTweenAnim
from display.marble import render_marble
from helpers.easing_expo import ease_out, ease_in
import colors.palette as palette
from config import (
    BOARD_SIZE, BOARD_MAXCOLS,
    BOARD_CELL_SIZE,
    BOARD_WIDTH, BOARD_HEIGHT,
    MARBLE_SIZE, MARBLE_COLORS,
)

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
            x, y = hex_to_point(cell, BOARD_CELL_SIZE / 2)
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
                pos=hex_to_point(marble_cell, BOARD_CELL_SIZE / 2),
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
