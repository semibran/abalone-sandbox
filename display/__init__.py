from math import sqrt
from dataclasses import dataclass, field
from tkinter import Tk, Canvas
from helpers.point_to_hex import point_to_hex
from helpers.hex_to_point import hex_to_point
from core.game import Player, find_board_score, find_marbles_in_line
from core.board_cell_state import BoardCellState
from core.hex import Hex
from display.anims.tween import TweenAnim
from display.anims.hex_tween import HexTweenAnim
from display.marble import render_marble
from display.score import render_score
from helpers.easing_expo import ease_out, ease_in
import colors.palette as palette
from config import (
    BOARD_SIZE, BOARD_MAXCOLS,
    BOARD_CELL_SIZE,
    BOARD_WIDTH, BOARD_HEIGHT,
    MARBLE_SIZE, MARBLE_COLORS,
)

class MarbleMoveAnim(HexTweenAnim):
    duration = 10

class MarbleShrinkAnim(TweenAnim):
    duration = 7

@dataclass
class Marble:
    cell: tuple[int, int]
    pos: tuple[float, float]
    kind: BoardCellState
    object_ids: list = field(default_factory=list)
    selected: bool = False
    focused: bool = False
    faded: bool = False

class Display:

    def __init__(self, title):
        self._title = title
        self._window = None
        self._canvas = None
        self._marbles = []
        self._anims = []
        self._ids_turn_indicator = []
        self._ids_scores = []

    @property
    def is_animating(self):
        return next((a for a in self._anims if not a.done), None)

    def open(self, on_click):
        self._window = Tk()
        self._window.title(self._title)

        self._canvas = Canvas(self._window, width=BOARD_WIDTH, height=BOARD_HEIGHT, highlightthickness=0)
        self._canvas.pack()
        self._canvas.bind("<Button-1>", lambda event: (
            rw := BOARD_CELL_SIZE / 2,
            rh := BOARD_CELL_SIZE / sqrt(3),
            x := event.x - rw - (BOARD_MAXCOLS - BOARD_SIZE) * rw,
            y := event.y - rw,
            on_click(Hex(*point_to_hex((x, y), rh)))
        ))

    def clear(self):
        self._delete_marbles()
        self._clear_hud()

    def update(self):
        self._update_anims()
        self._window.update()

    def update_hud(self, app):
        self._update_turn_indicator(app)
        self._update_scores(app)

    def _clear_hud(self):
        self._clear_turn_indicator()
        self._clear_scores()

    def _update_turn_indicator(self, app):
        self._clear_turn_indicator()
        self._render_turn_indicator(
            player_unit=app.PLAYER_MARBLES[app.game_turn],
            game_over=app.game_over,
        )

    def _clear_turn_indicator(self):
        for object_id in self._ids_turn_indicator:
            self._canvas.delete(object_id)
        self._ids_turn_indicator.clear()

    def _update_scores(self, app):
        self._clear_scores()
        self._render_scores(app)

    def _clear_scores(self):
        for object_id in self._ids_scores:
            self._canvas.delete(object_id)
        self._ids_scores.clear()

    def _update_anims(self):
        self._anims = [(a.update(), a)[-1] for a in self._anims if not a.done]

    def _update_board(self, app):
        for marble in self._marbles:
            is_marble_selected = bool(app.selection and marble.cell in app.selection.pieces())
            is_marble_focused = bool(app.selection and marble.cell == app.selection.head())
            is_marble_faded = app.game_over and marble.kind != app.PLAYER_MARBLES[app.game_winner]
            if (marble.selected != is_marble_selected
            or marble.focused != is_marble_focused
            or marble.faded != is_marble_faded):
                self._clear_marble(marble)
                marble.selected = is_marble_selected
                marble.focused = is_marble_focused
                marble.faded = is_marble_faded
                marble.object_ids = self._render_marble(app, marble.pos, marble.cell, marble.kind)

            marble_anims = [a for a in self._anims if a.target is marble]
            if marble_anims:
                self._update_marble(
                    marble,
                    anims=marble_anims,
                )

    def _update_marble(self, marble, anims):
        marble_size = MARBLE_SIZE
        marble_cell = marble.cell

        for marble_anim in anims:
            if isinstance(marble_anim, MarbleShrinkAnim):
                marble_size *= 1 - marble_anim.pos
            elif isinstance(marble_anim, MarbleMoveAnim):
                marble_cell = marble_anim.cell

        marble_pos = hex_to_point(marble_cell, BOARD_CELL_SIZE / 2)
        for object_id in marble.object_ids:
            if marble_size != MARBLE_SIZE:
                marble_scale = marble_size / MARBLE_SIZE
                self._canvas.scale(object_id, *marble_pos, marble_scale, marble_scale)

            old_x, old_y = marble.pos
            new_x, new_y = marble_pos
            delta = (new_x - old_x, new_y - old_y)
            if delta != (0, 0):
                self._canvas.move(object_id, *delta)

        marble.pos = marble_pos

    def _clear_marble(self, marble):
        for object_id in marble.object_ids:
            self._canvas.delete(object_id)
        marble.object_ids.clear()

    def _delete_marble(self, marble):
        self._clear_marble(marble)
        self._marbles.remove(marble)

    def _delete_marbles(self):
        for marble in self._marbles:
            self._clear_marble(marble)
        self._marbles.clear()

    def render(self, app):
        if self._marbles:
            self._update_board(app)
        else:
            self._render_game(app)

    def _render_turn_indicator(self, player_unit, game_over=False):
        self._ids_turn_indicator += render_marble(
            canvas=self._canvas,
            pos=(BOARD_WIDTH - BOARD_CELL_SIZE / 4, BOARD_CELL_SIZE / 4),
            color=(palette.COLOR_GRAY
                if game_over
                else MARBLE_COLORS[player_unit]),
            size=BOARD_CELL_SIZE / 4,
        )

    def _render_scores(self, app):
        # P1 score
        self._ids_scores += render_score(
            canvas=self._canvas,
            pos=(BOARD_CELL_SIZE / 4, BOARD_HEIGHT - BOARD_CELL_SIZE / 4),
            score=find_board_score(app.game_board, app.PLAYER_MARBLES[Player.ONE]),
            color=MARBLE_COLORS[app.PLAYER_MARBLES[Player.TWO]]
        )

        # P2 score
        self._ids_scores += render_score(
            canvas=self._canvas,
            pos=(BOARD_CELL_SIZE / 4, BOARD_CELL_SIZE / 4),
            score=find_board_score(app.game_board, app.PLAYER_MARBLES[Player.TWO]),
            color=MARBLE_COLORS[app.PLAYER_MARBLES[Player.ONE]]
        )

    def _render_game(self, app):
        self._render_turn_indicator(
            player_unit=app.PLAYER_MARBLES[app.game_turn],
            game_over=app.game_over,
        )
        self._render_scores(app)
        self._render_board(app)

    def _render_board(self, app):
        board_items = app.game_board.enumerate()
        if app.selection:
            board_items = sorted(board_items, key=lambda x: x[0] == app.selection.head())

        marble_items = []
        for cell, cell_state in board_items:
            x, y = hex_to_point(cell, BOARD_CELL_SIZE / 2)
            self._canvas.create_oval(
                x - MARBLE_SIZE / 2, y - MARBLE_SIZE / 2,
                x + MARBLE_SIZE / 2, y + MARBLE_SIZE / 2,
                fill=palette.COLOR_SILVER,
                outline="",
            )
            if not self._marbles and cell_state != BoardCellState.EMPTY:
                marble_items.append((cell, cell_state))

        for marble_cell, marble_kind in marble_items:
            marble_pos = hex_to_point(marble_cell, BOARD_CELL_SIZE / 2)
            self._marbles.append(Marble(
                pos=marble_pos,
                cell=marble_cell,
                kind=marble_kind,
                object_ids=self._render_marble(app, marble_pos, marble_cell, marble_kind)
            ))

    def _render_marble(self, app, pos, cell, kind):
        return render_marble(
            canvas=self._canvas,
            pos=pos,
            size=MARBLE_SIZE,
            color=(palette.COLOR_GRAY
                if (app.game_over
                    and kind != app.PLAYER_MARBLES[app.game_winner])
                else MARBLE_COLORS[kind]),
            selected=(app.selection and app.selection.pieces()
                and cell in app.selection.pieces()),
            focused=app.selection and cell == app.selection.head(),
        )

    def _find_marble_by_cell(self, cell):
        return next((m for m in self._marbles if m.cell == cell), None)

    def perform_move(self, move, board, on_end=None):
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
                on_end=on_end,
            ))
            if marble.cell not in board:
                self._anims.append(MarbleShrinkAnim(
                    target=marble,
                    easing=ease_in,
                    delay=MarbleMoveAnim.duration,
                    on_end=lambda: self._delete_marble(marble)
                ))
