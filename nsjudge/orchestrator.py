from __future__ import annotations

from pathlib import Path

from nsjudge.ast_ingestion import parse_file
from nsjudge.compositional import CompositionalVerifier
from nsjudge.config import Settings
from nsjudge.constraint_sandbox import ConstraintSandbox
from nsjudge.schemas import VerificationReport, VerifiedContract, Z3Result
from nsjudge.semantic_translator import SemanticTranslator


class Orchestrator:
    """Top-level pipeline: parse -> translate -> execute -> roll-up -> report."""

    def __init__(self, settings: Settings) -> None:
        self._settings = settings
        translator = SemanticTranslator(settings)
        sandbox = ConstraintSandbox(settings)
        self._verifier = CompositionalVerifier(translator, sandbox, settings)

    def verify_file(
        self,
        file_path: str,
        on_progress: callable | None = None,
    ) -> VerificationReport:
        """Verify all functions in a Python source file.

        Args:
            file_path: Path to the Python file to verify.
            on_progress: Optional callback(index, total, function_name, result)
                         called after each function is verified.
        """
        source_code = Path(file_path).read_text(encoding="utf-8")
        graph = parse_file(source_code)

        verified_deps: dict[str, VerifiedContract] = {}
        verified_list: list[VerifiedContract] = []
        counterexamples: list[Z3Result] = []
        errors: list[Z3Result] = []

        total = len(graph.verification_order)

        for i, func_name in enumerate(graph.verification_order):
            func_info = graph.functions[func_name]

            # Only pass deps that this function actually calls
            relevant_deps = {
                name: verified_deps[name]
                for name in func_info.calls
                if name in verified_deps
            }

            result, verified_contract = self._verifier.verify_function(
                func_info, relevant_deps
            )

            if verified_contract is not None:
                verified_deps[func_name] = verified_contract
                verified_list.append(verified_contract)
            elif result.status == "counterexample":
                counterexamples.append(result)
            else:
                errors.append(result)

            if on_progress:
                on_progress(i + 1, total, func_name, result)

        n_verified = len(verified_list)
        n_counter = len(counterexamples)
        n_errors = len(errors)
        summary = (
            f"{n_verified}/{total} functions verified"
            + (f", {n_counter} counterexample(s) found" if n_counter else "")
            + (f", {n_errors} error(s)" if n_errors else "")
        )

        return VerificationReport(
            file_path=file_path,
            total_functions=total,
            verified=verified_list,
            counterexamples=counterexamples,
            errors=errors,
            summary=summary,
        )
