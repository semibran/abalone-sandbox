from core.board_cell_state import BoardCellState
import colors.palette as palette
import colors.themes as themes

APP_NAME = "Abalone"
FPS = 60

BOARD_SIZE = 5
BOARD_MAXCOLS = BOARD_SIZE * 2 - 1
BOARD_CELL_SIZE = 48
BOARD_WIDTH = BOARD_CELL_SIZE * BOARD_MAXCOLS
BOARD_HEIGHT = (BOARD_CELL_SIZE * 7 / 8) * BOARD_MAXCOLS + BOARD_CELL_SIZE / 8
MARBLE_SIZE = BOARD_CELL_SIZE - 4
MARBLE_COLORS = themes.THEME_DEFAULT
