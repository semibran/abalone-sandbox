from math import sqrt
from helpers.axial_round import axial_round

def point_to_hex(point, radius):
    x, y = point
    q = (sqrt(3) / 3 * x - 1 / 3 * y) / radius
    r = (2 / 3 * y) / radius
    return axial_round(q, r)
