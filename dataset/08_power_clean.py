def power(base, exp):
    """Fast exponentiation by squaring. Correct for exp >= 0."""
    if exp == 0:
        return 1
    if exp % 2 == 0:
        half = power(base, exp // 2)
        return half * half
    else:
        return base * power(base, exp - 1)


def main():
    print(power(2, 10))
    print(power(3, 0))
    print(power(5, 3))
