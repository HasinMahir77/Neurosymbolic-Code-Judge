def clamp(x, lo, hi):
    """Clamp x to the range [lo, hi]."""
    if x < lo:
        return lo
    if x > hi:
        return hi
    return x


def normalize(value, min_val, max_val):
    """Normalize value to [0, 1] range using clamp."""
    clamped = clamp(value, min_val, max_val)
    if max_val == min_val:
        return 0
    return (clamped - min_val) / (max_val - min_val)


def process(data_point):
    """Process a single data point by normalizing to [0, 100] scale."""
    normalized = normalize(data_point, 0, 100)
    return int(normalized * 100)


def main():
    print(process(50))
    print(process(150))
    print(process(-10))
