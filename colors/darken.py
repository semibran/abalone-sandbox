import colors.palette as palette

COLORMAP_DARKEN = {
    palette.COLOR_BLUE: palette.COLOR_DARKBLUE,
    palette.COLOR_RED: palette.COLOR_DARKRED,
}

def darken_color(color):
    return (COLORMAP_DARKEN[color]
        if color in COLORMAP_DARKEN
        else None)
