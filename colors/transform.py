import colors.palette as palette

COLORMAP_DARKEN = {
    palette.COLOR_BLUE: palette.COLOR_DARKBLUE,
    palette.COLOR_LIGHTBLUE: palette.COLOR_BLUE,
    palette.COLOR_DARKBLUE: palette.COLOR_BLACK,
    palette.COLOR_RED: palette.COLOR_DARKRED,
    palette.COLOR_LIGHTRED: palette.COLOR_RED,
    palette.COLOR_DARKRED: palette.COLOR_BLACK,
}

COLORMAP_LIGHTEN = {
    palette.COLOR_BLUE: palette.COLOR_LIGHTBLUE,
    palette.COLOR_DARKBLUE: palette.COLOR_BLUE,
    palette.COLOR_RED: palette.COLOR_LIGHTRED,
    palette.COLOR_DARKRED: palette.COLOR_RED,
}

def darken_color(color):
    return (COLORMAP_DARKEN[color]
        if color in COLORMAP_DARKEN
        else color)

def lighten_color(color):
    return (COLORMAP_LIGHTEN[color]
        if color in COLORMAP_LIGHTEN
        else color)
