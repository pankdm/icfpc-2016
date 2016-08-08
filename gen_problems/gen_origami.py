import re
from sympy import Matrix, diag
from sympy.geometry import *
from fractions import Fraction

import matplotlib.pyplot as plt
import pylab

from sgibatel2 import get_cat_facets

import random

#from read_input import silhouette_pts

pts = dict()
def mkpt(p):
  if p not in pts:
    n = len(pts)
    pts[p] = n
  return p



def get_shift_transform(dx, dy):
  return Matrix([
    [1, 0, dx],
    [0, 1, dy],
    [0, 0, 1]])

def get_refl_transform(nx, ny):
  nss = nx**2 + ny**2

  v = Matrix([[nx, ny]]).T
  H2 = diag(1,1) - 2*v*v.T / nss

  H3 = diag(1,1,1)
  H3[0:2,0:2] = H2

  return H3


def transform_point(p, A):
  v = Matrix([  [p.x],
                [p.y],
                [1]  ])
  u = A*v
  return Point(u[0,0], u[1,0])



def transform_facet(facet, A):
  if isinstance(facet, Point):
    return transform_point(facet, A)

  new_facet = []
  for p in facet.vertices:
    new_facet.append(transform_point(p, A))
  return Polygon(*new_facet)


def fold_facet_by_line(facet_pair, tr_segment_pair):
  facet, mat = facet_pair
  inv_mat = mat ** -1

  segment_pair = (
      transform_point(tr_segment_pair[0], inv_mat),
      transform_point(tr_segment_pair[1], inv_mat))

  new_pts = [x for x in intersection(facet, Line(*segment_pair)) if isinstance(x,Point)]
  for p in new_pts:
    mkpt(p)

  facet_left = []
  facet_right = []
  for p in set(list(facet.vertices) + new_pts):
    p = transform_point(p, mat)
    dx1, dy1 = (
        tr_segment_pair[1].x - tr_segment_pair[0].x,
        tr_segment_pair[1].y - tr_segment_pair[0].y)
    dx2, dy2 = (
        p.x - tr_segment_pair[0].x,
        p.y - tr_segment_pair[0].y)

    sgn = dx1*dy2 - dx2*dy1

    if sgn <= 0:
      facet_right.append(transform_point(p, inv_mat))
    if sgn >= 0:
      facet_left.append(transform_point(p, inv_mat))

  facet_left = convex_hull(*facet_left) if len(facet_left)>0 else None
  facet_right = convex_hull(*facet_right) if len(facet_right)>0 else None

  T = get_shift_transform(
        -tr_segment_pair[0].x,
        -tr_segment_pair[0].y)

  T = get_refl_transform(
        -(tr_segment_pair[1].y - tr_segment_pair[0].y),
         (tr_segment_pair[1].x - tr_segment_pair[0].x)
      ) * T

  T = get_shift_transform(
        +tr_segment_pair[0].x,
        +tr_segment_pair[0].y
      ) * T

  return [f for f in [(facet_left, T*mat), (facet_right, mat)]
      if isinstance(f[0], Polygon) and f[0].area != 0]


def fold_all_facets_by_line(facet_pairs, tr_segment):
  new_facet_pairs = []
  for facet_pair in facet_pairs:
    new_facet_pairs.extend(
        fold_facet_by_line(facet_pair, tr_segment))
  return new_facet_pairs



def draw_polygon(fig, ps, ls='-', lw=2):
  num_sides = len(ps.sides)
  for side in ps.sides:
    x1, y1 = side.p1.x, side.p1.y
    x2, y2 = side.p2.x, side.p2.y
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

  #draw_polygon(fig_2, goal, ls=':', lw=3)

  pylab.show()


def solve_convex(goal, facet_pairs):
  if draw:
    draw_side_by_side(
        [f[0] for f in facet_pairs],
        [transform_facet(f[0], f[1]) for f in facet_pairs],
    )

  x = goal.vertices
  for k in range(10):
    len_before = len(facet_pairs)

    for tr_seg in zip(list(x), list(x)[1:]+[x[0]]):
      facet_pairs = fold_all_facets_by_line(facet_pairs, tr_seg)
      if draw:
        draw_side_by_side(
            [f[0] for f in facet_pairs],
            [transform_facet(f[0], f[1]) for f in facet_pairs],
        )

    # early exit
    if len(facet_pairs) == len_before:
      break

  if draw:
    draw_side_by_side(
        [f[0] for f in facet_pairs],
        [transform_facet(f[0], f[1]) for f in facet_pairs] + [goal]
    )

  # done:
  return facet_pairs

def gen_sgibatel():
    all_points, facets, mats = get_cat_facets()

    facets_for_vlad = []
    mats_for_vlad = []

    index = 0
    for f in facets:
        polygon_pts = []
        for p_index in f:
            polygon_pts.append(mkpt(all_points[p_index]))
        polygon = Polygon(*polygon_pts)
        facets_for_vlad.append(polygon)
        mats_for_vlad.append(mats[index])

        index += 1
    return zip(facets_for_vlad, mats_for_vlad)


if __name__ == "__main__":
    #
    # Convex goal
    #
    #goal = convex_hull(*silhouette_pts)
    #if goal.area > 0:
    #  goal = Polygon(*(list(goal.vertices)[::-1]))

    #
    # Starting state
    #
    # facets = [Polygon(
    #   mkpt(Point(Fraction(0),Fraction(0))),
    #   mkpt(Point(Fraction(0),Fraction(1))),
    #   mkpt(Point(Fraction(1),Fraction(1))),
    #   mkpt(Point(Fraction(1),Fraction(0))),
    # )]
    # mats = [diag(1,1,1)]
    #
    # #minx = min([p.x for p in goal.vertices])
    # #miny = min([p.y for p in goal.vertices])
    # #mats = [get_shift_transform(minx, miny)]
    #
    # facet_pairs = zip(facets, mats)

    facet_pairs = gen_sgibatel()
    # print facet_pairs


    #######################
    # dodraw?
    draw = True

    #if draw:
    #  draw_side_by_side([], [])

    small = random.randint(1, 3)
    big = random.randint(3, 7)
    # small = 2
    # big = 3
    lines = [
        [
            Point(0, Fraction(big, big + 1)),
            Point(1, Fraction(2, 7))
        ],
        # [
        #     Point(Fraction(1, small), Fraction(0)),
        #     Point(Fraction(1, big), Fraction(1))
        # ],
        [
            Point(Fraction(0), Fraction(0)),
            Point(Fraction(1, 3), Fraction(5, 6))
        ],
        [
            Point(Fraction(1, small) + Fraction(1, 11), Fraction(1)),
            Point(Fraction(3, 4), Fraction(0))
        ],
    ]
    for l in lines:
        facet_pairs = fold_all_facets_by_line(facet_pairs, l)


    # facet_pairs = fold_all_facets_by_line(facet_pairs,
    #     [Point(Fraction(1, small), 0), Point(Fraction(small, small + 2), 1)])
    #
    # facet_pairs = fold_all_facets_by_line(facet_pairs,
    #     [Point(0, Fraction(big, big + 1)), Point(3, Fraction(2, 13))])
    #

    # facet_pairs = fold_all_facets_by_line(facet_pairs,
    #     [Point(0,Fraction(1,2)), Point(1,Fraction(1,2))])
    # facet_pairs = fold_all_facets_by_line(facet_pairs,
    #     [Point(0,Fraction(1,4)), Point(1,Fraction(1,4))])
    # facet_pairs = fold_all_facets_by_line(facet_pairs,
    #     [Point(0,Fraction(1,8)), Point(1,Fraction(1,8))])
    # facet_pairs = fold_all_facets_by_line(facet_pairs,
    #     [Point(0,Fraction(1,16)), Point(1,Fraction(1,16))])

    # denom = random.randint(15, 30)
    # facet_pairs = fold_all_facets_by_line(facet_pairs,
    #     [Point(Fraction(7,17),Fraction(0,1)), Point(Fraction(9,17),Fraction(1,16))])

    def pyth(m, n):
        a = m*m - n * n
        b = 2 * m * n
        c = m*m + n * n
        return a, b, c

    m = random.randint(4, 6)
    n = random.randint(1, 3)

    a, b, c = pyth(m, n)
    a, b, c = 3, 4, 5

    draw_side_by_side(
        [f[0] for f in facet_pairs],
        [transform_facet(f[0], f[1]) for f in facet_pairs]
    )


    R = get_refl_transform(a, b)
    S = get_shift_transform(-1, Fraction(3))
    facet_pairs = [
        (f[0], S * R * f[1]) for f in facet_pairs]

    sol = facet_pairs


    #
    # Print solution
    #
    pts_revert = {}
    for p in pts:
      pts_revert[pts[p]] = p

    print len(pts)
    print '\n'.join([
        '{},{}'.format(pts_revert[i].x, pts_revert[i].y)
        for i in range(len(pts)) ])


    print len(sol)
    for pol in sol:
      print "{} {}".format(
          len(pol[0].vertices),
          ' '.join([
              str(pts[p]) for p in pol[0].vertices
            ]))


    transformed_pts = {}

    for facet_pair in sol:
      facet, mat = facet_pair
      for p in facet.vertices:
        transformed_pts[pts[p]] = transform_point(p, mat)

    print '\n'.join([
        '{},{}'.format(transformed_pts[i].x, transformed_pts[i].y)
        for i in range(len(pts))])

    #print set(transformed_pts.values())
    #print len(set(transformed_pts.values()))

    #for p in transformed_pts:
    #  print transformed_pts[p].x, " ", transformed_pts[p].y
