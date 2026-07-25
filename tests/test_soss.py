import pytest
import types
from solomon_core.soss.ast_validator import prove_code_safety
from solomon_core.soss.ast_injector import ASTInjector, InjectionError
from solomon_core.soss.synthesizer import CleanRoomSynthesizer

# --- AST Validator Tests ---

def test_ast_validator_safe_code():
    safe_code = "def add(a, b):\n    return a + b"
    is_safe, reason = prove_code_safety(safe_code)
    assert is_safe is True

def test_ast_validator_blocks_imports():
    unsafe_code = "import os\ndef read_file():\n    os.system('ls')"
    is_safe, reason = prove_code_safety(unsafe_code)
    assert is_safe is False
    assert "Forbidden module import: os" in reason

def test_ast_validator_blocks_dangerous_functions():
    unsafe_code = "def do_bad():\n    eval('1 + 1')"
    is_safe, reason = prove_code_safety(unsafe_code)
    assert is_safe is False
    assert "Forbidden function call: eval" in reason

def test_ast_validator_complexity_limit():
    complex_code = "def complex_loop():\n" + "    for i in range(10): pass\n" * 30
    is_safe, reason = prove_code_safety(complex_code)
    assert is_safe is False
    assert "Code complexity exceeded" in reason


# --- AST Injector Tests ---

def dummy_function():
    return "original"

def test_ast_injector_hot_reload():
    # Verify original behavior
    assert dummy_function() == "original"

    new_code = "def dummy_function():\n    return 'mutated'"

    # Mutate
    ASTInjector.hot_reload_function(dummy_function, new_code)

    # Verify mutated behavior
    assert dummy_function() == "mutated"

def test_ast_injector_fails_on_syntax_error():
    bad_code = "def dummy_function():\n return 'bad" # Missing quote
    with pytest.raises(InjectionError):
        ASTInjector.hot_reload_function(dummy_function, bad_code)

def test_ast_injector_fails_on_missing_function():
    wrong_name_code = "def some_other_function():\n    return 1"
    with pytest.raises(InjectionError):
        ASTInjector.hot_reload_function(dummy_function, wrong_name_code)


# --- Synthesizer Sandbox Tests ---

def test_synthesizer_sandboxed_execution_success():
    synthesizer = CleanRoomSynthesizer()

    code = "def test_func(x):\n    return x * 2"
    test_code = "def run_tests():\n    assert test_func(2) == 4\nrun_tests()"

    passed, msg = synthesizer._run_sandboxed_tests(code, test_code, "test_func")
    assert passed is True

def test_synthesizer_sandboxed_execution_failure():
    synthesizer = CleanRoomSynthesizer()

    code = "def test_func(x):\n    return x * 3" # Intentional bug
    test_code = "def run_tests():\n    assert test_func(2) == 4\nrun_tests()"

    passed, msg = synthesizer._run_sandboxed_tests(code, test_code, "test_func")
    assert passed is False
    assert "AssertionError" in msg

def test_synthesizer_sandboxed_execution_blocks_builtins():
    synthesizer = CleanRoomSynthesizer()

    # Try to use a builtin that is NOT in the sandbox globals (e.g. open)
    code = "def test_func(x):\n    return open('test.txt')"
    test_code = "def run_tests():\n    test_func(1)\nrun_tests()"

    passed, msg = synthesizer._run_sandboxed_tests(code, test_code, "test_func")
    assert passed is False
    assert "name 'open' is not defined" in msg

def test_ast_validator_blocks_aliasing():
    unsafe_code = "x = eval\nx('1 + 1')"
    is_safe, reason = prove_code_safety(unsafe_code)
    assert is_safe is False
    assert "Forbidden function aliasing: eval" in reason

def test_synthesizer_sandboxed_timeout():
    synthesizer = CleanRoomSynthesizer()

    code = "def test_func():\n    while True:\n        pass" # Infinite loop
    test_code = "def run_tests():\n    test_func()\nrun_tests()"

    passed, msg = synthesizer._run_sandboxed_tests(code, test_code, "test_func", timeout=1)
    assert passed is False
    assert "Execution timed out" in msg
