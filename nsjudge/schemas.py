from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel


class FunctionInfo(BaseModel):
    """A single parsed function from the source file."""

    name: str
    source: str
    args: list[str]
    calls: list[str]  # Names of other internal functions this function calls
    line_start: int
    line_end: int


class DependencyGraph(BaseModel):
    """Complete parse result for a source file."""

    functions: dict[str, FunctionInfo]
    verification_order: list[str]  # Topologically sorted, leaves first
    global_code: str  # Module-level code outside functions


class FunctionContract(BaseModel):
    """LLM-generated formal contract for a function."""

    function_name: str
    preconditions: list[str]
    postconditions: list[str]
    z3_script: str  # Complete, runnable Z3 Python script
    reasoning: str


class RefinementRequest(BaseModel):
    """Sent back to LLM when a Z3 script fails execution."""

    original_contract: FunctionContract
    error_traceback: str
    attempt_number: int


class Z3Result(BaseModel):
    """Output from running one Z3 script in the sandbox."""

    function_name: str
    status: Literal["verified", "counterexample", "error", "timeout"]
    counterexample: dict[str, Any] | None = None
    error_message: str | None = None
    raw_output: str = ""


class VerifiedContract(BaseModel):
    """A function that passed verification — used for compositional roll-up."""

    function_name: str
    contract: FunctionContract
    z3_result: Z3Result


class VerificationReport(BaseModel):
    """Complete verification output for an entire file."""

    file_path: str
    total_functions: int
    verified: list[VerifiedContract]
    counterexamples: list[Z3Result]
    errors: list[Z3Result]
    summary: str
