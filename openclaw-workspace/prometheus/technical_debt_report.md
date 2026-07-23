# Technical Debt Report

*Last Synced: 2026-07-19 18:32:53 UTC*

## Active Technical Debt Inventory

| ID | Debt Issue | Severity | Impact | Remediation Status |
| :--- | :--- | :--- | :--- | :--- |
| TD-001 | Unpinned Dependencies in requirements.txt | Medium | Vulnerable to breaking updates during automatic deployments on Render. | Planned: Pin 'flask' and 'openai' to stable packages in requirements.txt. |
| TD-002 | Deprecated OpenAI SDK in app.py | High | Code will crash on newer versions of the PyPI openai package (v1.0.0+). | Planned: Transition ChatCompletion.create syntax to client.chat.completions.create. |
| TD-003 | Flask Endpoint Lacks Authorization | Critical | Publicly available /chat route allows third-party actors to consume platform model budget. | Planned: Integrate API token checking in request headers. |

## Technical Debt Metric Trends
- **Active Technical Debt Count:** 3
- **Critical Issues Outstanding:** 1
- **High Issues Outstanding:** 1
