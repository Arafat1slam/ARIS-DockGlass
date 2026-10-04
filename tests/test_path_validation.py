import unittest
from src.infrastructure.paths import validate_path

class TestPathValidation(unittest.TestCase):
    def test_rejects_traversal(self):
        self.assertFalse(validate_path("../secret.txt"))
        self.assertFalse(validate_path("some/dir/../../secret.txt"))

    def test_rejects_js_and_file_urls(self):
        self.assertFalse(validate_path("javascript:alert(1)"))
        self.assertFalse(validate_path("file:///C:/Windows/System32/cmd.exe"))

    def test_accepts_http_https(self):
        self.assertTrue(validate_path("https://example.com"))
        self.assertTrue(validate_path("http://example.com"))

    def test_normalizes_paths(self):
        path = validate_path("C:\\Users\\Test\\..\\App.exe")
        self.assertEqual(path, "C:\\Users\\App.exe")

if __name__ == '__main__':
    unittest.main()
