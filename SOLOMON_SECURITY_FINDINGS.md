# Security Findings
1. Use of `exec()` in `tests/test_gabriel.py` and `gabriel_engine/core/models.py`.
2. AST Injection route (`/api/gabriel/ast-inject`) allows arbitrary code modification over HTTP.
