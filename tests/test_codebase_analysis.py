import unittest
from unittest.mock import patch, mock_open
from codebase_dump.core.codebase_analysis import CodebaseAnalysis
from codebase_dump.core.ignore_patterns_manager import IgnorePatternManager
from codebase_dump.core.models import DirectoryAnalysis, TextFileAnalysis

class TestCodebaseAnalysis(unittest.TestCase):


     @patch("codebase_dump.core.codebase_analysis.os.listdir", return_value=["file1.txt", "file2.py"])
     @patch('codebase_dump.core.codebase_analysis.os.path.isfile', return_value=True)
     @patch('codebase_dump.core.codebase_analysis.os.path.getsize', return_value=10)
     @patch("builtins.open", new_callable=mock_open, read_data="Loremm ipsum dolor sit amet")
     def test_analyze_directory_with_ignored(self, mock_read, mock_file, mock_isfile, mock):
          ignore_manager = IgnorePatternManager(".", load_default_ignore_patterns=False, extra_ignore_patterns=["*.py"])
          codebase_analysis = CodebaseAnalysis()
          result = codebase_analysis.analyze_directory(".", ignore_manager, ".")

          self.assertEqual(len(result.get_all_non_ignored_files()), 1)
          self.assertEqual(len(result.get_all_children()), 2)
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
                    self.assertEqual(len(result.get_all_non_ignored_files()), 2)
                    self.assertEqual(len(result.get_all_children()), 3)
                    self.assertEqual(result.get_all_non_ignored_files()[0].name, "dir")
                    self.assertEqual(result.get_all_non_ignored_files()[1].name, "file1.txt")


     @patch("os.getcwd", return_value="dir")
     @patch("os.listdir", return_value=["file1.txt", "file2.py"])
     @patch("os.path.isfile", side_effect=lambda x: not x.endswith("/") and not x.endswith("dir"))
     @patch("os.path.isdir", side_effect=lambda x: x.endswith("dir"))
     @patch("os.path.getsize", return_value=1024)
     @patch("builtins.open", new_callable=mock_open, read_data="Sample file content")
     def test_analyze_directory_basic(self, mock_open, mock_getsize, mock_isdir, mock_isfile, mock_listdir, mock_getcwd):
          ignore_manager = IgnorePatternManager(".", load_default_ignore_patterns=False)
          analysis = CodebaseAnalysis()

          result = analysis.analyze_directory(".", ignore_manager, ".")

          self.assertIsInstance(result, DirectoryAnalysis)
          self.assertEqual(len(result.children), 2)

          self.assertEqual(result.children[0].name, "file1.txt")
          self.assertIsInstance(result.children[0], TextFileAnalysis)
          self.assertEqual(result.children[1].name, "file2.py")
          self.assertIsInstance(result.children[1], TextFileAnalysis)

     @patch("os.listdir", return_value=["file1.log", "file2.tmp"])
     @patch("os.path.isfile", return_value=True)
     @patch("os.path.getsize", return_value=512)
     def test_analyze_directory_with_ignore_patterns(self, mock_getsize, mock_isfile, mock_listdir):
          ignore_manager = IgnorePatternManager(
               ".", load_default_ignore_patterns=False, extra_ignore_patterns={"*.log", "*.tmp"}
          )
          analysis = CodebaseAnalysis()
          result = analysis.analyze_directory(".", ignore_manager, ".")

          self.assertEqual(len(result.get_all_children()), 2)
          self.assertEqual(len(result.get_all_non_ignored_files()), 0)

     @patch("os.listdir", side_effect=FileNotFoundError)
     def test_list_directory_items_file_not_found(self, mock_listdir):
          analysis = CodebaseAnalysis()
          result = analysis._list_directory_items("nonexistent_dir")

          self.assertEqual(result, [])

     @patch("os.path.isfile", return_value=True)
     @patch("os.path.getsize", return_value=1024)
     @patch("builtins.open", new_callable=mock_open, read_data="Sample content")
     def test_analyze_text_file(self, mock_open, mock_getsize, mock_isfile):
          analysis = CodebaseAnalysis()
          result = analysis._analyze_file("file.txt", False, None)

          self.assertIsInstance(result, TextFileAnalysis)
          self.assertEqual(result.name, "file.txt")
          self.assertEqual(result.file_content, "Sample content")
          self.assertFalse(result.is_ignored)

     @patch("os.path.isfile", return_value=True)
     @patch("os.path.getsize", return_value=1024)
     @patch("builtins.open", side_effect=UnicodeDecodeError("utf-8", b"", 0, 1, "reason"))
     def test_analyze_non_text_file(self, mock_open, mock_getsize, mock_isfile):
          analysis = CodebaseAnalysis()
          result = analysis._analyze_file("file.bin", False, None)

          self.assertIsInstance(result, TextFileAnalysis)
          self.assertEqual(result.name, "file.bin")
          self.assertEqual(result.file_content, "[Non-text file]")
          self.assertFalse(result.is_ignored)

     @patch("os.listdir", return_value=["file1.txt", "file2.txt"])
     @patch("os.path.isfile", return_value=True)
     @patch("os.path.getsize", side_effect=[100, 200])
     @patch("builtins.open", new_callable=mock_open, read_data="Sample")
     def test_analyze_directory_with_file_sizes(self, mock_open, mock_getsize, mock_isfile, mock_listdir):
          ignore_manager = IgnorePatternManager(".", load_default_ignore_patterns=False)
          analysis = CodebaseAnalysis()
          result = analysis.analyze_directory(".", ignore_manager, ".")

          self.assertEqual(result.children[0].size, len("Sample"))
          self.assertEqual(result.children[1].size, len("Sample"))

     @patch("os.listdir")
     @patch("os.path.isfile")
     @patch("os.path.isdir")
     @patch("os.getcwd", return_value=".")
     @patch("os.path.getsize", return_value=2048)
     @patch("builtins.open", new_callable=mock_open, read_data="File content")
     def test_analyze_directory_with_nested(self, mock_open, mock_getsize, mock_getcwd, mock_isdir, mock_isfile, mock_listdir):
          def listdir_side_effect(path):
               if path == ".":
                    return ["file1.txt", "file2.py", "dir"]
               elif path.endswith("dir"):
                    return ["file3.txt"]
               return []

          def isdir_side_effect(path):
               return path.endswith("dir")

          def isfile_side_effect(path):
               return not path.endswith("dir")

          mock_listdir.side_effect = listdir_side_effect
          mock_isdir.side_effect = isdir_side_effect
          mock_isfile.side_effect = isfile_side_effect

          ignore_manager = IgnorePatternManager(".", load_default_ignore_patterns=False)
          analysis = CodebaseAnalysis()

          result = analysis.analyze_directory(".", ignore_manager, ".")

          self.assertEqual(len(result.children), 3)
          self.assertEqual(result.children[0].name, "file1.txt")
          self.assertEqual(result.children[1].name, "file2.py")
          self.assertEqual(result.children[2].name, "dir")

          nested_dir = result.children[2]
          self.assertIsInstance(nested_dir, DirectoryAnalysis)
          self.assertEqual(len(nested_dir.children), 1)
          self.assertEqual(nested_dir.children[0].name, "file3.txt")
          self.assertIsInstance(nested_dir.children[0], TextFileAnalysis)

     @patch("os.getcwd", return_value=".")
     @patch("codebase_dump.core.codebase_analysis.os.listdir", return_value=["file1.txt", "file2.txt", "file3.txt"])
     @patch('codebase_dump.core.codebase_analysis.os.path.isfile', return_value=True)
     @patch('codebase_dump.core.codebase_analysis.os.path.getsize', side_effect=[10, 20, 30])
     def test_analyze_directory_with_ignore_top_files(self, mock_read, mock_isfile, mock, mock_getcwd):

          def mock_open_side_effect(path, mode="r", encoding='utf-8', errors='ignore'):
            if path.endswith("file1.txt"):
                return mock_open(read_data="Big")()
            elif path.endswith("file2.txt"):
                return mock_open(read_data="Bigger")()
            elif path.endswith("file3.txt"):
                return mock_open(read_data="The Biggest")()
            else:
                return mock_open(read_data="")()
          
          with patch("builtins.open", new_callable=mock_open) as mock_file:
               mock_file.side_effect = mock_open_side_effect
               ignore_manager = IgnorePatternManager(".", load_default_ignore_patterns=False)
               codebase_analysis = CodebaseAnalysis()
               result = codebase_analysis.analyze_directory(".", ignore_manager, ".", ignore_top_files=2)
               self.assertEqual(len(result.children), 3)
               
               # Check that the two largest files are ignored
               self.assertTrue(result.children[2].is_ignored)
               self.assertTrue(result.children[1].is_ignored)

               # Check that the smallest file is not ignored
               self.assertFalse(result.children[0].is_ignored)