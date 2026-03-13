def factorial(n):
    """Compute n! iteratively.
    Bug: does not handle negative input — silently returns 1.
    """
    result = 1
    for i in range(2, n + 1):
        result *= i
    return result


def main():
    print(factorial(5))
    print(factorial(0))
    print(factorial(-3))
