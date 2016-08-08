
import random
from fractions import Fraction as F



def pyth(m, n):
    a = m*m - n * n
    b = 2 * m * n
    c = m*m + n * n
    return a, b, c


def get_random_angles():
    m = random.randint(150, 200)
    n = random.randint(20, 50)
    a, b, c = pyth(m, n)
    alpha = F(a, c)
    beta = F(b, c)
    return alpha, beta


if __name__ == "__main__":
    print pyth(3, 10)
    # print get_random_angles()
