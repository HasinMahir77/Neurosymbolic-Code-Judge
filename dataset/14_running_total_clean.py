def running_max(values):
    """Return a list where each element is the maximum of values[0..i] inclusive.

    Example: running_max([3, 1, 4, 1, 5]) == [3, 3, 4, 4, 5]
    """
    if not values:
        return []
    result = [values[0]]
    for v in values[1:]:
        result.append(max(result[-1], v))
    return result


def running_min(values):
    """Return a list where each element is the minimum of values[0..i] inclusive.

    Example: running_min([3, 1, 4, 1, 5]) == [3, 1, 1, 1, 1]
    """
    if not values:
        return []
    result = [values[0]]
    for v in values[1:]:
        result.append(min(result[-1], v))
    return result


def running_sum(values):
    """Return a list where each element is the sum of values[0..i] inclusive.

    Example: running_sum([1, 2, 3]) == [1, 3, 6]
    """
    if not values:
        return []
    result = [values[0]]
    for v in values[1:]:
        result.append(result[-1] + v)
    return result


def main():
    data = [3, 1, 4, 1, 5, 9, 2, 6]
    print(f"running_max: {running_max(data)}")
    print(f"running_min: {running_min(data)}")
    print(f"running_sum: {running_sum(data)}")
