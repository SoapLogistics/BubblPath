import unittest
from solomon_browser_companion import BrowserCompanionBackend

class TestBrowserCompanion(unittest.TestCase):
    def setUp(self):
        self.backend = BrowserCompanionBackend()

    def test_extract_actions(self):
        text = "Here is what I recommend:\n[ACTION: #submit-button]\nAnd fill out this field:\n[FILL: .search-input | hello world]"
        actions = self.backend._extract_actions(text)

        self.assertEqual(len(actions), 2)

        self.assertEqual(actions[0]['type'], 'ACTION')
        self.assertEqual(actions[0]['selector'], '#submit-button')

        self.assertEqual(actions[1]['type'], 'FILL')
        self.assertEqual(actions[1]['selector'], '.search-input')
        self.assertEqual(actions[1]['value'], 'hello world')

if __name__ == '__main__':
    unittest.main()
