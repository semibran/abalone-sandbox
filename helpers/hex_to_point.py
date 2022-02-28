from math import sqrt

def hex_to_point(cell, radius):
    q, r = cell.astuple()
    size = radius * 2 / sqrt(3)
    x = size * (sqrt(3) * q + sqrt(3) / 2 * r - 2.6)
    y = size * (3 / 2 * r + 1)
    return x, y
