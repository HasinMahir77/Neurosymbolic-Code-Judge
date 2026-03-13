def gcd(a, b):
    """Euclidean GCD.
    Bug: doesn't handle negative inputs — gcd(-6, 3) enters
    infinite loop or returns wrong sign.
    """
    while b != 0:
        a, b = b, a % b
    return a


def lcm(a, b):
    """Compute LCM using GCD.
    Bug: division by zero if both a and b are 0.
    """
    return a * b // gcd(a, b)


def main():
    print(gcd(12, 8))
    print(lcm(4, 6))
