# Benchmark Results vs Ground Truth

**Model:** gemini-3-flash-preview | **Thinking:** disabled (budget=0) | **Time:** ~150s  
**Verdict unit:** script (BUGGY if any non-`main` function has a counterexample)

---

## Script-Level Verdict

| Script | Ground Truth | System Verdict | Classification |
| :--- | :--- | :--- | :--- |
| `01_binary_search.py` | BUGGY — integer overflow on midpoint | CLEAN | ❌ False Negative |
| `02_factorial.py` | BUGGY — silent wrong result for `n < 0` | BUGGY (`factorial`, n=-1) | ✅ True Positive |
| `03_average.py` | BUGGY — off-by-one, first element double-counted | CLEAN | ❌ False Negative |
| `04_is_palindrome.py` | BUGGY — no guard for negative input | CLEAN | ❌ False Negative |
| `05_clamp_clean.py` | CLEAN | CLEAN | ✅ True Negative |
| `06_gcd.py` | BUGGY — negative input bug + lcm div-by-zero | BUGGY (`gcd`, a=-1, b=0) | ✅ True Positive |
| `07_max_subarray.py` | BUGGY — no base case for `lo > hi` | BUGGY (`max_subarray_sum`) | ✅ True Positive |
| `08_power_clean.py` | CLEAN | CLEAN | ✅ True Negative |
| `09_fizzbuzz.py` | BUGGY — `n % 15` branch unreachable | BUGGY (`classify`, n=0) | ✅ True Positive |
| `10_abs_diff_clean.py` | CLEAN | CLEAN | ✅ True Negative |

---

## Summary

| Metric | Count |
| :--- | :--- |
| True Positives (buggy scripts correctly flagged) | **4 / 7 = 57%** |
| False Negatives (buggy scripts missed) | **3** |
| True Negatives (clean scripts correctly verified) | **3 / 3 = 100%** |
| False Positives (clean scripts incorrectly flagged) | **0** |

**Bug detection rate: 4 / 7 = 57%**  
**False positive rate: 0 / 3 = 0%**  
**Overall accuracy: 7 / 10 = 70%**

---

## Missed Bugs Analysis

| Script | Buggy Function | Why Missed |
| :--- | :--- | :--- |
| `01_binary_search.py` | `binary_search` | Integer overflow requires values near `INT_MAX / 2`; Z3 integers are unbounded so the model may assert the overflow-free midpoint formula, verifying a correct formulation instead of the buggy one |
| `03_average.py` | `compute_sum` | Model generates a Z3 spec that mirrors the buggy implementation (start at `numbers[0]` then loop) rather than the correct mathematical sum; both agree, so Z3 finds no counterexample |
| `04_is_palindrome.py` | `is_palindrome` | Model adds `n >= 0` precondition (since `reverse_number` is verified for non-negative input), excluding the exact domain where the bug manifests |

---

## Notes

- **`gcd` / `lcm` timeouts**: `lcm` depends on `gcd`, but `gcd` was flagged as buggy (not added to `verified_deps`). Without an axiom, the model tries to inline the Euclidean algorithm in Z3, causing a timeout. This is a known structural issue in the compositional pipeline.
- **`main` filtering**: Counterexamples on functions named `main` are excluded from the file verdict. `main` is a test harness; its counterexamples are either spurious (empty variable dict) or proxies for bugs in callee functions already captured directly.
- **Spurious `main` counterexamples**: `factorial/main` and `is_palindrome/main` both produce empty-variable counterexamples (`{}`). These indicate a Z3 script that finds `sat` with no meaningful model — likely a modeling error in the harness script, not a real bug.
- **All 3 clean programs verified correctly** with zero false positives across all runs.
