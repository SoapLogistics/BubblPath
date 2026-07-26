import os

def test_soss_workspace_comms_smoke():
    with open("templates/solomon_loki_workspace.html", "r") as f:
        content = f.read()
    assert "Solomon Neural Interface" in content, "Missing official label"

if __name__ == "__main__":
    test_soss_workspace_comms_smoke()
    print("SOSS smoke passed")
