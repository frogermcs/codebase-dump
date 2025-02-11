import unittest
from codebase_dump.core.models import NodeAnalysis, DirectoryAnalysis, TextFileAnalysis

class TestNodeAnalysis(unittest.TestCase):
    
        def test_node_analysis(self):
            node = NodeAnalysis("test")
            self.assertEqual(node.name, "test")
    
        def test_directory_analysis(self):
            directory = DirectoryAnalysis("test")
            self.assertEqual(directory.name, "test")
            self.assertEqual(directory.type, "directory")
    
        def test_text_file_analysis(self):
            text_file = TextFileAnalysis("test")
            self.assertEqual(text_file.name, "test")
            self.assertEqual(text_file.type, "text_file")

        def test_empty_directory_analysis(self):
            directory = DirectoryAnalysis("test")
            self.assertEqual(directory.get_file_count(), 0)
            self.assertEqual(directory.get_dir_count(), 0)
            self.assertEqual(directory.get_total_tokens(), 0)
            self.assertEqual(directory.get_non_ignored_text_content_size(), 0)
            self.assertEqual(directory.size, 0)
        
        def test_directory_with_one_text_file(self):
            directory = DirectoryAnalysis("test")
            text_file = TextFileAnalysis("test")
            text_file.file_content = "length of this string is 27"
            
            directory.children.append(text_file)
            self.assertEqual(directory.get_file_count(), 1)
            self.assertEqual(directory.get_dir_count(), 0)
            self.assertEqual(directory.get_non_ignored_text_content_size(), 27)
            self.assertEqual(directory.size, 27)

        def test_directory_with_ten_files(self):
            directory = DirectoryAnalysis("test")
            for i in range(10):
                text_file = TextFileAnalysis("test")
                text_file.file_content = "length of this string is 27"
                directory.children.append(text_file)
            self.assertEqual(directory.get_file_count(), 10)
            self.assertEqual(directory.get_dir_count(), 0)
            self.assertEqual(directory.get_non_ignored_text_content_size(), 270)
            self.assertEqual(directory.size, 270)

        def test_directory_with_one_sub_directory(self):
            directory = DirectoryAnalysis("test")
            sub_directory = DirectoryAnalysis("test")
            text_file = TextFileAnalysis("test")
            text_file.file_content = "length of this string is 27"
            sub_directory.children.append(text_file)
            directory.children.append(sub_directory)
            self.assertEqual(directory.get_file_count(), 1)
            self.assertEqual(directory.get_dir_count(), 1)
            self.assertEqual(directory.get_non_ignored_text_content_size(), 27)
            self.assertEqual(directory.size, 27)

        def test_directory_with_one_ignored_file(self):
            directory = DirectoryAnalysis("test")
            text_file = TextFileAnalysis("test")
            text_file.is_ignored = True
            text_file.file_content = "length of this string is 27"
            directory.children.append(text_file)
            self.assertEqual(directory.get_file_count(), 0)
            self.assertEqual(directory.get_dir_count(), 0)
            self.assertEqual(directory.get_non_ignored_text_content_size(), 0)
            self.assertEqual(directory.size, 27)

        def test_directory_with_one_ignored_sub_directory(self):
            directory = DirectoryAnalysis("test")
            sub_directory = DirectoryAnalysis("test")
            sub_directory.is_ignored = True
            text_file = TextFileAnalysis("test")
            text_file.file_content = "length of this string is 27"
            sub_directory.children.append(text_file)
            directory.children.append(sub_directory)
            self.assertEqual(directory.get_file_count(), 0)
            self.assertEqual(directory.get_dir_count(), 0)
            self.assertEqual(directory.get_non_ignored_text_content_size(), 0)
            self.assertEqual(directory.size, 27)

        def test_directory_with_one_ignored_sub_sub_directory(self):
            directory = DirectoryAnalysis("test")
            sub_directory = DirectoryAnalysis("test")
            sub_sub_directory = DirectoryAnalysis("test")
            sub_sub_directory.is_ignored = True
            text_file = TextFileAnalysis("test")
            text_file.file_content = "length of this string is 27"
            directory.children.append(sub_directory)
            sub_directory.children.append(sub_sub_directory)
            sub_sub_directory.children.append(text_file)
            
            self.assertEqual(directory.get_file_count(), 0)
            self.assertEqual(directory.get_dir_count(), 1)
            self.assertEqual(directory.get_non_ignored_text_content_size(), 0)
            self.assertEqual(directory.size, 27)

        def test_directory_with_one_ignored_file_and_one_text_file(self):
            directory = DirectoryAnalysis("test")
            text_file = TextFileAnalysis("test")
            text_file.is_ignored = True
            text_file.file_content = "length of this string is 27"
            directory.children.append(text_file)
            text_file = TextFileAnalysis("test")
            text_file.file_content = "length of this string is 27"
            directory.children.append(text_file)
            self.assertEqual(directory.get_file_count(), 1)
            self.assertEqual(directory.get_dir_count(), 0)
            self.assertEqual(directory.get_non_ignored_text_content_size(), 27)
            self.assertEqual(directory.size, 54)

        def test_text_file_token_count(self):
            text_file = TextFileAnalysis("test", file_content="This is a test string")
            self.assertEqual(text_file.count_tokens(), 5)

        def test_text_file_one_token_count(self):
            text_file = TextFileAnalysis("test", file_content="This")
            self.assertEqual(text_file.count_tokens(), 1)

        def test_text_file_empty_content_token_count(self):
            text_file = TextFileAnalysis("test", file_content="")
            self.assertEqual(text_file.count_tokens(), 0)

        def test_text_file_with_long_text_token_count(self):
            long_text = "token " * 100
            long_text = long_text.strip()
            text_file = TextFileAnalysis("test", file_content=long_text)
            self.assertEqual(text_file.count_tokens(), 100)

        def test_text_file_no_content(self):
            text_file = TextFileAnalysis("test", file_content="")
            self.assertEqual(text_file.size, 0)

        def test_text_file_with_content(self):
            text_file = TextFileAnalysis("test", file_content="Test content")
            self.assertEqual(text_file.size, 12)

        def test_directory_with_nested_directories_get_full_path(self):
            root = DirectoryAnalysis("root")
            dir1 = DirectoryAnalysis("dir1", parent=root)
            dir2 = DirectoryAnalysis("dir2", parent=dir1)
            file1 = TextFileAnalysis("file1.txt", parent=dir2)

            root.children.append(dir1)
            dir1.children.append(dir2)
            dir2.children.append(file1)

            self.assertEqual(root.get_full_path(), "root")
            self.assertEqual(dir1.get_full_path(), "root/dir1")
            self.assertEqual(dir2.get_full_path(), "root/dir1/dir2")
            self.assertEqual(file1.get_full_path(), "root/dir1/dir2/file1.txt")

        def test_file_without_parent_get_full_path(self):
            file = TextFileAnalysis("file.txt")
            self.assertEqual(file.get_full_path(), "file.txt")

        def test_dir_without_parent_get_full_path(self):
            dir = DirectoryAnalysis("dir")
            self.assertEqual(dir.get_full_path(), "dir")