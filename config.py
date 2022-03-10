# general settings
APP_NAME = "Abalone"
FPS = 60
ENABLED_FPS_DISPLAY = False
AGENT_MAX_SEARCH_SECS = 5
AGENT_SEC_THRESHOLD = -0.02

# rules
BOARD_SIZE = 5
MAX_MOVABLE_MARBLES = 3
NUM_EJECTED_MARBLES_TO_WIN = 6

# display settings
BOARD_CELL_SIZE = 32
MARBLE_SIZE = BOARD_CELL_SIZE - 4
ENABLED_LOW_QUALITY_MARBLES = False

# helpers
BOARD_MAXCOLS = BOARD_SIZE * 2 - 1
BOARD_WIDTH = BOARD_CELL_SIZE * BOARD_MAXCOLS
BOARD_HEIGHT = (BOARD_CELL_SIZE * 7 / 8) * BOARD_MAXCOLS + BOARD_CELL_SIZE / 8
