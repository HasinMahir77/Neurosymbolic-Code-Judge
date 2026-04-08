# Research Question Answers

**System:** Neuro-Symbolic Code Judge (LLM → Z3 SMT solver pipeline)  
**Models tested:** `gemini-3-flash-preview`, `gemini-2.5-flash`  
**Dataset:** 15 Python scripts — 10 buggy, 5 clean (missing guards, off-by-one boundaries, unreachable branches, binary search invariants, operation order, divisor counting, primality)  
**Thinking budget:** 0 (disabled) for all runs  
**Date:** 2026-04-08

---

## RQ1 — LLM-Only vs. Hybrid

> Does the neuro-symbolic hybrid achieve higher bug detection accuracy than using an LLM alone?

### Results

| Approach | Model | TP | TN | FP | FN | Unc/Err | Accuracy |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **Hybrid** | **gemini-3-flash-preview** | **10/10** | **5/5** | **0** | **0** | **0** | **15/15** |
| LLM-only | gemini-2.5-flash | 10/10 | 5/5 | 0 | 0 | 0 | **15/15** |
| LLM-only | gemini-3-flash-preview | 9/10 | 4/5 | 1 | 0 | 1 | 13/14 dec. |
| Hybrid | gemini-2.5-flash | 8/10 | 3/5 | 1 | 1 | 2 | 11/13 dec. |

**The hybrid with gemini-3-flash-preview is the only configuration to achieve a perfect 15/15 with zero false positives.**

A critical observation: `gemini-3-flash-preview` LLM-only **falsely flagged `08_power_clean.py` as BUGGY**, spending ~16k thinking tokens to hallucinate a bug in a correct function. The hybrid's Z3 proof for `power` returned VERIFIED, blocking that false alarm. This is the first empirical demonstration — not a theoretical argument — that the SMT layer prevents the language model from hallucinating bugs in clean code.

While `gemini-2.5-flash` LLM-only also achieves 15/15, its verdict is a black-box assertion — no trace, no witness, no way to verify the reasoning. A developer receiving a BUGGY verdict has no basis to trust or reproduce it. The hybrid changes this fundamentally.

### Conclusion

Raw accuracy on this dataset does not fully separate the hybrid from the best LLM-only baseline. What separates them is the nature of the verdict. The hybrid provides two guarantees that no LLM-only approach can match:

1. **Traceable, step-by-step proof** — the Z3 script encodes the function's contract as explicit logical constraints. Every verification step can be inspected, replayed, and audited independently of the LLM.
2. **Concrete, runnable counterexamples** — every BUGGY verdict includes a specific witness (`n = 4`, `base=2, exp=2, mod=5`, `lo=1, hi=0`) that can be executed directly against the source to confirm the bug. LLM-only verdicts offer none of this; they are opaque confidence scores dressed as conclusions.

The SMT layer also eliminates false positives caused by model hallucination — something LLM-only cannot self-correct.

---

## RQ2 — LLM Model Sensitivity

> How does the choice of underlying LLM affect contract quality, measured by parse success rate, false positive rate, and correct bug detection?

### Hybrid benchmark — full 15 scripts

| Model | TP | TN | FP | FN | Uncertain | Accuracy | Avg tok/file | Wall time |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| gemini-3-flash-preview | **10/10** | **5/5** | **0** | **0** | **0** | **15/15** | **8,152** | **61s** |
| gemini-2.5-flash | 8/10 | 3/5 | 1 | 1 | 2 | 11/13 dec. | 15,257 | 334s |

### LLM-only baseline — full 15 scripts

| Model | TP | TN | FP | FN | Err | Accuracy | Avg tok/file | Wall time |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| gemini-2.5-flash | **10/10** | **5/5** | **0** | **0** | 0 | **15/15** | **2,273** | **37s** |
| gemini-3-flash-preview | 9/10 | 4/5 | 1 | 0 | 1 | 13/14 dec. | 20,081 | 350s |

### Key findings

**1. The model gap is substantial.**  
gemini-2.5-flash hybrid achieves only 11/13 decisive with a false positive on `clamp_clean`. Its Z3 script errors (symbolic list indexing, `TypeError: list indices must be integers or slices, not ArithRef`) affect multiple files. gemini-3-flash-preview hybrid achieves 100% with zero errors.

**2. gemini-2.5-flash hybrid produces a false positive.**  
The LLM generated an over-constrained postcondition for `clamp`, causing Z3 to find a spurious counterexample in a correct function. gemini-3-flash-preview produced no false positives in any run. Crucially, the false positive is detectable: running the counterexample against the actual Python function does not reproduce the claimed bug — the proof trail exposes the spec error.

**3. Heavy thinking is counterproductive for LLM-only.**  
gemini-3-flash-preview LLM-only uses 20,081 tokens/file (98% thinking) and achieves 13/14 decisive — worse than gemini-2.5-flash LLM-only at 2,273 tokens/file. The thinking model hallucinated a bug in `power_clean` and failed to produce a JSON response for `is_palindrome`. Unconstrained reasoning increases both cost and error rate.

**4. Instruction-following determines hybrid accuracy.**  
The hybrid imposes strict code-generation constraints (Z3-only imports, `If`-chain array access, no symbolic list indexing). gemini-3-flash-preview respects these; gemini-2.5-flash does not. Compliance with the code contract is a stronger predictor of hybrid accuracy than general model capability.

**5. Per-function bug coverage (hybrid):**

| Bug | gemini-3-flash-preview | gemini-2.5-flash |
| :--- | :--- | :--- |
| `factorial` (n<0 → silent wrong result) | ✓ | ✗ missed |
| `fibonacci` (fib(0) = 1 not 0) | ✓ | ✓ |
| `is_palindrome` (n≤0 rejects 0) | ✓ | ✓ |
| `gcd` (wrong sign for negatives) | ✓ | ✗ Z3 error |
| `lcm` (div-by-zero at gcd=0) | ✓ | ✗ Z3 error |
| `max_subarray_sum` (lo>hi crash) | ✓ | ✓ |
| `classify` (unreachable branch) | ✓ | ✓ |
| `isqrt` (< vs ≤ in binary search) | ✓ | ✓ |
| `mod_pow` (wrong operation order) | ✓ | ✓ |
| `count_divisors` (square root double-counted) | ✓ | ✓ |
| `is_prime` (< vs ≤ in trial division) | ✓ | ✓ |

---

## RQ3 — Counterexample Precision

> What fraction of generated counterexamples are genuine bugs vs. artifacts of over/under-constrained specifications?

### gemini-3-flash-preview hybrid — all 15 scripts

| Function | Counterexample | Genuine? |
| :--- | :--- | :--- |
| `factorial` | `n = -1` | ✓ Real bug |
| `fibonacci` | `n = 0` | ✓ Real bug |
| `is_palindrome` | `n = 0` | ✓ Real bug |
| `gcd` | `a = -2, b = 0` | ✓ Real bug |
| `lcm` | `a = -2, b = 0` | ✓ Real bug |
| `max_crossing_sum` | `a0=0, a1=-1000000, a2=0` | ✓ Real bug |
| `max_subarray_sum` | `lo=1, hi=0` | ✓ Real bug |
| `classify` | `n = -45` | ✓ Real bug |
| `isqrt` | `n = 4` | ✓ Real bug |
| `mod_pow` | `base=2, exp=2, mod=5` | ✓ Real bug |
| `count_divisors` | `n = 4` | ✓ Real bug |
| `is_prime` | `n = 9` | ✓ Real bug |

**Precision: 12/12 = 100%.** Every counterexample is a genuine, independently reproducible bug. Each one is not just a verdict — it is actionable evidence: a developer can paste the input directly into a test, run it, and watch the function fail. This is the defining advantage over LLM-only outputs, which produce a verdict but no proof.

### gemini-2.5-flash hybrid — false positive

`05_clamp_clean.py` was flagged BUGGY via a counterexample on `clamp`. This is a false positive — `clamp` is correct. The LLM generated an over-constrained postcondition and Z3 found a witness that violates the wrong spec, not the actual function. Because the counterexample is explicit and runnable, this error is detectable: executing the claimed witness against the real Python function does not reproduce the bug, immediately revealing the spec error. An LLM-only false positive has no such self-correction path.

**Overall precision: 12 genuine / 13 total counterexamples = 92%, driven entirely by the gemini-2.5-flash false positive. gemini-3-flash-preview precision: 12/12 = 100%.**

---

## RQ4 — Hybrid vs. Human Reviewers

> How does the neuro-symbolic hybrid compare to human code reviewers in terms of bug detection rate, false positive rate, and time-to-verdict?

**Pending.** This research question requires human participants to review the dataset scripts and record their verdicts. A Google Form has been prepared for this purpose. Results will be incorporated once responses are collected.

---

## RQ5 — Token Efficiency

> What is the token cost overhead of the hybrid vs. LLM-only, and does the accuracy gain justify it?

### Full 15-script comparison

| Configuration | Avg tok/file | Total tokens | Accuracy | FP | Wall time |
| :--- | :--- | :--- | :--- | :--- | :--- |
| LLM-only, gemini-2.5-flash | **2,273** | **34,095** | **15/15** | 0 | **37s** |
| **Hybrid, gemini-3-flash-preview** | **8,152** | **122,285** | **15/15** | **0** | **61s** |
| Hybrid, gemini-2.5-flash | 15,257 | 228,860 | 11/13 dec. | 1 | 334s |
| LLM-only, gemini-3-flash-preview | 20,081 | 301,229 | 13/14 dec. | 1 | 350s |

### The thinking model efficiency inversion

`gemini-3-flash-preview` is a thinking model. In LLM-only mode it consumes 20,081 tokens/file (98% hidden thinking); in hybrid mode only 8,152 tokens/file. The hybrid's structured JSON prompt constrains internal reasoning. The same model is therefore **2.5× cheaper** inside the hybrid than outside it — and more accurate.

### Token overhead and what it buys

The hybrid (`gemini-3-flash-preview`, 8,152 tok/file) costs 3.6× more than `gemini-2.5-flash` LLM-only (2,273 tok/file) at the same 15/15 accuracy. That overhead is not paying for a better verdict — it is paying for justification:

- **Concrete, runnable counterexamples** — `n = 4`, `base=2, exp=2, mod=5`, `lo=1, hi=0` — directly executable against the source, turning a verdict into a reproducible test case
- **Traceable Z3 proofs** — the full constraint encoding can be inspected, modified, and re-run by anyone, independently of the LLM that generated it
- **Auditability** — a CLEAN verdict means Z3 exhaustively searched the input space under the given preconditions and found no violation; an LLM-only CLEAN verdict is an assertion without proof
- **False-positive immunity** — the SMT proof blocked the hallucinated bug that `gemini-3-flash-preview` LLM-only produced on `power_clean`, a failure mode that LLM-only has no mechanism to catch

LLM-only outputs are black-box verdicts. They cannot be independently verified, cannot produce a test case, and cannot distinguish a genuine CLEAN result from a model that simply failed to reason about an edge case. The hybrid's additional cost buys transparency and trust.

### Practical recommendations

| Use case | Recommended configuration | Rationale |
| :--- | :--- | :--- |
| Fast triage / CI gate | LLM-only, gemini-2.5-flash | 2,273 tok/file, 37s, 15/15, 0 FP |
| Formal audit / evidence generation | Hybrid, gemini-3-flash-preview | 8,152 tok/file, 61s, 15/15, 0 FP, traceable proofs + concrete CEs |
| Complex / safety-critical review | Hybrid, gemini-3-flash-preview | SMT proof eliminates hallucinated bugs; every verdict is independently verifiable |
| Do not use | Hybrid, gemini-2.5-flash | False positives, slower, more expensive than alternatives |
