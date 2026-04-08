import os
import sys
import json
import glob
import time
import subprocess
from concurrent.futures import ThreadPoolExecutor, as_completed

RESULTS_DIR = os.path.join("ResultAnalysis", "Benchmarks")
MAX_PARALLEL = 5  # Run up to 5 files concurrently


_NSJUDGE = os.path.join(os.path.dirname(sys.executable), "nsjudge")


def _evaluate_file(f: str) -> dict:
    """Run nsjudge on a single file and return a result dict."""
    cmd = [_NSJUDGE, f, "--json"]
    try:
        proc = subprocess.run(cmd, capture_output=True, text=True)
        if proc.returncode != 0 and not proc.stdout.strip():
            return {"file": f, "status": "ProcessError", "error": proc.stderr}
        try:
            output_json = json.loads(proc.stdout)
            return {
                "file": f,
                "status": "Completed",
                "verified": len(output_json.get("verified", [])),
                "counterexamples": len(output_json.get("counterexamples", [])),
                "errors": len(output_json.get("errors", [])),
                "raw_data": output_json,
            }
        except json.JSONDecodeError:
            return {"file": f, "status": "ParseError", "raw_stdout": proc.stdout}
    except Exception as e:
        return {"file": f, "status": "Exception", "error": str(e)}


def run_dataset_benchmark():
    os.makedirs(RESULTS_DIR, exist_ok=True)

    dataset_dir = "dataset"
    if not os.path.exists(dataset_dir) or not os.path.isdir(dataset_dir):
        print(f"Error: Could not find the '{dataset_dir}' directory.")
        sys.exit(1)

    test_files = sorted(glob.glob(os.path.join(dataset_dir, "*.py")))
    if not test_files:
        print(f"No python files found in '{dataset_dir}/'.")
        sys.exit(0)

    print("==================================================")
    print("  Neuro-Symbolic Judge - Dataset Benchmark Runner ")
    print(f"  Running {len(test_files)} files ({MAX_PARALLEL} in parallel)")
    print("==================================================")

    total_files = len(test_files)
    results_map: dict[str, dict] = {}
    start_time = time.time()

    with ThreadPoolExecutor(max_workers=MAX_PARALLEL) as executor:
        future_to_file = {executor.submit(_evaluate_file, f): f for f in test_files}
        completed = 0
        for future in as_completed(future_to_file):
            completed += 1
            f = future_to_file[future]
            result = future.result()
            results_map[f] = result
            summary = result.get("raw_data", {}).get("summary", result.get("status", "?"))
            elapsed = time.time() - start_time
            print(f"  [{completed}/{total_files}] {os.path.basename(f)}: {summary}  ({elapsed:.0f}s elapsed)")

    # Restore sorted order for deterministic output
    results = [results_map[f] for f in test_files]

    # Print Summary Table
    elapsed = time.time() - start_time
    print("\n==================================================")
    print(f"Benchmark Completed in {elapsed:.2f} seconds")
    print("==================================================")
    
    uncertain = 0

    def _script_verdict(r: dict) -> tuple[str, str]:
        """Return (verdict, detail) for a result, ignoring 'main' counterexamples."""
        if r.get("status") != "Completed":
            return "ERROR", r.get("status", "?")
        raw = r.get("raw_data", {})
        # Counterexamples from non-main functions only
        real_ces = [
            ce for ce in raw.get("counterexamples", [])
            if ce.get("function_name") != "main"
        ]
        err = r.get("errors", 0)
        v = r.get("verified", 0)
        if real_ces:
            fns = ", ".join(ce["function_name"] for ce in real_ces)
            return "BUGGY", f"bug in: {fns}"
        elif err > 0:
            return "UNCERTAIN", f"{v} verified, {err} error(s)"
        else:
            return "CLEAN", f"{v} function(s) verified"

    print(f"{'File':<25} | {'Verdict':<8} | {'Details'}")
    print("-" * 70)
    verdicts = {}
    for r in results:
        file_base = os.path.basename(r.get("file", ""))
        verdict, detail = _script_verdict(r)
        verdicts[file_base] = verdict
        if verdict in ("ERROR", "UNCERTAIN"):
            uncertain += 1
        print(f"{file_base:<25} | {verdict:<8} | {detail}")

    buggy_count = sum(1 for v in verdicts.values() if v == "BUGGY")
    clean_count = sum(1 for v in verdicts.values() if v == "CLEAN")
    print("-" * 70)
    print(f"  Buggy scripts detected: {buggy_count}")
    print(f"  Clean scripts verified: {clean_count}")
    print(f"  Uncertain (errors):     {uncertain}")
    print("==================================================\n")

    # Save aggregated JSON
    json_path = os.path.join(RESULTS_DIR, "benchmark_results.json")
    with open(json_path, "w") as f:
        json.dump(results, f, indent=2)
    print(f"Detailed results saved to {json_path}")

    # Generate and save Markdown table
    md_content = ["# Benchmark Results\n"]
    md_content.append(f"**Total Time:** {elapsed:.2f} seconds\n")
    md_content.append("| File | Verdict | Details |")
    md_content.append("| :--- | :--- | :--- |")

    for r in results:
        file_base = os.path.basename(r.get("file", ""))
        verdict, detail = _script_verdict(r)
        md_content.append(f"| {file_base} | {verdict} | {detail} |")

    uncertain_count = sum(1 for v in verdicts.values() if v in ("ERROR", "UNCERTAIN"))
    md_content.append("")
    md_content.append(f"**Buggy scripts detected:** {buggy_count}  ")
    md_content.append(f"**Clean scripts verified:** {clean_count}  ")
    md_content.append(f"**Uncertain (errors):** {uncertain_count}  ")

    md_path = os.path.join(RESULTS_DIR, "benchmark_results.md")
    with open(md_path, "w") as f:
        f.write("\n".join(md_content) + "\n")
    print(f"Markdown table saved to {md_path}")
def run_unit_tests():
    print("Running system unit tests via pytest...")
    subprocess.run(["pytest", "tests/", "-v"])

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] in ("--unit", "-u"):
        run_unit_tests()
    else:
        run_dataset_benchmark()
