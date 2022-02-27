from core.board_cell_state import BoardCellState
import colors.palette as palette

THEME_DEFAULT = {
    BoardCellState.WHITE: palette.COLOR_BLUE,
    BoardCellState.BLACK: palette.COLOR_RED,
}

THEME_MONOCHROME = {
    BoardCellState.WHITE: palette.COLOR_SILVER,
    BoardCellState.BLACK: palette.COLOR_CHARCOAL,
}
