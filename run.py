import os
import sys
import json
import glob
import time
import subprocess

RESULTS_DIR = os.path.join("ResultAnalysis", "Benchmarks")


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
    print("==================================================")
    
    total_files = len(test_files)
    results = []
    start_time = time.time()

    for idx, f in enumerate(test_files, start=1):
        print(f"\n[{idx}/{total_files}] Evaluating {f} ...")
        
        # We run the command and request JSON output for easy aggregation
        cmd = ["nsjudge", f, "--json"]
        
        try:
            # capture_output to parse json, but user won't see LLM progression real-time.
            # To fix this, we'll let nsjudge run, but nsjudge's --json flag makes it mostly silent until the end.
            proc = subprocess.run(cmd, capture_output=True, text=True)
            
            if proc.returncode != 0 and not proc.stdout.strip():
                print(f"  -> Process Error:")
                print(proc.stderr)
                results.append({"file": f, "status": "ProcessError", "error": proc.stderr})
                continue
            
            # Extract JSON from stdout
            try:
                output_json = json.loads(proc.stdout)
                summary = output_json.get("summary", "No summary")
                print(f"  -> {summary}")
                
                results.append({
                    "file": f,
                    "status": "Completed",
                    "verified": len(output_json.get("verified", [])),
                    "counterexamples": len(output_json.get("counterexamples", [])),
                    "errors": len(output_json.get("errors", [])),
                    "raw_data": output_json
                })
            except json.JSONDecodeError:
                print("  -> Could not parse JSON output. Raw output was:")
                print(proc.stdout)
                if proc.stderr: print("Stderr:", proc.stderr)
                
                results.append({"file": f, "status": "ParseError", "raw_stdout": proc.stdout})

        except Exception as e:
            print(f"  -> Execution Failed: {e}")
            results.append({"file": f, "status": "Exception", "error": str(e)})

    # Print Summary Table
    elapsed = time.time() - start_time
    print("\n==================================================")
    print(f"Benchmark Completed in {elapsed:.2f} seconds")
    print("==================================================")
    
    total_verified = 0
    total_counterexamples = 0
    total_errors = 0
    
    print(f"{'File':<25} | {'Verified':<8} | {'Bugs Found':<10} | {'Errors':<6}")
    print("-" * 59)
    for r in results:
        file_base = os.path.basename(r.get("file", ""))
        if r.get("status") == "Completed":
            v = r.get("verified", 0)
            ce = r.get("counterexamples", 0)
            err = r.get("errors", 0)
            total_verified += v
            total_counterexamples += ce
            total_errors += err
            print(f"{file_base:<25} | {v:<8} | {ce:<10} | {err:<6}")
        else:
            print(f"{file_base:<25} | Status: {r.get('status')}")
            
    print("-" * 59)
    print(f"{'TOTALS':<25} | {total_verified:<8} | {total_counterexamples:<10} | {total_errors:<6}")
    print("==================================================\n")

    # Save aggregated JSON
    json_path = os.path.join(RESULTS_DIR, "benchmark_results.json")
    with open(json_path, "w") as f:
        json.dump(results, f, indent=2)
    print(f"Detailed results saved to {json_path}")

    # Generate and save Markdown table
    md_content = ["# Benchmark Results\n"]
    md_content.append(f"**Total Time:** {elapsed:.2f} seconds\n")
    md_content.append("| File | Verified | Bugs Found | Errors |")
    md_content.append("| :--- | :--- | :--- | :--- |")

    for r in results:
        file_base = os.path.basename(r.get("file", ""))
        if r.get("status") == "Completed":
            v = r.get("verified", 0)
            ce = r.get("counterexamples", 0)
            err = r.get("errors", 0)
            md_content.append(f"| {file_base} | {v} | {ce} | {err} |")
        else:
            md_content.append(f"| {file_base} | {r.get('status')} | | |")

    md_content.append(f"| **TOTALS** | **{total_verified}** | **{total_counterexamples}** | **{total_errors}** |")

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
