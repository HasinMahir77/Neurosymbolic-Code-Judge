def absolute(x):
    """Return absolute value of x. Correct implementation."""
    if x < 0:
        return -x
    return x


def abs_diff(a, b):
    """Return |a - b|. Correct — uses absolute()."""
    return absolute(a - b)


def main():
    print(abs_diff(10, 3))
    print(abs_diff(3, 10))
    print(abs_diff(-5, -8))
