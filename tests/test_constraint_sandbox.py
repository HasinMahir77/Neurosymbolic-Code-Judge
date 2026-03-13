import pytest

from nsjudge.config import Settings
from nsjudge.constraint_sandbox import ConstraintSandbox

VERIFIED_SCRIPT = """\
from z3 import *
x = Int('x')
s = Solver()
s.add(x > 0)
s.add(Not(x > 0))
if s.check() == sat:
    print("COUNTEREXAMPLE")
    m = s.model()
    for d in m.decls():
        print(f"  {d.name()} = {m[d]}")
else:
    print("VERIFIED")
"""

COUNTEREXAMPLE_SCRIPT = """\
from z3 import *
x = Int('x')
s = Solver()
s.add(x > 0)
s.add(x < 5)
# Negation: is there an x in (0,5) where x != 3? Obviously yes.
s.add(x != 3)
if s.check() == sat:
    print("COUNTEREXAMPLE")
    m = s.model()
    for d in m.decls():
        print(f"  {d.name()} = {m[d]}")
else:
    print("VERIFIED")
"""

SYNTAX_ERROR_SCRIPT = """\
from z3 import *
x = Int('x'
"""

TIMEOUT_SCRIPT = """\
import time
time.sleep(60)
"""


@pytest.fixture
def sandbox():
    settings = Settings(gemini_api_key="unused", sandbox_timeout_seconds=5)
    return ConstraintSandbox(settings)


class TestConstraintSandbox:
    def test_verified_script(self, sandbox):
        result = sandbox.execute("test_func", VERIFIED_SCRIPT)
        assert result.status == "verified"
        assert result.function_name == "test_func"

    def test_counterexample_script(self, sandbox):
        result = sandbox.execute("test_func", COUNTEREXAMPLE_SCRIPT)
        assert result.status == "counterexample"
        assert result.counterexample is not None
        assert "x" in result.counterexample

    def test_syntax_error_script(self, sandbox):
        result = sandbox.execute("test_func", SYNTAX_ERROR_SCRIPT)
        assert result.status == "error"
        assert result.error_message is not None

    def test_timeout_script(self, sandbox):
        result = sandbox.execute("test_func", TIMEOUT_SCRIPT)
        assert result.status == "timeout"

    def test_no_output_script(self, sandbox):
        result = sandbox.execute("test_func", "x = 1\n")
        assert result.status == "error"
        assert "Unexpected output" in (result.error_message or "")
