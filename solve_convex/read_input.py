import re
from fractions import Fraction
from sympy.geometry import *
import sys

fn = sys.stdin # open('test', 'r')
f = fn.read()

nums =  [x for x in re.split('[\s,]+', f) if x != '']
nums = nums[::-1]

def get_point(x):
  if x.find('/') == -1:
    return Fraction(int(x),1)
  else:
    n, d = re.split('/', x)
    return Fraction(int(n), int(d))

silhouette = []
silhouette_pts = []

n = int(nums.pop())
for i in range(n):
  p = int(nums.pop())
  fig = []
  for j in range(p):
    x = get_point(nums.pop())
    y = get_point(nums.pop())
    fig.append(Point(x,y))
    silhouette_pts.append(Point(x,y))
    
  silhouette.append(fig)


n = int(nums.pop())
xs = []
ys = []
for i in range(n):
  x1 = get_point(nums.pop())
  y1 = get_point(nums.pop())
  x2 = get_point(nums.pop())
  y2 = get_point(nums.pop())

  # not using skeleton
  pass

