import unittest
from unittest.mock import patch, MagicMock
from solomon_jules_bridge import JulesAutonomousDaemon, JulesTask

class TestJulesDaemon(unittest.TestCase):
    def setUp(self):
        self.daemon = JulesAutonomousDaemon()

    def test_parse_blueprint(self):
        blueprint = """
# Master Plan
## Phase 1: Setup
This is the first task.
We need to initialize the db.

## Phase 2: Execution
Run the things.
        """
        tasks = self.daemon.parse_blueprint(blueprint.strip())
        self.assertEqual(len(tasks), 2)
        self.assertEqual(tasks[0].title, "Phase 1: Setup")
        self.assertIn("initialize the db", tasks[0].description)
        self.assertEqual(tasks[1].title, "Phase 2: Execution")

    @patch('solomon_jules_bridge.openai.Client')
    @patch('solomon_jules_bridge.subprocess.run')
    def test_execute_single_task(self, mock_subprocess, mock_openai_client):
        # Setup mock OpenAI response
        mock_response = MagicMock()
        mock_response.choices[0].message.content = "# filename: test_output.py\nprint('hello world')"
        mock_client_instance = MagicMock()
        mock_client_instance.chat.completions.create.return_value = mock_response
        mock_openai_client.return_value = mock_client_instance

        # Setup mock git hash return
        mock_git_res = MagicMock()
        mock_git_res.stdout = "abc123hash"
        mock_subprocess.return_value = mock_git_res

        task = JulesTask("Phase 1: Tests", "Write a test")

        # Run execution
        self.daemon._execute_single_task(task)

        # Verify file was written
        with open("test_output.py", "r") as f:
            content = f.read()
        self.assertEqual(content.strip(), "print('hello world')")

        # Verify commit hash recorded
        self.assertEqual(task.commit_hash, "abc123hash")

        # Cleanup
        import os
        if os.path.exists("test_output.py"):
            os.remove("test_output.py")

if __name__ == '__main__':
    unittest.main()
