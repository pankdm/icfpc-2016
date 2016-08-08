
import math
from fractions import Fraction as F



def get_a(h):
    a = h - 2 * h * h
    return a




if __name__ == "__main__":
    print get_a(F(1, 3))
