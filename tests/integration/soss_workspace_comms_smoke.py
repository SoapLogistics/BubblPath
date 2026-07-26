import pytest

def test_soss_workspace_template_contains_correct_label():
    with open("templates/solomon_loki_workspace.html", "r") as f:
        content = f.read()
    assert "Solomon Neural Interface" in content
