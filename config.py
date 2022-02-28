from core.board_cell_state import BoardCellState
import colors.palette as palette
import colors.themes as themes

# general settings
APP_NAME = "Abalone"
FPS = 60
ENABLED_FPS_DISPLAY = False

# rules
BOARD_SIZE = 5
NUM_EJECTED_MARBLES_TO_WIN = 1

# display settings
BOARD_CELL_SIZE = 48
MARBLE_SIZE = BOARD_CELL_SIZE - 4
MARBLE_COLORS = themes.THEME_DEFAULT
ENABLED_LOW_QUALITY_MARBLES = False

# helpers
BOARD_MAXCOLS = BOARD_SIZE * 2 - 1
BOARD_WIDTH = BOARD_CELL_SIZE * BOARD_MAXCOLS
BOARD_HEIGHT = (BOARD_CELL_SIZE * 7 / 8) * BOARD_MAXCOLS + BOARD_CELL_SIZE / 8
