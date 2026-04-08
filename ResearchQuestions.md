# Research Questions

**RQ1 — LLM-Only vs. Hybrid**
Does the neuro-symbolic hybrid (LLM + Z3 SMT solver) achieve higher bug detection accuracy than using an LLM alone to judge code correctness?

**RQ2 — LLM Model Sensitivity**
How does the choice of underlying LLM (capability tier) affect contract quality, measured by parse success rate, false positive rate, and correct bug detection?

**RQ3 — Counterexample Precision**
What fraction of generated counterexamples are genuine bugs (true positives) versus artifacts of over/under-constrained LLM-generated specifications (false positives/negatives)?

**RQ4 — Hybrid vs. Human Reviewers**
How does the neuro-symbolic hybrid compare to human code reviewers in terms of bug detection rate, false positive rate, and time-to-verdict?

**RQ5 — Token Efficiency**
What is the token cost overhead of the hybrid approach (LLM + Z3) compared to LLM-only verification, and does the accuracy gain justify the additional token expenditure?
