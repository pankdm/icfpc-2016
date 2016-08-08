import sys

from fractions import Fraction
import re
import matplotlib.pyplot as plt


fn = sys.stdin # open('test', 'r')
f = fn.read()

nums =  [x for x in re.split('[\s,]+', f) if x != '']
nums = nums[::-1]

def get_fraction(x):
  if x.find('/') == -1:
    return Fraction(int(x),1)
  else:
    n, d = re.split('/', x)
    return Fraction(int(n), int(d))

num_src = int(nums.pop())
for i in xrange(num_src):
    fx = get_fraction(nums.pop())
    fy = get_fraction(nums.pop())

num_facets = int(nums.pop())
for i in xrange(num_facets):
    sides = int(nums.pop())
    for j in xrange(sides):
        index = nums.pop()

dst_points = set()
for i in xrange(num_src):
    fx = get_fraction(nums.pop())
    fy = get_fraction(nums.pop())
    dst_points.add( (fx, fy) )

def show_points(pts):
    i = 0
    for p in pts:
        x1, y1 = p
        plt.plot([x1], [y1], 'r--')
        plt.annotate(str(i), (x1, y1))
        i += 1
    plt.show()


print len(dst_points)
for p in dst_points:
    print p

show_points(dst_points)
