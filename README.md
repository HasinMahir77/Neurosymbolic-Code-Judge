# Neuro-Symbolic Code Judge

A hybrid verification framework that combines LLM semantic understanding (Gemini) with Z3 SMT solver formal verification to automatically detect bugs in Python programs.

## How It Works

The system takes a single-file Python program with a `main()` entry point and mathematically proves whether each function behaves correctly — or produces a concrete counterexample demonstrating the bug.

### Data Flow

```
┌─────────────────────────────────────────────────────────────────────┐
│                        INPUT: Python Source File                    │
│                     (single file with main() entry)                │
└──────────────────────────────┬──────────────────────────────────────┘
                               │
                               ▼
┌──────────────────────────────────────────────────────────────────────┐
│                    1. AST INGESTION MODULE                          │
│                       (ast_ingestion.py)                            │
│                                                                     │
│   • Parses source code into Abstract Syntax Tree                   │
│   • Extracts all top-level function definitions                    │
│   • Builds a call graph of internal function dependencies          │
│   • Topologically sorts functions (Kahn's algorithm)               │
│                                                                     │
│   Output: DependencyGraph                                          │
│     - functions: {name → FunctionInfo(source, args, calls)}        │
│     - verification_order: [leaf_fn, ..., main]                     │
└──────────────────────────────┬──────────────────────────────────────┘
                               │
                               ▼
┌──────────────────────────────────────────────────────────────────────┐
│            2. BOTTOM-UP VERIFICATION LOOP                          │
│                  (orchestrator.py)                                  │
│                                                                     │
│   For each function in verification_order (leaves first):          │
│                                                                     │
│   ┌────────────────────────────────────────────────────────────┐   │
│   │  2a. SEMANTIC TRANSLATION ENGINE (semantic_translator.py)  │   │
│   │                                                            │   │
│   │  Sends to Gemini LLM:                                     │   │
│   │    • Function source code                                  │   │
│   │    • Contracts of already-verified dependencies (axioms)   │   │
│   │    • System prompt with negation strategy                  │   │
│   │                                                            │   │
│   │  Receives back (structured JSON):                          │   │
│   │    • Preconditions (human-readable)                        │   │
│   │    • Postconditions (human-readable)                       │   │
│   │    • Complete Z3 Python script                             │   │
│   │    • Chain-of-thought reasoning                            │   │
│   └────────────────────────┬───────────────────────────────────┘   │
│                            │                                        │
│                            ▼                                        │
│   ┌────────────────────────────────────────────────────────────┐   │
│   │  2b. CONSTRAINT EXECUTION SANDBOX (constraint_sandbox.py)  │   │
│   │                                                            │   │
│   │  • Writes Z3 script to temp file                           │   │
│   │  • Executes in isolated subprocess (30s timeout)           │   │
│   │  • Parses stdout for VERIFIED or COUNTEREXAMPLE            │   │
│   └────────────────────────┬───────────────────────────────────┘   │
│                            │                                        │
│                            ▼                                        │
│   ┌────────────────────────────────────────────────────────────┐   │
│   │  2c. SELF-REFINEMENT LOOP (compositional.py)               │   │
│   │                                                            │   │
│   │  If Z3 script errored (syntax/runtime):                    │   │
│   │    → Feed traceback back to LLM                            │   │
│   │    → LLM produces corrected script                         │   │
│   │    → Re-execute in sandbox                                 │   │
│   │    → Repeat up to 3 attempts                               │   │
│   └────────────────────────┬───────────────────────────────────┘   │
│                            │                                        │
│                            ▼                                        │
│   ┌────────────────────────────────────────────────────────────┐   │
│   │  2d. COMPOSITIONAL ROLL-UP                                 │   │
│   │                                                            │   │
│   │  If VERIFIED:                                              │   │
│   │    → Store contract as axiom for parent functions           │   │
│   │    → Parents verify against the contract, not the code     │   │
│   │    → Prevents state-space explosion                        │   │
│   │                                                            │   │
│   │  If COUNTEREXAMPLE:                                        │   │
│   │    → Record bug with concrete variable assignments         │   │
│   └────────────────────────────────────────────────────────────┘   │
│                                                                     │
└──────────────────────────────┬──────────────────────────────────────┘
                               │
                               ▼
┌──────────────────────────────────────────────────────────────────────┐
│                     3. VERIFICATION REPORT                         │
│                                                                     │
│   • Per-function status: VERIFIED / COUNTEREXAMPLE / ERROR         │
│   • Concrete counterexample values for each bug found              │
│   • Summary statistics                                             │
│   • Available as human-readable text or JSON                       │
└──────────────────────────────────────────────────────────────────────┘
```

### Core Mathematical Principle

For each function, the system defines:
- **Preconditions (P):** constraints on valid inputs
- **Postconditions (Q):** expected properties of outputs

Instead of proving `P → Q` directly, the Z3 solver checks the **negation**: "Does there exist an input satisfying P where Q is violated?"

- **`unsat`** → No such input exists → function is **mathematically proven correct**
- **`sat`** → A violating input exists → Z3 produces a **concrete counterexample** (the bug)

## Setup

### Prerequisites
- Python 3.12+
- Conda (recommended)

### Installation

```bash
conda create -n nsjudge python=3.12 -y
conda activate nsjudge
pip install -e ".[dev]"
```

### Configuration

Create a `.env` file in the project root:

```
GEMINI_API_KEY=your-gemini-api-key
```

## Usage

```bash
# Basic verification
nsjudge path/to/program.py

# Verbose output (shows Z3 scripts and LLM reasoning)
nsjudge path/to/program.py -v

# JSON output (machine-readable report)
nsjudge path/to/program.py --json
```

### Input Requirements

- Single Python file
- Must contain a top-level `main()` function
- All functions to verify must be defined at the module level

### Example Output

```
Neuro-Symbolic Code Judge
========================================
File: dataset/09_fizzbuzz.py

[1/3] classify ... COUNTEREXAMPLE FOUND
      n = 15
[2/3] run_fizzbuzz ... VERIFIED
[3/3] main ... VERIFIED

Summary: 1/3 functions verified, 1 counterexample(s) found
```

## Running Tests

```bash
conda activate nsjudge
pytest tests/ -v
```

## Dataset

The `dataset/` directory contains 10 test programs for evaluating the framework. Programs are a mix of intentionally buggy code and correct implementations.

### Buggy Programs

| # | File | Bug Type | Description |
|---|------|----------|-------------|
| 01 | `01_binary_search.py` | Integer overflow | `(lo + hi) // 2` overflows for large indices. Should be `lo + (hi - lo) // 2`. |
| 02 | `02_factorial.py` | Missing input guard | `factorial(n)` silently returns 1 for negative `n` instead of raising an error or returning a defined value. |
| 03 | `03_average.py` | Off-by-one | `compute_sum` starts accumulation from `numbers[0]` then iterates `range(1, count)`, which is correct for all elements but the logic is fragile — a `count=0` call would index out of bounds. |
| 04 | `04_is_palindrome.py` | Missing input guard | `is_palindrome(-121)` should return `False` but `reverse_number` loops forever on negative input (the `while n > 0` never triggers). |
| 06 | `06_gcd.py` | Division by zero | `lcm(0, 0)` divides by `gcd(0, 0) = 0`. Also, `gcd` with negative inputs may return negative values. |
| 07 | `07_max_subarray.py` | Missing base case | `max_subarray_sum` has no guard for `lo > hi` (empty range), causing index errors when called on empty subarrays. |
| 09 | `09_fizzbuzz.py` | Unreachable branch | The `n % 15 == 0` check comes after separate `n % 3` and `n % 5` checks, so "FizzBuzz" is never returned — `n=15` returns "Fizz". |

### Clean Programs (No Bugs)

| # | File | Description |
|---|------|-------------|
| 05 | `05_clamp_clean.py` | Clamp, scale, and process pipeline — all correct. |
| 08 | `08_power_clean.py` | Fast exponentiation by squaring — correct for `exp >= 0`. |
| 10 | `10_abs_diff.py` | Absolute value and absolute difference — correct. |

## Project Structure

```
nsjudge/
├── cli.py                    # CLI entry point (argparse)
├── orchestrator.py           # Top-level pipeline coordinator
├── ast_ingestion.py          # AST parsing, dependency graph, topological sort
├── semantic_translator.py    # Gemini LLM integration for contract generation
├── constraint_sandbox.py     # Subprocess-isolated Z3 script execution
├── compositional.py          # Self-refinement loop + compositional roll-up
├── schemas.py                # All Pydantic data models
├── prompts.py                # LLM prompt templates
└── config.py                 # Settings (API key, model, timeouts)

dataset/                      # Test programs (7 buggy, 3 clean)
tests/                        # Unit and integration tests
```

## Known Limitations

- **Loops and recursion:** Z3 may time out on functions with complex loops or deep recursion, as these require modeling unbounded computation.
- **Data structures:** Lists, dictionaries, and strings are abstracted into simpler Z3-compatible representations (e.g., length as `Int`), so some data-structure bugs may be missed.
- **LLM variability:** Results are non-deterministic across runs due to LLM output variance. The self-refinement loop mitigates syntax errors but not semantic mismodeling.
- **Single-file scope:** Only verifies functions within one file. External imports and standard library calls are not modeled.

