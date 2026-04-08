# Dataset Ground Truth

10 scripts — 6 buggy, 4 clean.

## Script-Level Verdicts

| Script | Ground Truth | Buggy Function(s) | Bug Description |
| :--- | :--- | :--- | :--- |
| `01_binary_search.py` | **CLEAN** | — | Midpoint `(lo + hi) // 2` has no overflow in Python (arbitrary-precision integers). Correct for all inputs. |
| `02_factorial.py` | **BUGGY** | `factorial` | No guard for negative input — `range(2, n+1)` is empty for `n < 0`, silently returns 1. |
| `03_fibonacci.py` | **BUGGY** | `fibonacci` | Base case returns `1` for both `n=0` and `n=1`; should return `n`. `fib(0)` returns 1 instead of 0. |
| `04_is_palindrome.py` | **BUGGY** | `is_palindrome` | Guard `n <= 0` rejects 0, which is a valid palindrome. Should be `n < 0`. |
| `05_clamp_clean.py` | **CLEAN** | — | Correct clamping and scaling across all edge cases. |
| `06_gcd.py` | **BUGGY** | `gcd`, `lcm` | `gcd`: wrong sign for negative inputs. `lcm`: division by zero when both inputs are 0. |
| `07_max_subarray.py` | **BUGGY** | `max_subarray_sum` | Missing base case for empty range — when `lo > hi`, falls through to `arr[lo]` without checking bounds. |
| `08_power_clean.py` | **CLEAN** | — | Fast exponentiation by squaring. Correct for all `exp >= 0`. |
| `09_fizzbuzz.py` | **BUGGY** | `classify` | `n % 15 == 0` branch is unreachable — appears after `n % 3 == 0`, which already matches all multiples of 15. |
| `10_abs_diff_clean.py` | **CLEAN** | — | Correct absolute value and difference, handles negative inputs and reversed operand order. |
