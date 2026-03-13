def compute_sum(numbers, count):
    """Sum the first `count` elements.
    Bug: off-by-one — uses range(1, count) instead of range(count).
    """
    total = numbers[0]
    for i in range(1, count):  # Bug: skips nothing if count=1, but misses last element
        total += numbers[i]
    return total


def compute_average(numbers, count):
    """Compute average of `count` numbers."""
    if count == 0:
        return 0
    total = compute_sum(numbers, count)
    return total / count


def main():
    data = [10, 20, 30, 40, 50]
    print(compute_average(data, 5))
