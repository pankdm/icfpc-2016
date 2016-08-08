
from origami import *

class Needle(Origami):
    def __init__(self, n):
        pieces = 2**n
        side = F(1, 2**n)

        self.dst = [
            (F(0), F(0)),
            (F(1), F(0)),
            (F(0), side),
            (F(1), side),
        ]

        self.src = []
        now = 0
        while (now <= 1):
            self.src.append( (now, F(0)) )
            self.src.append( (now, F(1)) )
            now += side

        self.facets = []
        start = 0
        while (start + 3 <= len(self.src)):
            self.facets.append( (start, start + 1, start + 3, start + 2) )
            start += 2


        self.transform = {}
        for i in xrange(0, len(self.src)):
            self.transform[i] = i % 4

origami = Needle(3)
origami.dump_output()
# origami.show()
