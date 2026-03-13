def binary_search(arr, target, lo, hi):
    """Binary search for target in sorted arr[lo..hi].
    Bug: integer overflow on midpoint calculation for large arrays.
    """
    while lo <= hi:
        mid = (lo + hi) // 2  # Bug: should be lo + (hi - lo) // 2
        if arr[mid] == target:
            return mid
        elif arr[mid] < target:
            lo = mid + 1
        else:
            hi = mid - 1
    return -1


def main():
    data = [1, 3, 5, 7, 9, 11, 13]
    print(binary_search(data, 7, 0, len(data) - 1))
