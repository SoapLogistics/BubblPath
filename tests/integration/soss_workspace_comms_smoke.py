import unittest

class TestSOSSWorkspaceSmoke(unittest.TestCase):
    def test_template_label_match(self):
        with open("templates/solomon_loki_workspace.html", "r") as f:
            content = f.read()
        self.assertIn("Solomon Neural Interface", content, "Template label mismatch")

if __name__ == "__main__":
    unittest.main()
