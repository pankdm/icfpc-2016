
from ship import Ship
import matplotlib.pyplot as plt
import pylab
from sympy import Point, Polygon, pi


def draw_polygon(fig, ps):
    num_sides = len(ps.sides)
    for side in ps.sides:
        x1, y1 = side.p1
        x2, y2 = side.p2
        fig.plot([x1, x2], [y1, y2], linestyle='-', lw=10)


def draw_side_by_side(p1s, p2s):
    fig = pylab.figure()
    fig_1 = fig.add_subplot(2,1,1)
    fig_2 = fig.add_subplot(2,1,2)

    for p1 in p1s:
        draw_polygon(fig_1, p1)

    for p2 in p2s:
        draw_polygon(fig_2, p2)

    pylab.show()


if __name__ == "__main__":
    p1, p2, p3, p4, p5 = [(0, 0), (0.2, 0), (1, 1), (0, 1), (0.6, 0)]
    p1s = Polygon(p1, p2, p3, p4)
    p2s = Polygon(p1, p5, p3, p4)
    draw_side_by_side([p1s], [p2s])
