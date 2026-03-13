from pathlib import Path

import pytest

from nsjudge.ast_ingestion import parse_file

FIXTURES = Path(__file__).parent / "fixtures"


class TestParseFile:
    def test_simple_math_extracts_all_functions(self):
        source = FIXTURES.joinpath("simple_math.py").read_text()
        graph = parse_file(source)

        assert set(graph.functions.keys()) == {"add", "double", "main"}

    def test_simple_math_verification_order(self):
        source = FIXTURES.joinpath("simple_math.py").read_text()
        graph = parse_file(source)

        order = graph.verification_order
        # Leaf functions must come before main
        assert order.index("add") < order.index("main")
        assert order.index("double") < order.index("main")

    def test_nested_calls_dependency_graph(self):
        source = FIXTURES.joinpath("nested_calls.py").read_text()
        graph = parse_file(source)

        assert "clamp" in graph.functions["normalize"].calls
        assert "normalize" in graph.functions["process"].calls
        assert "process" in graph.functions["main"].calls

    def test_nested_calls_topo_order(self):
        source = FIXTURES.joinpath("nested_calls.py").read_text()
        graph = parse_file(source)

        order = graph.verification_order
        assert order.index("clamp") < order.index("normalize")
        assert order.index("normalize") < order.index("process")
        assert order.index("process") < order.index("main")

    def test_function_args_extracted(self):
        source = FIXTURES.joinpath("simple_math.py").read_text()
        graph = parse_file(source)

        assert graph.functions["add"].args == ["a", "b"]
        assert graph.functions["double"].args == ["x"]
        assert graph.functions["main"].args == []

    def test_missing_main_raises_error(self):
        source = "def helper(x):\n    return x + 1\n"
        with pytest.raises(ValueError, match="main"):
            parse_file(source)

    def test_circular_dependency_raises_error(self):
        source = """
def foo():
    return bar()

def bar():
    return foo()

def main():
    foo()
"""
        with pytest.raises(ValueError, match="Circular dependency"):
            parse_file(source)

    def test_self_recursion_allowed(self):
        source = """
def factorial(n):
    if n <= 1:
        return 1
    return n * factorial(n - 1)

def main():
    print(factorial(5))
"""
        graph = parse_file(source)
        # Self-recursion should NOT appear in calls (excluded from deps)
        assert "factorial" not in graph.functions["factorial"].calls

    def test_global_code_extracted(self):
        source = """CONSTANT = 42

def main():
    print(CONSTANT)
"""
        graph = parse_file(source)
        assert "CONSTANT = 42" in graph.global_code
