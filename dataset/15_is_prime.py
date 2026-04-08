def is_prime(n):
    """Return True if n is a prime number, False otherwise.

    Handles edge cases: n < 2 is not prime; 2 is prime; even numbers > 2
    are not prime. For odd n >= 3, performs trial division by odd numbers
    up to sqrt(n).
    """
    if n < 2:
        return False
    if n == 2:
        return True
    if n % 2 == 0:
        return False
    i = 3
    while i * i < n:
        if n % i == 0:
            return False
        i += 2
    return True


def main():
    primes = [n for n in range(2, 60) if is_prime(n)]
    print(f"Primes below 60: {primes}")
    for n in [1, 4, 9, 17, 25, 49]:
        print(f"is_prime({n}) = {is_prime(n)}")
