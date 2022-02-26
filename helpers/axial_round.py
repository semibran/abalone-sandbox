def axial_round(x, y):
  xgrid = round(x)
  ygrid = round(y)
  x -= xgrid
  y -= ygrid
  dx = round(x + 0.5 * y) * (x * x >= y * y)
  dy = round(y + 0.5 * x) * (x * x < y * y)
  return (xgrid + dx, ygrid + dy)
