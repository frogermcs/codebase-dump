import unittest
from unittest.mock import patch, mock_open
from codebase_dump.core.codebase_analysis import CodebaseAnalysis
from codebase_dump.core.ignore_patterns_manager import IgnorePatternManager
from codebase_dump.core.models import DirectoryAnalysis, TextFileAnalysis

class TestCodebaseAnalysis(unittest.TestCase):

    @patch("codebase_dump.core.codebase_analysis.os.listdir", return_value=["file1.txt", "file2.txt"])
    @patch('codebase_dump.core.codebase_analysis.os.path.isfile', return_value=True)
    @patch('codebase_dump.core.codebase_analysis.os.path.getsize', return_value=10)
    @patch("builtins.open", new_callable=mock_open, read_data="Loremm ipsum dolor sit amet")
    def test_analyze_directory_basic(self, mock_read, mock_file, mock_isfile, mock):
         ignore_manager = IgnorePatternManager(".", load_default_ignore_patterns=False)
         codebase_analysis = CodebaseAnalysis()
         result = codebase_analysis.analyze_directory(".", ignore_manager, ".")
         self.assertEqual(len(result.children), 2)
         self.assertEqual(result.children[0].name, "file1.txt")
         self.assertEqual(result.children[1].name, "file2.txt")
         self.assertEqual(result.children[0].parent, result)
         self.assertEqual(result.children[1].parent, result)


    @patch("codebase_dump.core.codebase_analysis.os.listdir", return_value=["file1.txt", "file2.py"])
    @patch('codebase_dump.core.codebase_analysis.os.path.isfile', return_value=True)
    @patch('codebase_dump.core.codebase_analysis.os.path.getsize', return_value=10)
    @patch("builtins.open", new_callable=mock_open, read_data="Loremm ipsum dolor sit amet")
    def test_analyze_directory_with_ignored(self, mock_read, mock_file, mock_isfile, mock):
         ignore_manager = IgnorePatternManager(".", load_default_ignore_patterns=False, extra_ignore_patterns=["*.py"])
         codebase_analysis = CodebaseAnalysis()
         result = codebase_analysis.analyze_directory(".", ignore_manager, ".")
         self.assertEqual(len(result.children), 1)
         self.assertEqual(result.children[0].name, "file1.txt")


    @patch("codebase_dump.core.codebase_analysis.os.listdir", return_value=["file1.txt", "file2.py"])
    @patch('codebase_dump.core.codebase_analysis.os.path.isfile', return_value=True)
    @patch('codebase_dump.core.codebase_analysis.os.path.getsize', return_value=10)
    @patch("builtins.open", new_callable=mock_open, read_data="Loremm ipsum dolor sit amet")
    def test_analyze_directory_with_ignored_and_nested_dir(self, mock_read, mock_file, mock_isfile, mock):
         ignore_manager = IgnorePatternManager(".", load_default_ignore_patterns=False, extra_ignore_patterns=["*.py"])
         codebase_analysis = CodebaseAnalysis()

         with patch("codebase_dump.core.codebase_analysis.os.listdir", return_value=["dir", "file1.txt", "file2.py"]):
              with patch('codebase_dump.core.codebase_analysis.os.path.isdir', side_effect=[True, False, False]):
                  result = codebase_analysis.analyze_directory(".", ignore_manager, ".")
                  self.assertEqual(len(result.children), 2)
                  self.assertEqual(result.children[0].name, "dir")
                  self.assertEqual(result.children[1].name, "file1.txt")
