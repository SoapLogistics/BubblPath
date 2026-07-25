import unittest
from unittest.mock import patch, MagicMock
from solomon_joe_bridge import JoeOmegaEngine, JoeTask, BlueprintJob

class TestJoeDaemon(unittest.TestCase):
    def setUp(self):
        self.daemon = JoeOmegaEngine()

    @patch('solomon_joe_bridge.openai.Client')
    def test_analyze_and_expand_blueprint(self, mock_openai_client):
        # Mock LLM response that dictates 2 helpers and 2 tasks
        mock_response = MagicMock()
        mock_response.choices[0].message.content = '{"helpers": 2, "tasks": [{"title": "Phase 1", "description": "Desc 1"}, {"title": "Boundary Push", "description": "Push limits"}]}'
        mock_client_instance = MagicMock()
        mock_client_instance.chat.completions.create.return_value = mock_response
        mock_openai_client.return_value = mock_client_instance

        job = BlueprintJob("Test Blueprint", "Do the thing")
        self.daemon._analyze_and_expand_blueprint(job)

        self.assertEqual(job.helpers_needed, 2)
        self.assertEqual(len(job.tasks), 2)
        self.assertEqual(job.tasks[1].title, "Boundary Push")

    @patch('solomon_joe_bridge.openai.Client')
    @patch('solomon_joe_bridge.subprocess.run')
    def test_execute_single_task(self, mock_subprocess, mock_openai_client):
        # Setup mock OpenAI response
        mock_response = MagicMock()
        mock_response.choices[0].message.content = '{"monologue": "Thinking...", "file_path": "test_output.py", "code": "print(\'hello world\')", "bash_command": ""}'
        mock_client_instance = MagicMock()
        mock_client_instance.chat.completions.create.return_value = mock_response
        mock_openai_client.return_value = mock_client_instance

        # Setup mock git hash return
        mock_git_res = MagicMock()
        mock_git_res.returncode = 0
        mock_git_res.stdout = "abc123hash"
        mock_subprocess.return_value = mock_git_res

        task = JoeTask("Phase 1: Tests", "Write a test")

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
