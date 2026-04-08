# Dataset Ground Truth

10 scripts — 7 buggy, 3 clean.

## Script-Level Verdicts

| Script | Ground Truth | Buggy Function(s) | Bug Description |
| :--- | :--- | :--- | :--- |
| `01_binary_search.py` | **BUGGY** | `binary_search` | Midpoint `(lo + hi) // 2` overflows for large index values. Should be `lo + (hi - lo) // 2`. |
| `02_factorial.py` | **BUGGY** | `factorial` | No guard for negative input — `range(2, n+1)` is empty for `n < 0`, silently returns 1. |
| `03_average.py` | **BUGGY** | `compute_sum` | Off-by-one: initialises `total = numbers[0]` then loops `range(1, count)`, double-counting the first element. |
| `04_is_palindrome.py` | **BUGGY** | `is_palindrome` | No guard for negative inputs — `reverse_number(-121)` returns 0, so `is_palindrome(-121)` silently returns False. |
| `05_clamp_clean.py` | **CLEAN** | — | Correct clamping and scaling across all edge cases. |
| `06_gcd.py` | **BUGGY** | `gcd`, `lcm` | `gcd`: wrong sign for negative inputs. `lcm`: division by zero when both inputs are 0. |
| `07_max_subarray.py` | **BUGGY** | `max_subarray_sum` | Missing base case for empty range — when `lo > hi`, falls through to `arr[lo]` without checking. |
| `08_power_clean.py` | **CLEAN** | — | Fast exponentiation by squaring. Correct for all `exp >= 0`. |
| `09_fizzbuzz.py` | **BUGGY** | `classify` | `n % 15 == 0` branch is unreachable — appears after `n % 3 == 0`, which already matches all multiples of 15. |
| `10_abs_diff_clean.py` | **CLEAN** | — | Correct absolute value and difference, handles negative inputs and reversed operand order. |
