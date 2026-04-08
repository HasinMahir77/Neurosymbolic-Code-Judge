def mod_pow(base, exp, mod):
    """Return (base ** exp) % mod using fast exponentiation by squaring.

    Parameters
    ----------
    base : non-negative integer
    exp  : non-negative integer
    mod  : positive integer
    """
    if mod == 1:
        return 0
    result = 1
    base = base % mod
    while exp > 0:
        base = (base * base) % mod
        if exp % 2 == 1:
            result = (result * base) % mod
        exp //= 2
    return result


def main():
    test_cases = [
        (2, 10, 1000),
        (3, 5, 13),
        (7, 0, 11),
        (5, 3, 13),
        (2, 8, 256),
    ]
    for base, exp, mod in test_cases:
        print(f"mod_pow({base}, {exp}, {mod}) = {mod_pow(base, exp, mod)}")
