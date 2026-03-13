def max_crossing_sum(arr, lo, mid, hi):
    """Find max subarray sum crossing the midpoint."""
    left_sum = -999999
    total = 0
    for i in range(mid, lo - 1, -1):
        total += arr[i]
        if total > left_sum:
            left_sum = total

    right_sum = -999999
    total = 0
    for i in range(mid + 1, hi + 1):
        total += arr[i]
        if total > right_sum:
            right_sum = total

    return left_sum + right_sum


def max_subarray_sum(arr, lo, hi):
    """Divide and conquer max subarray.
    Bug: base case returns arr[lo] but doesn't handle empty range (lo > hi).
    """
    if lo == hi:
        return arr[lo]
    mid = (lo + hi) // 2
    left = max_subarray_sum(arr, lo, mid)
    right = max_subarray_sum(arr, mid + 1, hi)
    cross = max_crossing_sum(arr, lo, mid, hi)
    return max(left, right, cross)


def main():
    data = [-2, 1, -3, 4, -1, 2, 1, -5, 4]
    print(max_subarray_sum(data, 0, len(data) - 1))
