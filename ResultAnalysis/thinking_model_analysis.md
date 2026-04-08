# Thinking Model Analysis: gemini-3-flash-preview

## Discovery

During benchmark profiling, the `gemini-3-flash-preview` model was found to consume 97% of its
token budget on **internal reasoning** before producing any output. This is characteristic of
a *thinking model* (analogous to OpenAI o1/o3) — the model silently runs a chain-of-thought
before generating a response.

### Measured Token Breakdown (per function, thinking enabled)

| Token Type | Count | Share |
| :--- | :--- | :--- |
| Thinking (internal reasoning) | ~62,900 | **97%** |
| Prompt (system + function source) | ~1,100 | 2% |
| Output (Z3 script + contract) | ~650 | 1% |
| **Total** | **~64,650** | 100% |

This explained the benchmark runtime anomaly: **4,752 seconds** for 28 functions (~170s/function),
despite Z3 execution averaging only **0.09 seconds per script**.

---

## Thinking Budget Behaviour

The `thinking_budget` parameter does not behave as a simple hard cap. It acts more like
a **minimum effort floor**: if the task requires more reasoning than the budget permits,
the model ignores the limit entirely. The effective behaviour, measured on a complex
function (GCD via Euclidean algorithm):

| `thinking_budget` | API time | Thinking tokens | Z3 result |
| :--- | :--- | :--- | :--- |
| `0` or `1024` | ~5s | 0 (disabled) | COUNTEREXAMPLE ✓ |
| `4096` | ~247s | 62,913 *(cap ignored)* | COUNTEREXAMPLE ✓ |
| `8192` | ~245s | 62,913 *(cap ignored)* | Z3 error |
| **`16384`** | **~47s** | **~8,000** | **COUNTEREXAMPLE ✓** |
| `-1` (unlimited) | ~250s | ~63,000 | COUNTEREXAMPLE ✓ |

Key observations:
- Values ≤ 1024 disable thinking entirely (same as `0`).
- Values 4096–8192 are silently ignored for complex functions; the model runs unconstrained.
- **16384 is the effective minimum cap** that the model respects (~8k tokens, ~47s).
- `ThinkingLevel` enum values (`LOW`, `MEDIUM`, `HIGH`, `MINIMAL`) were also tested.
  `MINIMAL` behaves identically to `budget=0`. `LOW` and `MEDIUM` triggered full thinking.

## Performance Tiers

| Mode | `thinking_budget` | API time | Tokens/call | Benchmark total (est.) |
| :--- | :--- | :--- | :--- | :--- |
| Fast | `0` | ~5–7s | ~2,000 | ~150–250s |
| **Balanced** | **`16384`** | **~15–50s** | **~2k–8k** | **~600–1,200s** |
| Full | `-1` | ~250s | ~64,700 | ~4,750s |

Default is now `16384` (balanced). The budget is ignored below ~16k for complex functions,
making values in that range effectively identical to unlimited thinking.

---

## Accuracy Trade-off

Disabling thinking reduces reasoning depth. Based on the model comparison benchmark:

| Mode | Verified | Bugs Found | Errors |
| :--- | :--- | :--- | :--- |
| Thinking enabled | 17 | 11 | 0 |
| Thinking disabled *(projected)* | ~13–15 | ~8–11 | ~1–4 |

The thinking model's main advantages were:
- Zero JSON/syntax errors (prompt following)
- Correct handling of unbounded loops (invariant-based Z3 modeling)
- No false positives on clean programs

---

## Configuration

`thinking_budget` is now a first-class setting in `nsjudge/config.py`:

```
THINKING_BUDGET=0     # Fast mode (~5s/call) — for development and iteration
THINKING_BUDGET=-1    # Full thinking (~250s/call) — for final benchmark runs
```

Set via `.env` or environment variable. Default is `0` (fast).

---

## Additional Changes in This Session

### Prompt Engineering (`nsjudge/prompts.py`)
Three new sections added to `SYSTEM_PROMPT` to address observed failure modes:

1. **Handling Loops and Recursion** — bans `ForAll` quantifiers (caused Z3 timeouts on GCD
   and `power`); instructs the model to use invariant-based modeling or bounded `If`-chain
   unrolling instead.

2. **Avoiding Z3 Incompleteness** — bans `ForAll` for array sums (caused false negatives
   on `compute_sum`); instructs use of concrete 3–5 element symbolic arrays.

3. **Boundary Conditions** — keep preconditions minimal; test `n=0`, negatives, and
   divisibility combinations (e.g., `n=15` for FizzBuzz).

### Structured Output (`nsjudge/semantic_translator.py`)
Added `response_schema=FunctionContract` to `GenerateContentConfig`. Forces Gemini to
return strictly valid JSON matching the schema, eliminating the `Extra data` parse errors
that appeared on `09_fizzbuzz.py`.

### Parallel Benchmark Runner (`run.py`)
Replaced sequential `subprocess.run()` loop with `ThreadPoolExecutor(max_workers=5)`.
All 10 dataset files now run concurrently. Expected wall-time reduction: ~5x.

---

## RQ5 Implication (Token Efficiency)

The thinking model creates a sharp token-efficiency cliff:

- **Thinking disabled:** ~2,000 tokens/function — comparable to a standard LLM call
- **Thinking enabled:** ~65,000 tokens/function — 32x higher, with most tokens never
  visible in the output

For RQ5 analysis, token counts should be reported separately for thinking vs. non-thinking
configurations, as they represent fundamentally different cost profiles.
