def reverse_number(n):
    """Reverse the digits of a non-negative integer."""
    reversed_n = 0
    while n > 0:
        reversed_n = reversed_n * 10 + n % 10
        n //= 10
    return reversed_n


def is_palindrome(n):
    """Check if an integer is a palindrome.
    Negative numbers are not considered palindromes.
    """
    if n <= 0:  # Bug: should be n < 0; rejects 0 which is a valid palindrome
        return False
    return n == reverse_number(n)


def main():
    print(is_palindrome(121))
    print(is_palindrome(123))
    print(is_palindrome(-121))
    print(is_palindrome(0))
