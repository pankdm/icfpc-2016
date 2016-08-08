import re
import matplotlib.pyplot as plt
import sys
import pylab
from fractions import Fraction

#fn = open('test89', 'r')
fn = sys.stdin
f = fn.read()
nums =  [x for x in re.split('[\s,]+', f) if x != '']
nums = nums[::-1]

MAX = 10**18


def getfloat(x):
  if x.find('/') == -1:
	return float(x)
  else:
      n, d = re.split('/', x)
      n = int(n)
      d = int(d)
      if n > MAX:
          n /= MAX
        #   d /= MAX

      return Fraction(int(n), int(d))
	# return float(int(n)*1000000 / int(d)) / 1000000.0;


n = int(nums.pop())
print(n)
for i in range(n):
	p = int(nums.pop())
	for j in range(p):
		x = getfloat(nums.pop())
		y = getfloat(nums.pop())
		pass

n = int(nums.pop())
print(n)
xs = []
ys = []
for i in range(n):
	x1 = getfloat(nums.pop())
	y1 = getfloat(nums.pop())
	x2 = getfloat(nums.pop())
	y2 = getfloat(nums.pop())

	plt.plot([x1, x2], [y1, y2], linestyle='-', lw=5)

# plt.plot([-0.25], [-0.25])
# plt.plot([1.25], [1.25])
# plt.show()

pylab.savefig(sys.argv[1])


#fig, ax = plt.subplots( nrows=1, ncols=1 )  # create figure & 1 axis
#ax.plot([0,1,2], [10,20,3])
#fig.savefig('path/to/save/image/to.png')   # save the figure to file
#plt.close(fig)
