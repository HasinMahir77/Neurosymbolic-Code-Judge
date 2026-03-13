def classify(n):
    """Return 'FizzBuzz', 'Fizz', 'Buzz', or the number as string.
    Bug: checks divisible by 3 and 5 separately before checking both,
    so 15 returns 'Fizz' instead of 'FizzBuzz'.
    """
    if n % 3 == 0:
        return "Fizz"
    if n % 5 == 0:
        return "Buzz"
    if n % 15 == 0:  # Bug: unreachable — already caught by n%3==0
        return "FizzBuzz"
    return str(n)


def run_fizzbuzz(limit):
    """Run FizzBuzz from 1 to limit."""
    results = []
    for i in range(1, limit + 1):
        results.append(classify(i))
    return results


def main():
    output = run_fizzbuzz(20)
    for line in output:
        print(line)
