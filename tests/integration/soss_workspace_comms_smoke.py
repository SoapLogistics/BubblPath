import os
import sys

def test_soss_workspace_smoke():
    template_path = "templates/solomon_loki_workspace.html"
    assert os.path.exists(template_path), "Template not found"
    with open(template_path, 'r') as f:
        content = f.read()
    assert "Solomon Neural Interface" in content, "Official label mismatch in template"
    print("SOSS Workspace Comms Smoke Test Passed")

if __name__ == "__main__":
    test_soss_workspace_smoke()
