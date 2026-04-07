from __future__ import annotations

from nsjudge.config import Settings
from nsjudge.constraint_sandbox import ConstraintSandbox
from nsjudge.schemas import (
    FunctionInfo,
    RefinementRequest,
    TokenUsage,
    VerifiedContract,
    Z3Result,
)
from nsjudge.semantic_translator import SemanticTranslator


class CompositionalVerifier:
    """Verifies functions with self-refinement and compositional roll-up."""

    def __init__(
        self,
        translator: SemanticTranslator,
        sandbox: ConstraintSandbox,
        settings: Settings,
    ) -> None:
        self._translator = translator
        self._sandbox = sandbox
        self._max_attempts = settings.max_refinement_attempts

    def verify_function(
        self,
        func_info: FunctionInfo,
        verified_deps: dict[str, VerifiedContract],
    ) -> tuple[Z3Result, VerifiedContract | None, TokenUsage]:
        """Verify a single function, using refinement if Z3 script errors.

        Returns the Z3Result, an optional VerifiedContract for roll-up, and
        the accumulated TokenUsage across all LLM calls for this function.
        """
        token_usage = TokenUsage()

        try:
            contract, usage = self._translator.generate_contract(func_info, verified_deps)
            token_usage = token_usage + usage
        except Exception as e:
            return Z3Result(
                function_name=func_info.name,
                status="error",
                error_message=f"LLM contract generation failed: {e}",
            ), None, token_usage

        result = self._sandbox.execute(func_info.name, contract.z3_script)

        attempt = 1
        while result.status == "error" and attempt < self._max_attempts:
            attempt += 1
            try:
                refinement = RefinementRequest(
                    original_contract=contract,
                    error_traceback=result.error_message or result.raw_output,
                    attempt_number=attempt,
                )
                contract, usage = self._translator.refine_contract(refinement)
                token_usage = token_usage + usage
                result = self._sandbox.execute(func_info.name, contract.z3_script)
            except Exception as e:
                result = Z3Result(
                    function_name=func_info.name,
                    status="error",
                    error_message=f"LLM refinement failed (attempt {attempt}): {e}",
                )

        if result.status == "verified":
            verified = VerifiedContract(
                function_name=func_info.name,
                contract=contract,
                z3_result=result,
            )
            return result, verified, token_usage

        return result, None, token_usage
