
from fractions import Fraction as F
import matplotlib.pyplot as plt

from origami import *
import random

def validate_problem(p):
    print 'Checking transform'
    for i in xrange(len(p.src)):
        assert i in p.transform, i
    for p1, p2 in p.transform.items():
        assert p2 < len(p.dst), p2


def prepare_output(p, name):
    f = open(name, 'wt')

    mapping = range(0, len(p.src))
    random.shuffle(mapping)
    reverse_mapping = range(0, len(p.src))
    for i in xrange(len(mapping)):
        reverse_mapping[ mapping[i] ] = i

    print >> f, len(p.src)
    for i in xrange(len(p.src)):
        # x, y = p.src[ mapping[i] ]
        x,y = p.src[ i ]
        print >> f, "{},{}".format(x, y)
    print >> f, len(p.facets)
    for facet in p.facets:
        output = '{} '.format(len(facet))
        output += ' ' + ' '.join(map(str, facet))
        # output += ' ' + ' '.join(map(str, map(lambda x: mapping[x], facet)))
        # output += ' ' + ' '.join(map(str, map(lambda x: reverse_mapping[x], facet)))
        print >> f, output

    delta_x = F(4543, 982)
    delta_y = F(95423, 6292)

    # alpha = F(6253, 9997)
    # beta = F(7800, 9997)
    # (7701, 10100, 12701)
    alpha = F(7701, 12701)
    beta = F(10100, 12701)

    for i in xrange(len(p.src)):
        # orig = reverse_mapping[i]
        orig = i
        next = p.transform[orig]
        x0, y0 = p.dst[next]
        x = x0 * alpha + y0 * beta + delta_x
        y = x0 * (-beta) + y0 * alpha + delta_y
        print >> f, "{},{}".format(x, y)
    f.close()

class Ship(Origami):
    def __init__(self):
        self.dst = [
            (F(0), F(0)),
            (F(1, 4), F(0)),
            (F(1, 2), F(1, 4)),
            (F(3, 4), F(1, 4)),
            (F(3, 4), F(1, 2)),
            (F(1), F(3, 4)),
            (F(1), F(1)),
            (F(3, 4), F(3, 4)),
            (F(1, 4), F(3, 4)),
            (F(1, 4), F(1, 4)),
        ]
        self.segments = [
            (0, 1),
            (0, 6),
            (1, 5),
            (9, 3),
            (3, 7),
            (5, 6),
            (5, 8),
            (8, 1),
        ]

        self.facets = [
            (9, 7, 8),
            (0, 6, 7, 9),
            (0, 1, 5, 6),
            (1, 2, 4, 5),
            (2, 3, 4),
        ]

        self.src = [
            (F(0), F(0)),
            (F(1, 4), F(0)),
            (F(1, 2), F(0)),
            (F(1), F(0)),
            (F(1), F(1, 2)),
            (F(1), F(3, 4)),
            (F(1), F(1)),
            (F(3, 4), F(1)),
            (F(0), F(1)),
            (F(0), F(1, 4)),
        ]

        self.transform = {
            0: 0,
            1: 1,
            2: 9,
            3: 3,
            4: 7,
            5: 5,
            6: 6,
            7: 5,
            8: 8,
            9: 1,
        }

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

        for s1, s2 in self.segments:
            x1, y1 = self.dst[s1]
            x2, y2 = self.dst[s2]
            plt.plot([x1, x2], [y1, y2], linestyle='-')

        plt.plot([-0.25], [-0.25])
        plt.plot([1.25], [1.25])
        plt.show()


def show(old_points):
    points = old_points + [old_points[0]]
    for i in xrange(len(points) - 1):
        x1, y1 = points[i]
        x2, y2 = points[i+1]
        # print [x1, y1], [x2, y2]
        plt.annotate(str(i), (x1, y1))
        plt.plot([x1, x2], [y1, y2], linestyle='-')

    plt.plot([-0.25], [-0.25])
    plt.plot([1.25], [1.25])
    plt.show()

def show_skeleton(points, segments):
    for i in xrange(len(points)):
        x1, y1 = points[i]
        plt.annotate(str(i), (x1, y1))

    for s1, s2 in segments:
        x1, y1 = points[s1]
        x2, y2 = points[s2]
        plt.plot([x1, x2], [y1, y2], linestyle='-')

    plt.plot([-0.25], [-0.25])
    plt.plot([1.25], [1.25])
    plt.show()


if __name__ == "__main__":
    origami = Ship()
    origami.dump_output()
    origami.show()




# ship = Ship()
# validate_problem(ship)
# prepare_output(ship, 'output.txt')


#ship.show()
#show(points)
#show_skeleton(ship.dst, ship.segments)
