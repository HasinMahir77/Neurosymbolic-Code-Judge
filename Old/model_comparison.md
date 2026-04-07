# Neuro-Symbolic Judge: Model Generation Comparison

This document compares the performance of three Gemini models when generating deterministic Z3 constraints for the Neuro-Symbolic Code Judge.

## High-Level Metrics Comparison

| Metric | Gemini 2.5 Flash | Gemini 3.0 Flash | Gemini 3.1 Pro Preview |
| :--- | :--- | :--- | :--- |
| **Total Functions Verified** | 13 | 13 | **17** |
| **Bugs (Counterexamples) Found** | 7 | 11 | **10** |
| **Framework Errors (Timeouts/Parsing)** | 8 | 4 | **1** |
| **Missed Bugs (False Positives)**| 1 (`factorial`) | **0** | **0** |

---

## Key Behavioral Differences

### 1. Accuracy vs False "Counterexamples"
At first glance, it might look like **Gemini 3.0 Flash** found more "bugs" (11) than **3.1 Pro** (10). However, looking closely at the generated constraints reveals that 3.0 Flash triggered several false alarms.

> [!WARNING]
> **False Positives in 3.0 Flash**
> In `05_clamp_clean.py`, the `main` function is mathematically correct. However, 3.0 Flash failed to properly model its dependencies, causing the SMT solver to flag a false `COUNTEREXAMPLE`. 3.1 Pro perfectly modeled the logic and successfully recognized the code as `VERIFIED`.

### 2. JSON Constraints & Syntax Robustness 
We can clearly see a progression in strict instruction-following capabilities across the models:

* **Gemini 2.5 Flash (8 Errors):** Struggled heavily to strictly obey the `Pydantic` JSON schemas. It repeatedly broke the parser with trailing commas and unescaped character quotes.
* **Gemini 3.0 Flash (4 Errors):** Fixed all JSON parsing logic, but still hit timeout issues and hallucinated Python execution concepts. For example, it injected `NameError: name 'SDiv' is not defined` inside its generated proof for `01_binary_search`.
* **Gemini 3.1 Pro (1 Error):** Handled strict JSON formats perfectly and wrote 100% executable Python script logic. The only error it hit was a pure mathematical Z3 timeout.

### 3. Solving the Unbounded Loop Limitation
A known issue with standard SMT Solvers like Z3 is that they time out mathematically when forced to unroll unbounded `while` loops (such as the Euclidean algorithm).

> **Pro's Unrolling Strategy**
> Both 2.5 and 3.0 Flash hit strict timeouts limits on unbounded loops. **Gemini 3.1 Pro** was smart enough to recognize a formal prover's mathematical limitations and bypassed them dynamically! Rather than letting Z3 stall infinitely, 3.1 Pro automatically injected hardcoded bound ranges into the scripts (e.g. `for _ in range(6)` to constrain tests for integers <100,000) allowing for a successful proof without Timing out.
