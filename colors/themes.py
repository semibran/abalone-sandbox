from core.board_cell_state import BoardCellState
import colors.palette as palette

THEME_DEFAULT = {
    BoardCellState.WHITE: palette.COLOR_BLUE,
    BoardCellState.BLACK: palette.COLOR_RED,
    "background": palette.COLOR_WHITE,
    "board_cell": palette.COLOR_SILVER,
}

THEME_MONOCHROME = {
    BoardCellState.WHITE: palette.COLOR_SILVER,
    BoardCellState.BLACK: palette.COLOR_CHARCOAL,
    "background": palette.COLOR_BROWN,
    "board_cell": palette.COLOR_SAND,
}

THEME_DARK = {
    BoardCellState.WHITE: palette.COLOR_TURQUOISE,
    BoardCellState.BLACK: palette.COLOR_PURPLE,
    "background": palette.COLOR_DARKGRAY,
    "board_cell": palette.COLOR_CHARCOAL,
}
