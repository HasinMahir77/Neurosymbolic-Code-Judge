def sum_up_to(n):
    """Should return 1 + 2 + ... + n, but has an off-by-one error."""
    total = 0
    for i in range(n):  # Bug: should be range(1, n + 1)
        total += i
    return total


def main():
    print(sum_up_to(10))
