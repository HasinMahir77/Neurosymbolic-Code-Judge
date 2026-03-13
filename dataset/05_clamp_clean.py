def clamp(value, low, high):
    """Clamp value to [low, high]. This implementation is correct."""
    if value < low:
        return low
    if value > high:
        return high
    return value


def scale(value, factor):
    """Multiply value by factor. Correct implementation."""
    return value * factor


def process(raw_value):
    """Clamp raw_value to [0, 100] then scale by 2.55 for 8-bit range."""
    clamped = clamp(raw_value, 0, 100)
    return scale(clamped, 2.55)


def main():
    print(process(50))
    print(process(-10))
    print(process(200))
