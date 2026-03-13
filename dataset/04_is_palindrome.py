def reverse_number(n):
    """Reverse the digits of a non-negative integer."""
    reversed_n = 0
    while n > 0:
        reversed_n = reversed_n * 10 + n % 10
        n //= 10
    return reversed_n


def is_palindrome(n):
    """Check if a non-negative integer is a palindrome.
    Bug: returns True for n=0 via reverse_number, but fails for
    negative numbers (no guard).
    """
    return n == reverse_number(n)


def main():
    print(is_palindrome(121))
    print(is_palindrome(123))
    print(is_palindrome(-121))
