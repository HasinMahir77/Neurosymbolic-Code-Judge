"""
LLM-only baseline for RQ1.

Sends each dataset script to the LLM with a single prompt asking for a
BUGGY/CLEAN verdict — no Z3 involved. Compares against ground truth and
reports accuracy, token usage, and per-file verdicts.
"""

import os
import sys
import json
import glob
import time
import argparse
from concurrent.futures import ThreadPoolExecutor, as_completed

from google import genai
from google.genai import types
from pydantic import BaseModel

RESULTS_DIR = os.path.join("ResultAnalysis", "LLMOnly")
MAX_PARALLEL = 5

GROUND_TRUTH = {
    "01_binary_search.py": "CLEAN",
    "02_factorial.py": "BUGGY",
    "03_fibonacci.py": "BUGGY",
    "04_is_palindrome.py": "BUGGY",
    "05_clamp_clean.py": "CLEAN",
    "06_gcd.py": "BUGGY",
    "07_max_subarray.py": "BUGGY",
    "08_power_clean.py": "CLEAN",
    "09_fizzbuzz.py": "BUGGY",
    "10_abs_diff_clean.py": "CLEAN",
}

SYSTEM_PROMPT = """\
You are an expert Python code reviewer. Your task is to carefully read a Python \
script and determine whether any of its non-main functions contain bugs that \
produce incorrect output for valid inputs.

A function is BUGGY if there exists any valid input for which it returns a wrong \
result, raises an unexpected exception, or silently produces an incorrect value.

A file is BUGGY if ANY non-main function is buggy.
A file is CLEAN if ALL non-main functions are correct for all valid inputs.

Important notes:
- Python integers are arbitrary precision — there is no 32-bit or 64-bit overflow.
- Evaluate based on Python semantics, not C or Java.
- Negative numbers, zero, and boundary values are valid inputs unless the \
  docstring explicitly forbids them.
- Do not flag main() — it is a test harness.
"""

USER_PROMPT_TEMPLATE = """\
Analyze the following Python script for bugs:

```python
{source}
```

Respond with a JSON object:
{{
  "verdict": "BUGGY" or "CLEAN",
  "reasoning": "concise analysis of each non-main function",
  "buggy_functions": [
    {{"name": "function_name", "bug": "description", "counterexample": "concrete input that triggers the bug"}}
  ]
}}
If the file is CLEAN, set "buggy_functions" to an empty list.
"""


class LLMVerdict(BaseModel):
    verdict: str  # "BUGGY" or "CLEAN"
    reasoning: str
    buggy_functions: list[dict]


def _evaluate_file(filepath: str, model: str, client: genai.Client) -> dict:
    filename = os.path.basename(filepath)
    with open(filepath) as f:
        source = f.read()

    prompt = USER_PROMPT_TEMPLATE.format(source=source)
    start = time.time()
    try:
        response = client.models.generate_content(
            model=model,
            contents=prompt,
            config=types.GenerateContentConfig(
                system_instruction=SYSTEM_PROMPT,
                response_mime_type="application/json",
                temperature=0.1,
            ),
        )
        elapsed = time.time() - start

        usage = response.usage_metadata
        tokens = {
            "prompt_tokens": usage.prompt_token_count or 0,
            "completion_tokens": usage.candidates_token_count or 0,
            "total_tokens": usage.total_token_count or 0,
        }

        raw_text = response.text or ""
        # Strip markdown fences if present
        if "```" in raw_text:
            import re
            m = re.search(r"```(?:json)?\s*([\s\S]*?)```", raw_text)
            if m:
                raw_text = m.group(1).strip()
        try:
            data = json.loads(raw_text)
        except Exception:
            data = {"verdict": "ERROR", "reasoning": raw_text, "buggy_functions": []}

        verdict = data.get("verdict", "ERROR").upper()
        if verdict not in ("BUGGY", "CLEAN"):
            verdict = "ERROR"

        return {
            "file": filename,
            "verdict": verdict,
            "ground_truth": GROUND_TRUTH.get(filename, "UNKNOWN"),
            "reasoning": data.get("reasoning", ""),
            "buggy_functions": data.get("buggy_functions", []),
            "tokens": tokens,
            "elapsed_s": round(elapsed, 2),
        }
    except Exception as e:
        elapsed = time.time() - start
        return {
            "file": filename,
            "verdict": "ERROR",
            "ground_truth": GROUND_TRUTH.get(filename, "UNKNOWN"),
            "reasoning": str(e),
            "buggy_functions": [],
            "tokens": {"prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0},
            "elapsed_s": round(elapsed, 2),
        }


def run_llm_only_benchmark(model: str):
    os.makedirs(RESULTS_DIR, exist_ok=True)

    api_key = os.environ.get("GEMINI_API_KEY", "")
    if not api_key:
        # Try reading from .env
        if os.path.exists(".env"):
            for line in open(".env"):
                if line.startswith("GEMINI_API_KEY="):
                    api_key = line.split("=", 1)[1].strip()
    if not api_key:
        print("Error: GEMINI_API_KEY not set.")
        sys.exit(1)

    client = genai.Client(api_key=api_key)

    test_files = sorted(glob.glob(os.path.join("dataset", "*.py")))
    if not test_files:
        print("No python files found in dataset/.")
        sys.exit(0)

    print("==================================================")
    print("  LLM-Only Baseline")
    print(f"  Model: {model}")
    print(f"  Files: {len(test_files)} ({MAX_PARALLEL} parallel)")
    print("==================================================")

    start_time = time.time()
    results_map: dict[str, dict] = {}

    with ThreadPoolExecutor(max_workers=MAX_PARALLEL) as executor:
        future_to_file = {
            executor.submit(_evaluate_file, f, model, client): f for f in test_files
        }
        completed = 0
        for future in as_completed(future_to_file):
            completed += 1
            f = future_to_file[future]
            result = future.result()
            results_map[f] = result
            gt = result["ground_truth"]
            v = result["verdict"]
            match = "✓" if v == gt else "✗"
            print(
                f"  [{completed}/{len(test_files)}] {result['file']}: "
                f"{v} (truth={gt}) {match}  ({result['elapsed_s']}s)"
            )

    total_elapsed = time.time() - start_time
    results = [results_map[f] for f in test_files]

    # Compute metrics
    tp = sum(1 for r in results if r["verdict"] == "BUGGY" and r["ground_truth"] == "BUGGY")
    tn = sum(1 for r in results if r["verdict"] == "CLEAN" and r["ground_truth"] == "CLEAN")
    fp = sum(1 for r in results if r["verdict"] == "BUGGY" and r["ground_truth"] == "CLEAN")
    fn = sum(1 for r in results if r["verdict"] == "CLEAN" and r["ground_truth"] == "BUGGY")
    errors = sum(1 for r in results if r["verdict"] == "ERROR")
    total_tokens = sum(r["tokens"]["total_tokens"] for r in results)
    avg_tokens = total_tokens // len(results) if results else 0

    print(f"\n{'File':<25} | {'Verdict':<8} | {'Truth':<8} | {'Match':<6} | Tokens")
    print("-" * 75)
    for r in results:
        match = "✓" if r["verdict"] == r["ground_truth"] else "✗"
        print(
            f"{r['file']:<25} | {r['verdict']:<8} | {r['ground_truth']:<8} | "
            f"{match:<6} | {r['tokens']['total_tokens']:>6,}"
        )
    print("-" * 75)
    buggy = sum(1 for r in results if r["ground_truth"] == "BUGGY")
    clean = sum(1 for r in results if r["ground_truth"] == "CLEAN")
    print(f"  True Positives:  {tp} / {buggy}")
    print(f"  True Negatives:  {tn} / {clean}")
    print(f"  False Positives: {fp}")
    print(f"  False Negatives: {fn}")
    print(f"  Errors:          {errors}")
    print(f"  Accuracy:        {(tp + tn)}/{len(results)}")
    print(f"  Total tokens:    {total_tokens:,}")
    print(f"  Avg tokens/file: {avg_tokens:,}")
    print(f"  Wall time:       {total_elapsed:.1f}s")
    print("==================================================\n")

    safe_model = model.replace("/", "-")
    json_path = os.path.join(RESULTS_DIR, f"llm_only_{safe_model}.json")
    with open(json_path, "w") as f:
        json.dump(
            {
                "model": model,
                "results": results,
                "summary": {
                    "tp": tp, "tn": tn, "fp": fp, "fn": fn,
                    "errors": errors,
                    "accuracy": f"{tp + tn}/{len(results)}",
                    "total_tokens": total_tokens,
                    "avg_tokens_per_file": avg_tokens,
                    "wall_time_s": round(total_elapsed, 2),
                },
            },
            f,
            indent=2,
        )
    print(f"Results saved to {json_path}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="LLM-only baseline runner")
    parser.add_argument("--model", "-m", required=True, help="Gemini model name")
    args = parser.parse_args()
    run_llm_only_benchmark(args.model)
