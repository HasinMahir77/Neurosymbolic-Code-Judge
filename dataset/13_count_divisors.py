def count_divisors(n):
    """Return the number of positive divisors of n, including 1 and n itself.

    Uses the standard O(sqrt(n)) approach: for each i up to sqrt(n) that
    divides n, both i and n // i are counted as distinct divisors.
    """
    if n <= 0:
        raise ValueError("n must be a positive integer")
    count = 0
    i = 1
    while i * i <= n:
        if n % i == 0:
            count += 2
        i += 1
    return count


def main():
    for n in [1, 2, 3, 4, 6, 9, 12, 16, 28, 36]:
        print(f"count_divisors({n}) = {count_divisors(n)}")
