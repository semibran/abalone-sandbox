from display.marble import render_marble
from config import BOARD_CELL_SIZE

def render_score(canvas, pos, score, color):
    object_ids = []
    x, y = pos
    MARBLE_SIZE = BOARD_CELL_SIZE / 4
    MARBLE_MARGIN = MARBLE_SIZE / 4
    for i in range(score):
        object_ids += render_marble(
            canvas,
            pos=(x + i * (MARBLE_SIZE + MARBLE_MARGIN), y),
            color=color,
            size=MARBLE_SIZE
        )
    return object_ids
