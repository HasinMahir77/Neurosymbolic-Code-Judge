# Dataset Ground Truth

15 scripts — 10 buggy, 5 clean.

## Script-Level Verdicts

| Script | Ground Truth | Buggy Function(s) | Bug Description |
| :--- | :--- | :--- | :--- |
| `01_binary_search.py` | **CLEAN** | — | Midpoint `(lo + hi) // 2` has no overflow in Python (arbitrary-precision integers). Correct for all valid inputs. |
| `02_factorial.py` | **BUGGY** | `factorial` | No guard for negative input — `range(2, n+1)` produces an empty range for `n < 0`, silently returning 1 instead of raising an error. |
| `03_fibonacci.py` | **BUGGY** | `fibonacci` | Base case returns `1` for both `n=0` and `n=1`. Should return `n`. `fib(0)` produces 1 instead of 0, making every subsequent value wrong. |
| `04_is_palindrome.py` | **BUGGY** | `is_palindrome` | Guard `n <= 0` incorrectly rejects 0. Should be `n < 0`. Zero is a valid palindrome (`reverse_number(0) == 0`), but the function returns False. |
| `05_clamp_clean.py` | **CLEAN** | — | Correct clamping and scaling across all boundary cases. |
| `06_gcd.py` | **BUGGY** | `gcd`, `lcm` | `gcd`: returns the wrong sign for negative inputs (e.g., `gcd(-4, 2)` returns -2 instead of 2). `lcm`: division by zero when both inputs are 0 (`gcd(0, 0) == 0`). |
| `07_max_subarray.py` | **BUGGY** | `max_subarray_sum` | Missing base case for an empty range: when `lo > hi`, the function falls through to `arr[lo]` without a bounds check, causing an index error or wrong value. |
| `08_power_clean.py` | **CLEAN** | — | Fast exponentiation by squaring. Correct for all `exp >= 0`. |
| `09_fizzbuzz.py` | **BUGGY** | `classify` | The `n % 15 == 0` branch (FizzBuzz) is unreachable — it appears after `n % 3 == 0`, which already matches all multiples of 15. |
| `10_abs_diff_clean.py` | **CLEAN** | — | Correct absolute value and difference for all inputs, including negatives and reversed operand order. |
| `11_isqrt.py` | **BUGGY** | `isqrt` | The binary search condition `mid * mid < n` should be `mid * mid <= n`. The strict inequality causes the loop to terminate one step early for perfect squares, returning a value one less than the correct floor square root. Counterexample: `isqrt(4)` returns 1 instead of 2; `isqrt(9)` returns 2 instead of 3. |
| `12_mod_pow.py` | **BUGGY** | `mod_pow` | The base is squared at the top of each loop iteration, before being conditionally multiplied into the result. The correct order is: (1) multiply result by base if the current bit of exp is 1, then (2) square base for the next bit. Squaring first means the code uses `base²` for the least-significant bit instead of `base¹`. Counterexample: `mod_pow(2, 2, 5)` returns 1 instead of 4. |
| `13_count_divisors.py` | **BUGGY** | `count_divisors` | The loop unconditionally adds 2 for every divisor `i` found, counting both `i` and `n // i`. When `n` is a perfect square and `i == n // i` (i.e., `i` is the square root of `n`), both are the same divisor and should only be counted once. Counterexample: `count_divisors(4)` returns 4 instead of 3 (divisors: 1, 2, 4). |
| `14_running_total_clean.py` | **CLEAN** | — | `running_max`, `running_min`, and `running_sum` all correctly build prefix-aggregate lists. Handles empty input and single-element inputs correctly. |
| `15_is_prime.py` | **BUGGY** | `is_prime` | The trial division loop uses `i * i < n` instead of `i * i <= n`. The strict inequality causes the loop to exit without testing `i` when `i² == n`, missing the case where `n` is the square of an odd prime. Counterexample: `is_prime(9)` returns True (9 = 3²) and `is_prime(25)` returns True (25 = 5²). |
