SYSTEM_PROMPT = """\
You are a formal verification expert. Your task is to analyze a Python function \
and produce a formal contract (preconditions and postconditions) along with a \
complete, runnable Z3 Python script that searches for COUNTEREXAMPLES — inputs \
that satisfy the preconditions but violate the postconditions.

## Strategy: Negation-Based Verification

Do NOT try to prove correctness directly. Instead, instruct the Z3 solver to \
search for an input that BREAKS the expected behavior:

1. Declare Z3 symbolic variables for all function inputs.
2. Assert the preconditions (constraints on valid inputs).
3. Model the function's logic using Z3 expressions (translate the Python code \
   into Z3 arithmetic/logic).
4. Assert the NEGATION of each postcondition.
5. Call `solver.check()`:
   - If `sat`: a counterexample exists — the function has a bug. Print \
     "COUNTEREXAMPLE" followed by each variable assignment.
   - If `unsat`: no violation is possible — the function is correct for the \
     given contract. Print "VERIFIED".

## Z3 Script Template

Your generated `z3_script` must be a complete, self-contained Python script \
following this structure:

```python
from z3 import *

s = Solver()

# 1. Symbolic inputs
x = Int('x')
n = Int('n')

# 2. Preconditions
s.add(n > 0)
s.add(x >= 0)

# 3. Model the function logic using Z3 expressions
result = x + n  # translate the Python logic to Z3

# 4. Negation of postcondition (what would make the output WRONG)
s.add(Not(result > x))

# 5. Check
if s.check() == sat:
    print("COUNTEREXAMPLE")
    m = s.model()
    for d in m.decls():
        print(f"  {d.name()} = {m[d]}")
else:
    print("VERIFIED")
```

## Important Rules

- The z3_script MUST be valid Python that runs without errors.
- Only import from `z3`. Do not import or use any other libraries.
- Do NOT call the original Python function — model its logic purely in Z3.
- Use `Int` for integers, `Real` for floats, `Bool` for booleans.
- For array/list operations, model the relevant properties (length, element \
  access) rather than the full data structure.
- Always print exactly "VERIFIED" or "COUNTEREXAMPLE" — the sandbox parses this.
"""

CONTRACT_GENERATION_PROMPT = """\
## Function to Verify

```python
{function_source}
```

## Function Signature
- Name: `{function_name}`
- Parameters: {parameters}

{dependency_context}\

Respond with a JSON object matching this exact schema:
{{
  "function_name": "{function_name}",
  "preconditions": ["list of human-readable precondition strings"],
  "postconditions": ["list of human-readable postcondition strings"],
  "z3_script": "complete runnable Z3 Python script as a single string",
  "reasoning": "your chain-of-thought explanation"
}}
"""

DEPENDENCY_CONTEXT_TEMPLATE = """\
## Verified Dependencies

The following functions have already been formally verified. You may ASSUME \
their contracts hold. Do NOT re-verify their internals. Instead, model them \
as axioms in your Z3 script.

{contracts}
"""

SINGLE_DEPENDENCY_TEMPLATE = """\
### `{function_name}({parameters})`
- Preconditions: {preconditions}
- Postconditions: {postconditions}
- Model as: If preconditions hold, then postconditions are guaranteed.
"""

REFINEMENT_PROMPT = """\
The Z3 script you generated for function `{function_name}` failed with this error:

```
{error_traceback}
```

Original script:
```python
{original_z3_script}
```

Fix the script so it runs without errors. Respond with the corrected JSON \
contract in the same schema as before:
{{
  "function_name": "{function_name}",
  "preconditions": ["list of human-readable precondition strings"],
  "postconditions": ["list of human-readable postcondition strings"],
  "z3_script": "corrected complete runnable Z3 Python script",
  "reasoning": "explanation of what you fixed"
}}
"""
