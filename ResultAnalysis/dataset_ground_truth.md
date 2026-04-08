# Dataset Ground Truth

15 scripts — 10 buggy, 5 clean.

## Script-Level Verdicts

| Script | Ground Truth | Buggy Function(s) | Bug Description |
| :--- | :--- | :--- | :--- |
| `01_binary_search.py` | **CLEAN** | — | Midpoint `(lo + hi) // 2` has no overflow in Python (arbitrary-precision integers). Correct for all valid inputs. |
| `02_factorial.py` | **BUGGY** | `factorial` | No guard for negative input — `range(2, n+1)` produces an empty range for `n < 0`, silently returning 1 instead of raising an error. |
| `03_fibonacci.py` | **BUGGY** | `fibonacci` | Base case returns `1` for both `n=0` and `n=1`. Should return `n`. `fib(0)` produces 1 instead of 0. |
| `04_is_palindrome.py` | **BUGGY** | `is_palindrome` | Guard `n <= 0` incorrectly rejects 0. Should be `n < 0`. Zero is a valid palindrome. |
| `05_clamp_clean.py` | **CLEAN** | — | Correct clamping and scaling across all boundary cases. |
| `06_gcd.py` | **BUGGY** | `gcd`, `lcm` | `gcd`: wrong sign for negative inputs. `lcm`: division by zero when both inputs are 0. |
| `07_max_subarray.py` | **BUGGY** | `max_subarray_sum` | Missing base case for empty range — when `lo > hi`, falls through to `arr[lo]` without a bounds check. |
| `08_power_clean.py` | **CLEAN** | — | Fast exponentiation by squaring. Correct for all `exp >= 0`. |
| `09_fizzbuzz.py` | **BUGGY** | `classify` | The `n % 15 == 0` branch is unreachable — it appears after `n % 3 == 0`, which already matches all multiples of 15. |
| `10_abs_diff_clean.py` | **CLEAN** | — | Correct absolute value and difference for all inputs. |
| `11_isqrt.py` | **BUGGY** | `isqrt` | Binary search condition `mid * mid < n` should be `mid * mid <= n`. Strict inequality causes early termination for perfect squares. Counterexample: `isqrt(4)` → 1, expected 2. |
| `12_mod_pow.py` | **BUGGY** | `mod_pow` | Base is squared before being multiplied into result; should be squared after. Counterexample: `mod_pow(2, 2, 5)` → 1, expected 4. |
| `13_count_divisors.py` | **BUGGY** | `count_divisors` | Unconditionally adds 2 for each divisor found, double-counting the square root of perfect squares. Counterexample: `count_divisors(4)` → 4, expected 3. |
| `14_running_total_clean.py` | **CLEAN** | — | `running_max`, `running_min`, and `running_sum` all correct. |
| `15_is_prime.py` | **BUGGY** | `is_prime` | Trial division loop uses `i * i < n` instead of `i * i <= n`, missing the case where `n` is the square of an odd prime. Counterexample: `is_prime(9)` → True, expected False. |
