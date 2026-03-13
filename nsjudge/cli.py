from __future__ import annotations

import argparse
import sys

from nsjudge.config import Settings
from nsjudge.orchestrator import Orchestrator
from nsjudge.schemas import Z3Result


def main() -> None:
    parser = argparse.ArgumentParser(
        prog="nsjudge",
        description="Neuro-Symbolic Code Judge: verify Python programs using LLM + Z3",
    )
    parser.add_argument("file", help="Path to the Python file to verify")
    parser.add_argument(
        "-v", "--verbose", action="store_true", help="Show Z3 scripts and LLM reasoning"
    )
    parser.add_argument(
        "--json", action="store_true", help="Output raw JSON report"
    )
    args = parser.parse_args()

    try:
        settings = Settings()
    except Exception as e:
        print(f"Configuration error: {e}", file=sys.stderr)
        print("Ensure GEMINI_API_KEY is set (via .env or environment).", file=sys.stderr)
        sys.exit(1)

    if not settings.gemini_api_key:
        print("Error: GEMINI_API_KEY is not set.", file=sys.stderr)
        print("Set it in a .env file or as an environment variable.", file=sys.stderr)
        sys.exit(1)

    orchestrator = Orchestrator(settings)

    if not args.json:
        print("Neuro-Symbolic Code Judge")
        print("=" * 40)
        print(f"File: {args.file}")
        print()

    def on_progress(index: int, total: int, func_name: str, result: Z3Result) -> None:
        if args.json:
            return
        status_icon = {
            "verified": "VERIFIED",
            "counterexample": "COUNTEREXAMPLE FOUND",
            "error": "ERROR",
            "timeout": "TIMEOUT",
        }[result.status]

        print(f"[{index}/{total}] {func_name} ... {status_icon}")

        if result.status == "counterexample" and result.counterexample:
            for var, val in result.counterexample.items():
                print(f"      {var} = {val}")

        if result.status == "error" and result.error_message:
            print(f"      {result.error_message}")

        if args.verbose and result.raw_output:
            print(f"      Raw: {result.raw_output}")

    try:
        report = orchestrator.verify_file(args.file, on_progress=on_progress)
    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Unexpected error: {e}", file=sys.stderr)
        sys.exit(1)

    if args.json:
        print(report.model_dump_json(indent=2))
    else:
        print()
        print(f"Summary: {report.summary}")


if __name__ == "__main__":
    main()
