
import time
from pyth import pyth, get_random_angles
import random
from fractions import Fraction as F
import matplotlib.pyplot as plt

MIN_INT = 100
MAX_INT = 1000


def get_random_delta():
    p = random.randint(-MAX_INT, MAX_INT)
    q = random.randint(MIN_INT, MAX_INT)
    return F(p, q)


class Origami:
    def __init__(self):
        pass

    def dump_output(self):
        ts = time.time()
        result = []

        # print >> f, len(self.src)
        result += [str(len(self.src))]
        for i in xrange(len(self.src)):
            x,y = self.src[ i ]
            result += ["{},{}".format(x, y)]
            # print >> f, "{},{}".format(x, y)

        # print >> f, len(self.facets)
        result += [str(len(self.facets))]
        for facet in self.facets:
            output = '{} '.format(len(facet))
            output += ' ' + ' '.join(map(str, facet))
            result += [output]
            # print >> f, output
        delta_x = get_random_delta()
        delta_y = get_random_delta()
        print delta_x, delta_y

        # alpha = F(6253, 9997)
        # beta = F(7800, 9997)
        # (7701, 10100, 12701)
        alpha, beta = get_random_angles()
        print alpha, beta

        for i in xrange(len(self.src)):
            # orig = reverse_mapping[i]
            orig = i
            next = self.transform[orig]
            x0, y0 = self.dst[next]
            x = x0 * alpha + y0 * beta + delta_x
            y = x0 * (-beta) + y0 * alpha + delta_y
            result += ["{},{}".format(x, y)]
            # print >> f, "{},{}".format(x, y)

        print
        print '=' * 80
        print '\n'.join(result)
        f = open('output/{}.txt'.format(ts), 'wt')
        f.write('\n'.join(result))
        f.close()

    def show(self):
        inbound = {}
        for p1, p2 in self.transform.items():
            if p2 not in inbound:
                inbound[p2] = list()
            inbound[p2].append(p1)

        for i in xrange(len(self.dst)):
            x1, y1 = self.dst[i]
            incoming = inbound.get(i, None)
            text = '{} <- {}'.format(i, str(incoming))
            plt.annotate(text, (x1, y1))

        # for s1, s2 in self.segments:
        #     x1, y1 = self.dst[s1]
        #     x2, y2 = self.dst[s2]
        #     plt.plot([x1, x2], [y1, y2], linestyle='-')

        plt.plot([-0.25], [-0.25])
        plt.plot([1.25], [1.25])
        plt.show()
