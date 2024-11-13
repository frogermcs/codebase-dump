import os
import unittest
from unittest.mock import patch, mock_open
from codebase_dump.core.ignore_patterns_manager import IgnorePatternManager

class TestIgnorePatternsManager(unittest.TestCase):
        
        def test_ignore_patterns_manager_should_load_default_patterns(self):
            manager = IgnorePatternManager("/test", 
                                           load_default_ignore_patterns=True,
                                           load_gitignore=False,
                                           load_cdigestignore=False)
            self.assertSetEqual(manager.ignore_patterns_as_str, set(IgnorePatternManager.DEFAULT_IGNORE_PATTERNS))

        @patch('codebase_dump.core.ignore_patterns_manager.os.path.exists', return_value=True)
        @patch("builtins.open", new_callable=mock_open, read_data=".java\n.class\n#comment\n")
        def test_load_cdigestignore(self, mock_file, mock_exists):
            manager = IgnorePatternManager("/test", 
                                           load_default_ignore_patterns=False,
                                           load_gitignore=False, 
                                           load_cdigestignore=True)
            
            mock_file.assert_called_once_with("/test/.cdigestignore", "r")
            self.assertSetEqual(manager.ignore_patterns_as_str, set([".java", ".class"]))

        @patch('codebase_dump.core.ignore_patterns_manager.os.path.exists', return_value=True)
        def test_load_both_gitignore_and_cdigestignore(self, mock_exists):
            def mock_open_side_effect(path, mode="r"):
                if path.endswith(".cdigestignore"):
                    return mock_open(read_data=".java\n")()  # Mock for .cdigestignore
                elif path.endswith(".gitignore"):
                    return mock_open(read_data=".py\n")()  # Mock for .gitignore
                else:
                    raise FileNotFoundError(f"Unexpected file opened: {path}")  # Catch unexpected file opens

            with patch("builtins.open", new_callable=mock_open) as mock_file:
                mock_file.side_effect = mock_open_side_effect
                manager = IgnorePatternManager("/test", load_default_ignore_patterns=False,
                                                load_gitignore=True, load_cdigestignore=True)

            self.assertSetEqual(manager.ignore_patterns_as_str, {".java", ".py"})

        @patch('codebase_dump.core.ignore_patterns_manager.os.path.exists', return_value=True)
        @patch("builtins.open", new_callable=mock_open, read_data=".java\n.class\n#comment\n")
        def test_load_gitignore(self, mock_file, mock_exists):
            manager = IgnorePatternManager("/test", load_default_ignore_patterns=False,
                                            load_gitignore=True, load_cdigestignore=False)
            self.assertSetEqual(manager.ignore_patterns_as_str, set([".java", ".class"]))

        @patch('codebase_dump.core.ignore_patterns_manager.os.path.exists', return_value=True)
        @patch("builtins.open", new_callable=mock_open, read_data=".java\n.class\n#comment\n")
        def test_load_gitignore_and_default(self, mock_file, mock_exists):
            manager = IgnorePatternManager("/test", load_default_ignore_patterns=True,
                                            load_gitignore=True, load_cdigestignore=False)
            
            expected_patterns = set(IgnorePatternManager.DEFAULT_IGNORE_PATTERNS)
            expected_patterns.update([".java", ".class"])

            self.assertSetEqual(manager.ignore_patterns_as_str, expected_patterns)
        
        def test_load_extra_patterns(self):
            manager = IgnorePatternManager("/test", load_default_ignore_patterns=False,
                                        load_gitignore=False, load_cdigestignore=False,
                                        extra_ignore_patterns={"extra1", "extra2"})
            self.assertSetEqual(manager.ignore_patterns_as_str, {"extra1", "extra2"})

        def test_should_ignore_filename(self):
            manager = IgnorePatternManager("/test", load_default_ignore_patterns=False,
                                        load_gitignore=False, load_cdigestignore=False,
                                        extra_ignore_patterns={"test.txt"})
            self.assertTrue(manager.should_ignore("/test/test.txt", "/test"))
            self.assertFalse(manager.should_ignore("/test/other.txt", "/test"))

        def test_should_ignore_relative_path(self):
            manager = IgnorePatternManager("/test", load_default_ignore_patterns=False,
                                        load_gitignore=False, load_cdigestignore=False,
                                        extra_ignore_patterns={"sub/test.txt"})
            self.assertTrue(manager.should_ignore("/test/sub/test.txt", "/test"))
            self.assertFalse(manager.should_ignore("/test/sub/other.txt", "/test"))
            self.assertFalse(manager.should_ignore("/test/test.txt", "/test")) # Test that only the relative path is matched

        def test_should_ignore_leading_slash_absolute_path(self):
            base_path = os.path.abspath("/test")  # Get absolute path            
            manager = IgnorePatternManager("/test", load_default_ignore_patterns=False,
                                        load_gitignore=False, load_cdigestignore=False,
                                        extra_ignore_patterns={"sub/test.txt"})
            self.assertTrue(manager.should_ignore(os.path.join(base_path, "sub/test.txt"), base_path))
            self.assertFalse(manager.should_ignore(os.path.join(base_path, "sub/other.txt"), base_path))
            self.assertFalse(manager.should_ignore(os.path.join(base_path, "test.txt"), base_path))

        def test_ignore_directory_pattern(self):
            manager = IgnorePatternManager("/test", load_default_ignore_patterns=False,
                                            load_gitignore=False, load_cdigestignore=False,
                                            extra_ignore_patterns={"sub/"})
            self.assertTrue(manager.should_ignore("/test/sub", "/test"))
            self.assertFalse(manager.should_ignore("/test/sub.txt", "/test"))

        def test_ignore_recursive_wildcard_pattern(self):
            manager = IgnorePatternManager("/test", load_default_ignore_patterns=False,
                                            load_gitignore=False, load_cdigestignore=False,
                                            extra_ignore_patterns={"**/logs", "**/*.tmp"})
            self.assertTrue(manager.should_ignore("/test/logs", "/test"))
            self.assertTrue(manager.should_ignore("/test/sub/logs", "/test"))
            self.assertTrue(manager.should_ignore("/test/sub/file.tmp", "/test"))
            self.assertFalse(manager.should_ignore("/test/sub/file.txt", "/test"))

        def test_empty_pattern_handling(self):
            manager = IgnorePatternManager("/test", load_default_ignore_patterns=False,
                                            load_gitignore=False, load_cdigestignore=False,
                                            extra_ignore_patterns={"", "# Comment only"})
            self.assertFalse(manager.should_ignore("/test/file.txt", "/test"))  # No patterns should ignore anything

        def test_should_ignore_directory_inside_bug_test(self):
            manager = IgnorePatternManager("/Users/aaa/dev/workspace/typescript/repo-analysis-app", load_default_ignore_patterns=False,
                                        load_gitignore=False, load_cdigestignore=False,
                                        extra_ignore_patterns={"/.next/"}) 
            self.assertTrue(manager.should_ignore("/Users/aaa/dev/workspace/typescript/repo-analysis-app/.next/static/chunks/pages/_app-6a626577ffa902a4.js", "/Users/frogermcs/dev/workspace/typescript/repo-analysis-app"))
