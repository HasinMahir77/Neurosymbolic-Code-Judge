from __future__ import annotations

import subprocess
import sys
import tempfile
from pathlib import Path

from nsjudge.config import Settings
from nsjudge.schemas import Z3Result


class ConstraintSandbox:
    """Executes LLM-generated Z3 scripts in isolated subprocesses."""

    def __init__(self, settings: Settings) -> None:
        self._timeout = settings.sandbox_timeout_seconds

    def execute(self, function_name: str, z3_script: str) -> Z3Result:
        """Run a Z3 script and parse its output."""
        tmp_path: Path | None = None
        try:
            with tempfile.NamedTemporaryFile(
                mode="w", suffix=".py", delete=False
            ) as f:
                f.write(z3_script)
                tmp_path = Path(f.name)

            result = subprocess.run(
                [sys.executable, str(tmp_path)],
                capture_output=True,
                text=True,
                timeout=self._timeout,
            )

            return self._parse_output(function_name, result)

        except subprocess.TimeoutExpired:
            return Z3Result(
                function_name=function_name,
                status="timeout",
                error_message=f"Z3 script timed out after {self._timeout}s",
            )
        except Exception as e:
            return Z3Result(
                function_name=function_name,
                status="error",
                error_message=str(e),
            )
        finally:
            if tmp_path is not None:
                tmp_path.unlink(missing_ok=True)

    def _parse_output(
        self, function_name: str, result: subprocess.CompletedProcess[str]
    ) -> Z3Result:
        """Parse subprocess output into a Z3Result."""
        stdout = result.stdout.strip()
        stderr = result.stderr.strip()

        if result.returncode != 0:
            return Z3Result(
                function_name=function_name,
                status="error",
                error_message=stderr or f"Process exited with code {result.returncode}",
                raw_output=stdout,
            )

        if "VERIFIED" in stdout:
            return Z3Result(
                function_name=function_name,
                status="verified",
                raw_output=stdout,
            )

        if "COUNTEREXAMPLE" in stdout:
            counterexample = self._parse_counterexample(stdout)
            return Z3Result(
                function_name=function_name,
                status="counterexample",
                counterexample=counterexample,
                raw_output=stdout,
            )

        return Z3Result(
            function_name=function_name,
            status="error",
            error_message="Unexpected output: script did not print VERIFIED or COUNTEREXAMPLE",
            raw_output=stdout,
        )

    @staticmethod
    def _parse_counterexample(stdout: str) -> dict[str, str]:
        """Extract variable assignments from COUNTEREXAMPLE output."""
        counterexample: dict[str, str] = {}
        in_counterexample = False

        for line in stdout.splitlines():
            line = line.strip()
            if line == "COUNTEREXAMPLE":
                in_counterexample = True
                continue
            if in_counterexample and "=" in line:
                key, _, value = line.partition("=")
                counterexample[key.strip()] = value.strip()

        return counterexample
