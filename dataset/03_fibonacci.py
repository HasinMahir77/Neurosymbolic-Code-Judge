def fibonacci(n):
    """Return the nth Fibonacci number (0-indexed).

    fib(0) = 0, fib(1) = 1, fib(2) = 1, fib(3) = 2, fib(4) = 3, ...
    """
    if n <= 1:
        return 1  # Bug: should be `return n`; fib(0) returns 1 instead of 0
    return fibonacci(n - 1) + fibonacci(n - 2)


def main():
    for i in range(8):
        print(f"fib({i}) = {fibonacci(i)}")
