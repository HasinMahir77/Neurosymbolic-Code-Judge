def isqrt(n):
    """Return the integer square root of n, i.e., floor(sqrt(n)), for n >= 0.

    Uses binary search: find the largest integer x such that x * x <= n.
    """
    if n < 0:
        raise ValueError("Square root is not defined for negative numbers")
    if n == 0:
        return 0
    lo, hi = 1, n
    while lo < hi:
        mid = (lo + hi + 1) // 2
        if mid * mid < n:
            lo = mid
        else:
            hi = mid - 1
    return lo


def main():
    for n in [0, 1, 2, 3, 4, 8, 9, 15, 16, 25, 100]:
        print(f"isqrt({n}) = {isqrt(n)}")
