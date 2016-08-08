#!/usr/bin/python

import re
import sys
from sympy import Matrix, diag
from sympy.geometry import *
from fractions import Fraction

# dodraw?
draw = False
if draw:
  import matplotlib.pyplot as plt
  import pylab

from read_input import silhouette_pts

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

  draw_polygon(fig_2, goal, ls=':', lw=3)

  pylab.show()


def solve_convex(goal, facet_pairs):
  global pts

  if draw:
    draw_side_by_side(
        [f[0] for f in facet_pairs],
        [transform_facet(f[0], f[1]) for f in facet_pairs],
    )

  x = goal.vertices
  for k in range(20):
    len_before = len(facet_pairs)

    for tr_seg in zip(list(x), list(x)[1:]+[x[0]]):
      
      pts_backup = pts.copy()
      facet_pairs_cand = fold_all_facets_by_line(facet_pairs, tr_seg)

      # if too long:
      if sol_len(serialize_solution(facet_pairs_cand)) > 5000:
        import sys
        print >> sys.stderr, "Size exceeded limit"
        pts = pts_backup
        return facet_pairs

      # if ok
      facet_pairs = facet_pairs_cand

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



#
# Print solution
#
def serialize_solution(sol):
  pts_revert = {}
  for p in pts:
    pts_revert[pts[p]] = p

  lines = []

  lines.append(str(len(pts)))
  lines.append('\n'.join([
      '{},{}'.format(pts_revert[i].x, pts_revert[i].y)
      for i in range(len(pts)) ]))


  lines.append(str(len(sol)))
  for pol in sol:
    lines.append("{} {}".format(
        len(pol[0].vertices),
        ' '.join([
            str(pts[p]) for p in pol[0].vertices
          ])))


  transformed_pts = {}

  for facet_pair in sol:
    facet, mat = facet_pair
    for p in facet.vertices:
      transformed_pts[pts[p]] = transform_point(p, mat)

  lines.append('\n'.join([
      '{},{}'.format(transformed_pts[i].x, transformed_pts[i].y)
      for i in range(len(pts))
      ]))

  return '\n'.join(lines)

def sol_len(s):
  return len(s) - s.count(' ') - s.count('\n')
 

#
# Convex goal
#
goal = convex_hull(*silhouette_pts)
if goal.area > 0:
  goal = Polygon(*(list(goal.vertices)[::-1]))

#
# Starting state
#
facets = [Polygon(
  mkpt(Point(Fraction(0),Fraction(0))),
  mkpt(Point(Fraction(0),Fraction(1))),
  mkpt(Point(Fraction(1),Fraction(1))),
  mkpt(Point(Fraction(1),Fraction(0))),
)]
#mats = [diag(1,1,1)]

##
# Rotations:
##
rots = [ (1, 0, 1),
    (3,4,5), (15,8,17), (5,12,13),
    (-3,4,5), (-15,8,17), (-5,12,13),
    (3,-4,5), (15,-8,17), (5,-12,13),
    (-3,-4,5), (-15,-8,17), (-5,-12,13), ]

from argparse import ArgumentParser
parser = ArgumentParser()
parser.add_argument('--rot', type=int, default=0)
args = parser.parse_args()

rot = rots[ args.rot ]

sina = Fraction(rot[0], rot[2])
cosa = Fraction(rot[1], rot[2])
mat_rot = Matrix([
    [sina, cosa, 0],
    [-cosa, sina, 0],
    [0, 0, 1],
  ])

# inverse rotate goal:
goal = transform_facet(goal, mat_rot ** -1)

# fit from left/botton:
minx = min([p.x for p in goal.vertices])
miny = min([p.y for p in goal.vertices])
mat_shift = get_shift_transform(minx, miny)

xd = max([p.x for p in goal.vertices]) - minx
yd = max([p.y for p in goal.vertices]) - miny

# rotate goal to original
goal = transform_facet(goal, mat_rot)

# initial square:
facet_pairs = zip(facets, [diag(1,1,1)])

# log-reduce size if possible
#for k in range(1,7):
#  if xd > Fraction(1,2):
#    break
#  facet_pairs = fold_all_facets_by_line(facet_pairs,
#      (
#          Point(Fraction(1,2**k), 1),
#          Point(Fraction(1,2**k), 0)
#      ))
#  xd *= 2
#for k in range(1,7):
#  if yd > Fraction(1,2):
#    break
#  facet_pairs = fold_all_facets_by_line(facet_pairs,
#      (
#          Point(0, Fraction(1,2**k)),
#          Point(1, Fraction(1,2**k))
#      ))
#  yd *= 2

# reduce size to bounding rectangle
fx = Fraction(0,1)
while fx < 1:
  pts_backup = pts.copy()
  facet_pairs_cand = fold_all_facets_by_line(facet_pairs,
      (
          Point(xd / Fraction(1), Fraction(1)),
          Point(xd / Fraction(1), Fraction(0))
      ))
  # if too long:
  if sol_len(serialize_solution(facet_pairs_cand)) > 5000:
    print >> sys.stderr, "Size exceeded limit"
    pts = pts_backup
    break

  facet_pairs = facet_pairs_cand
  fx += xd

  pts_backup = pts.copy()
  facet_pairs_cand = fold_all_facets_by_line(facet_pairs,
      (
          Point(Fraction(0), Fraction(0)),
          Point(Fraction(0), Fraction(1))
      ))
  # if too long:
  if sol_len(serialize_solution(facet_pairs_cand)) > 5000:
    print >> sys.stderr, "Size exceeded limit"
    pts = pts_backup
    break

  facet_pairs = facet_pairs_cand
  fx += xd

fy = Fraction(0,1)
while fy < 1:
  pts_backup = pts.copy()
  facet_pairs_cand = fold_all_facets_by_line(facet_pairs,
      (
          Point(Fraction(0), yd / Fraction(1)),
          Point(Fraction(1), yd / Fraction(1))
      ))
  # if too long:
  if sol_len(serialize_solution(facet_pairs_cand)) > 5000:
    print >> sys.stderr, "Size exceeded limit"
    pts = pts_backup
    break

  facet_pairs = facet_pairs_cand
  fy += yd
  
  pts_backup = pts.copy()
  facet_pairs_cand = fold_all_facets_by_line(facet_pairs,
      (
          Point(Fraction(1), Fraction(0)),
          Point(Fraction(0), Fraction(0))
      ))
  # if too long:
  if sol_len(serialize_solution(facet_pairs_cand)) > 5000:
    print >> sys.stderr, "Size exceeded limit"
    pts = pts_backup
    break

  facet_pairs = facet_pairs_cand
  fy += yd


# apply shirt/rotate transform matrix
mat = mat_rot * mat_shift
facet_pairs = [(f[0], mat * f[1]) for f in facet_pairs]


## -- manutal steps
#facet_pairs = fold_all_facets_by_line(facet_pairs,
#    (
#        Point(0,Fraction(2,3)),
#        Point(1,Fraction(2,3))
#    ))
#facet_pairs = fold_all_facets_by_line(facet_pairs,
#    (
#        Point(0,Fraction(1,3)),
#        Point(1,Fraction(1,3))
#    ))
#facet_pairs = fold_all_facets_by_line(facet_pairs,
#    (
#        Point(0,Fraction(1,6)),
#        Point(1,Fraction(1,6))
#    ))
#
#facet_pairs = fold_all_facets_by_line(facet_pairs,
#    ( 
#        Point(Fraction(16,31),1),
#        Point(Fraction(16,31),0)
#    ))
#facet_pairs = fold_all_facets_by_line(facet_pairs,
#    (
#        Point(Fraction(8,31),1),
#        Point(Fraction(8,31),0)
#    ))
#facet_pairs = fold_all_facets_by_line(facet_pairs,
#    (
#        Point(Fraction(4,31),1),
#        Point(Fraction(4,31),0)
#    ))
#facet_pairs = fold_all_facets_by_line(facet_pairs,
#    (
#        Point(Fraction(2,31),1),
#        Point(Fraction(2,31),0)
#    ))
#facet_pairs = fold_all_facets_by_line(facet_pairs,
#    (
#        Point(Fraction(1,31),1),
#        Point(Fraction(1,31),0)
#    ))


#######################

if draw:
  draw_side_by_side([], [])
  draw_side_by_side(
      [f[0] for f in facet_pairs],
      [transform_facet(f[0], f[1]) for f in facet_pairs],
  )

sol = solve_convex(goal, facet_pairs)
print serialize_solution(sol)

