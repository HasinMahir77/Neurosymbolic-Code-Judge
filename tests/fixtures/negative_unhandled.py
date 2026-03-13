def safe_divide(a, b):
    """Should safely divide a by b, but doesn't handle b == 0."""
    return a // b  # Bug: no check for b == 0


def absolute_value(x):
    """Should return absolute value, but fails for the most negative int."""
    if x < 0:
        return -x
    return x


def main():
    print(safe_divide(10, 3))
    print(absolute_value(-5))
