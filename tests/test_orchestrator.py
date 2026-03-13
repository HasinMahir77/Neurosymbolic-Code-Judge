from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from nsjudge.config import Settings
from nsjudge.schemas import FunctionContract, Z3Result

FIXTURES = Path(__file__).parent / "fixtures"


def _make_verified_contract(func_name: str) -> FunctionContract:
    """Create a mock contract that produces a VERIFIED Z3 script."""
    return FunctionContract(
        function_name=func_name,
        preconditions=["input is valid"],
        postconditions=["output is correct"],
        z3_script=(
            "from z3 import *\n"
            "s = Solver()\n"
            "s.add(False)\n"  # unsat -> VERIFIED
            "if s.check() == sat:\n"
            "    print('COUNTEREXAMPLE')\n"
            "else:\n"
            "    print('VERIFIED')\n"
        ),
        reasoning="Mock contract for testing",
    )


def _make_counterexample_contract(func_name: str) -> FunctionContract:
    """Create a mock contract that produces a COUNTEREXAMPLE Z3 script."""
    return FunctionContract(
        function_name=func_name,
        preconditions=["input is valid"],
        postconditions=["output is correct"],
        z3_script=(
            "from z3 import *\n"
            "x = Int('x')\n"
            "s = Solver()\n"
            "s.add(x == 42)\n"  # sat -> COUNTEREXAMPLE
            "if s.check() == sat:\n"
            "    print('COUNTEREXAMPLE')\n"
            "    m = s.model()\n"
            "    for d in m.decls():\n"
            "        print(f'  {d.name()} = {m[d]}')\n"
            "else:\n"
            "    print('VERIFIED')\n"
        ),
        reasoning="Mock contract for testing",
    )


class TestOrchestrator:
    @patch("nsjudge.orchestrator.SemanticTranslator")
    def test_all_verified(self, mock_translator_cls):
        """All functions in simple_math.py should verify with mocked LLM."""
        mock_translator = MagicMock()
        mock_translator.generate_contract.side_effect = (
            lambda fi, deps: _make_verified_contract(fi.name)
        )
        mock_translator_cls.return_value = mock_translator

        from nsjudge.orchestrator import Orchestrator

        settings = Settings(gemini_api_key="test-key")
        orch = Orchestrator(settings)

        report = orch.verify_file(str(FIXTURES / "simple_math.py"))

        assert report.total_functions == 3
        assert len(report.verified) == 3
        assert len(report.counterexamples) == 0
        assert len(report.errors) == 0

    @patch("nsjudge.orchestrator.SemanticTranslator")
    def test_counterexample_detected(self, mock_translator_cls):
        """One function returns counterexample, rest verified."""
        mock_translator = MagicMock()

        def side_effect(fi, deps):
            if fi.name == "sum_up_to":
                return _make_counterexample_contract(fi.name)
            return _make_verified_contract(fi.name)

        mock_translator.generate_contract.side_effect = side_effect
        mock_translator_cls.return_value = mock_translator

        from nsjudge.orchestrator import Orchestrator

        settings = Settings(gemini_api_key="test-key")
        orch = Orchestrator(settings)

        report = orch.verify_file(str(FIXTURES / "off_by_one.py"))

        assert report.total_functions == 2
        assert len(report.counterexamples) == 1
        assert report.counterexamples[0].function_name == "sum_up_to"

    @patch("nsjudge.orchestrator.SemanticTranslator")
    def test_progress_callback(self, mock_translator_cls):
        """Progress callback is called for each function."""
        mock_translator = MagicMock()
        mock_translator.generate_contract.side_effect = (
            lambda fi, deps: _make_verified_contract(fi.name)
        )
        mock_translator_cls.return_value = mock_translator

        from nsjudge.orchestrator import Orchestrator

        settings = Settings(gemini_api_key="test-key")
        orch = Orchestrator(settings)

        progress_calls = []
        report = orch.verify_file(
            str(FIXTURES / "simple_math.py"),
            on_progress=lambda i, t, n, r: progress_calls.append((i, t, n)),
        )

        assert len(progress_calls) == 3
        assert progress_calls[-1][0] == 3  # Last call: index 3 of 3
