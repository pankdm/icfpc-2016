#from origami import *

from sympy.geometry import *
from fractions import Fraction
from sympy import Matrix, diag

from pyth import get_random_angles
import time


import pylab

DEBUG = False
DRAW = False

def get_shift_transform(dx, dy):
  return Matrix([
    [1, 0, dx],
    [0, 1, dy],
    [0, 0, 1]])

def get_refl_transform(nx, ny):
  if DEBUG:
    print "Transforming normal:"
    print nx, ny
  nss = nx**2 + ny**2

  v = Matrix([[nx, ny]]).T
  H2 = diag(1,1) - 2*v*v.T / nss

  H3 = diag(1,1,1)
  H3[0:2,0:2] = H2

  return H3

def draw_polygon(fig, f, ls='-', lw=5):
  num_sides = len(f)
  for i in range(0, len(f) - 1):
    x1, y1 = f[i].x, f[i].y
    x2, y2 = f[i + 1].x, f[i + 1].y
    fig.plot([x1, x2], [y1, y2], linestyle=ls, lw=lw)
  x1, y1 = f[len(f) - 1].x, f[len(f) - 1].y
  x2, y2 = f[0].x, f[0].y
  fig.plot([x1, x2], [y1, y2], linestyle=ls, lw=lw)

def draw_side_by_side(p1s, p2s):
  fig = pylab.figure()
  fig_1 = fig.add_subplot(2,1,1, aspect=1)
  fig_2 = fig.add_subplot(2,1,2, aspect=1)

  for p1 in p1s:
    draw_polygon(fig_1, p1)

  fig_1.plot([-0.05], [-0.05])
  fig_1.plot([1.05], [1.05])

  for p2 in p2s:
    draw_polygon(fig_2, p2)

  pylab.savefig('debug-img/{}.png'.format(time.time()))
  pylab.show()


def bend(pts, facets):
  edges = {}
  for f in range(0, len(facets)):
    edges[f] = []
    vertices = facets[f]
    for v in range(0, len(vertices) - 1):
      edges[f].append([vertices[v], vertices[v + 1]])
    edges[f].append([vertices[len(vertices) - 1], vertices[0]])

  if DEBUG:
    print "Edges:"
    print edges



  def edges_eq(e1, e2):
    if e1 == e2 or (e1[0] == e2[1] and e1[1] == e2[0]):
      return True
    return False

  def common_edge(f1, f2):
    for e1 in edges[f1]:
      for e2 in edges[f2]:
        if edges_eq(e1, e2):
          return e1
    return None

  neighbours = {}
  for f1 in range(0, len(facets)):
    neighbours[f1] = []
    for f2 in range(0, len(facets)):
      if f2 == f1:
        continue
      if common_edge(f1, f2):
        neighbours[f1].append(f2)

  def transform_point(ptr, T):
    p = pts[ptr]
    v = Matrix([[p.x],
                [p.y],
                [1]])
    u = T * v
    return Point(u[0,0], u[1,0])

  def transform_point_2d(p, T):
    v = Matrix([[p.x],
                [p.y],
                [1]])
    u = T * v
    return Point(u[0,0], u[1,0])

  def transform_facet(f, T):
    new_facet = []
    for p in facets[f]:
      new_facet.append(transform_point(p, T))
    return new_facet


  if DEBUG:
    print "Neighbours:"
    print neighbours

  to_process = []
  for f in neighbours[0]:
    to_process.append([f, common_edge(0, f), diag(1, 1, 1)])
  processed = {0: diag(1, 1, 1)}


  while len(to_process) > 0:
    if DRAW:
      draw_side_by_side([[pts[p] for p in f] for f in facets], [transform_facet(f, processed[f]) for f in processed])
      #draw_side_by_side([], [transform_facet(f, processed[f]) for f in processed])
    curr = to_process.pop(0)
    print "Facet # " + str(curr)
    curr_n = neighbours[curr[0]]
    curr_t = curr[2]

    curr_e = [transform_point_2d(pts[curr[1][0]], curr_t),
                transform_point_2d(pts[curr[1][1]], curr_t)
    ]
    curr_t = get_shift_transform(-curr_e[0].x, -curr_e[0].y) * curr_t
    curr_t = get_refl_transform(
        -(curr_e[1].y - curr_e[0].y),
         (curr_e[1].x - curr_e[0].x)
        ) * curr_t
    curr_t = get_shift_transform(curr_e[0].x, curr_e[0].y) * curr_t
    if DEBUG:
      print "Curr:"
      print curr[0]
      print facets[curr[0]]
      print "Common edge with parent:"
      print curr[1]
      print "Parent matrix:"
      print curr[2]
      print "Curr matrix:"
      print curr_t
      print "Neighbours:"
      print curr_n
    for f in curr_n:
      if f not in processed:
        to_process.append([f, common_edge(curr[0], f), curr_t])
    processed[curr[0]] = curr_t

  if DEBUG:
    print "Processed:"
    print processed

  # if DRAW:
  # draw_side_by_side([[pts[p] for p in f] for f in facets], [transform_facet(f, processed[f]) for f in processed])
  f_i = 14
  draw_side_by_side([[pts[p] for p in f] for f in facets], [transform_facet(f_i, processed[f_i])] )


  solution = {}
  for f in range(0, len(facets)):
    for p in facets[f]:
      solution[p] = transform_point(p, processed[f])

  print len(pts)
  for p in pts:
    print '{},{}'.format(p.x, p.y)
  print len(facets)
  for f in facets:
    facet_str = str(len(f))
    facet_str += ' ' + ' '.join(map(str, f))
    # for p in f:
    #   facet_str += str(p) + ","
    # facet_str = facet_str[:-1]
    print facet_str

  alpha, beta = get_random_angles()
  index = 0
  for p in solution:
    # x0, y0 = solution[p].x, solution[p].y
    # x = alpha * x0 + beta * y0 - 1
    # y = -beta * x0 + alpha * y0 - 2
    # print "{},{}".format(x, y)

    x = solution[p].x
    y = solution[p].y
    # if p == 3:
    #     y = Fraction(1, 5)

    print index, "{},{}".format(x, y)
    # print "{},{}".format(x, y)

    index += 1



# _____________________________________________________

'''pts = [
  Point(Fraction(0), Fraction(0)),
  Point(Fraction(0), Fraction(1)),
  Point(Fraction(1), Fraction(1)),
  Point(Fraction(1), Fraction(0)),
  Point(Fraction(1,2), Fraction(1,2)),
]
facets = [
  [0,1,4],
  [1,2,4],
  [2,3,4],
  [3,0,4],
]'''


def line_cat(h):
    half = Fraction(1, 2)
    a = get_a(h)

    y = 1 - (1 - 2 * h) / 2

    pts = [
      Point(Fraction(0), Fraction(0)),
      Point(Fraction(0), Fraction(1,2)),
      Point(Fraction(0), Fraction(1)),
      Point(Fraction(1), Fraction(1)),
      Point(Fraction(1), Fraction(1,2)),
      Point(Fraction(1), Fraction(0)),
      Point(half + a, Fraction(0)),
      Point(half - a, Fraction(0)),
      Point(half, h),

      Point(Fraction(0), y),
      Point(Fraction(1), y),
    ]

    facets = [
      [1,9,10,4,8],
      [0,1,8,7],
      [7,8,6],
      [8,4,5,6],
      [9,2,3,10]
    ]
    return pts, facets

def get_a(h):
    a = h - 2 * h * h
    print 'a = {}, h = {}'.format(a, h)
    return a

def symmetric_cat(h1, h2):
    half = Fraction(1, 2)
    a1 = get_a(h1)
    a2 = get_a(h2)

    pts = [
      Point(Fraction(0), Fraction(0)),
      Point(Fraction(0), Fraction(1,2)),
      Point(Fraction(0), Fraction(1)),
      Point(Fraction(1), Fraction(1)),
      Point(Fraction(1), Fraction(1,2)),
      Point(Fraction(1), Fraction(0)),
      Point(half + a1, Fraction(0)), # 6
      Point(half - a1 , Fraction(0)), # 7
      Point(half, h1), # 8

      Point(half - a2, Fraction(1)), # 9
      Point(half + a2, Fraction(1)), # 10
      Point(half, Fraction(1) - h2), # 11

    #   Point(Fraction(0), Fraction(5,6)),
    #   Point(Fraction(1), Fraction(5,6)),
    ]

    facets = [
    #   [1, 2, 3, 4, 8],
    #   [1,9,10,4,8],
      [1, 11, 4, 8],
      [0,1,8,7],
      [7,8,6],
      [8,4,5,6],
      [1, 2, 9, 11],
      [9, 11, 10],
      [11, 10, 3, 4],
    #   [9,2,3,10]
    ]
    return pts, facets

def folded_cat(h1, h2):
    half = Fraction(1, 2)
    a1 = get_a(h1)
    a2 = get_a(h2)

    pts = [
      Point(Fraction(0), Fraction(0)),
      Point(Fraction(0), Fraction(1,2)),
      Point(Fraction(0), Fraction(1)),
      Point(Fraction(1), Fraction(1)),
      Point(Fraction(1), Fraction(1,2)),
      Point(Fraction(1), Fraction(0)),
      Point(half + a1, Fraction(0)), # 6
      Point(half - a1 , Fraction(0)), # 7
      Point(half, h1), # 8

      Point(half - a2, Fraction(1)), # 9
      Point(half + a2, Fraction(1)), # 10
      Point(half, Fraction(1) - h2), # 11

    #   Point(Fraction(0), Fraction(5,6)),
    #   Point(Fraction(1), Fraction(5,6)),
    ]

    facets = [
    #   [1, 2, 3, 4, 8],
    #   [1,9,10,4,8],
      [1, 11, 4, 8],
      [0,1,8,7],
      [7,8,6],
      [8,4,5,6],
      [1, 2, 9, 11],
      [9, 11, 10],
      [11, 10, 3, 4],
    #   [9,2,3,10]
    ]
    return pts, facets


def letter_n():
    old_pts = [
        Point(Fraction(0), Fraction(0)), #0
        Point(Fraction(1), Fraction(0)), #1
        Point(Fraction(4), Fraction(0)), #2
        Point(Fraction(5), Fraction(0)), #3
        Point(Fraction(0), Fraction(1)), #4
        Point(Fraction(1), Fraction(1)), #5
        Point(Fraction(2), Fraction(1)), #6
        Point(Fraction(3), Fraction(1)), #7
        Point(Fraction(4), Fraction(1)), #8
        Point(Fraction(5), Fraction(1)), #9
        Point(Fraction(1), Fraction(2)), #10
        Point(Fraction(4), Fraction(2)), #11
        Point(Fraction(1), Fraction(3)), #12
        Point(Fraction(4), Fraction(3)), #13
        Point(Fraction(0), Fraction(4)), #14
        Point(Fraction(1), Fraction(4)), #15
        Point(Fraction(2), Fraction(4)), #16
        Point(Fraction(3), Fraction(4)), #17
        Point(Fraction(4), Fraction(4)), #18
        Point(Fraction(5), Fraction(4)), #19
        Point(Fraction(0), Fraction(5)), #20
        Point(Fraction(1), Fraction(5)), #21
        Point(Fraction(4), Fraction(5)), #22
        Point(Fraction(5), Fraction(5)), #23
    ]

    pts = []
    for p in old_pts:
        pts.append(Point(p.x / 5, p.y / 5))

    facets = [
        [10, 11, 13, 12], #1
        [0, 1, 5, 4], #2
        [1, 6, 5], #3
        [1, 2, 7, 6],#4
        [2, 8, 7], #5
        [2, 3, 9, 8], #6
        [4, 10, 12, 14], #7
        [4, 5, 10], #8
        [5, 6, 10], #9
        [6, 7, 11, 10], #10
        [7, 8, 11], #11
        [11, 8, 9], #12
        [11, 9, 19, 13], #13
        [14, 12, 15], # 14
        [12, 16, 15], # 15
        [12, 13, 17, 16], # 16
        [17, 13, 18],
        [13, 19, 18],
        [14, 15, 21, 20],
        [15, 16, 21],
        [16, 17, 22, 21],
        [17, 18, 22],
        [18, 19, 23, 22],
    ]
    return pts, facets


if __name__ == "__main__":
    h = Fraction(1, 7)
    h1 = Fraction(1, 3)
    h2 = Fraction(4, 9)

    # h1 = Fraction(50, 113)
    # h2 = Fraction(7, 19)
    # pts, facets = symmetric_cat(h1, h2)
    pts, facets = letter_n()

    # pts, facets = line_cat(h2)

    print
    print '=' * 80
    bend(pts, facets)
    # print "{}/{},{}/{}".format()
    # print "{}/{},{}/{}".format()
    # print "{}/{},{}/{}".format()
    # print "{}/{},{}/{}".format()
    # print "{}/{},{}/{}".format()
    # print "{}/{},{}/{}".format()
    # print "{}/{},{}/{}".format()
    # print "{}/{},{}/{}".format()
    # print "{}/{},{}/{}".format()
    # print "{}/{},{}/{}".format()
    # print "{}/{},{}/{}".format()
    # print "{}/{},{}/{}".format()
    # print "{}/{},{}/{}".format()
    # print "{}/{},{}/{}".format()
    # print "{}/{},{}/{}".format()
    # print "{}/{},{}/{}".format()
    # print "{}/{},{}/{}".format()
    # print "{}/{},{}/{}".format()
    # print "{}/{},{}/{}".format()
    # print "{}/{},{}/{}".format()
    # print "{}/{},{}/{}".format()
    # print "{}/{},{}/{}".format()
    # print "{}/{},{}/{}".format()
    # print "{}/{},{}/{}".format()
