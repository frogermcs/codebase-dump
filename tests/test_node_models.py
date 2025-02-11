import unittest
import os
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
            self.assertEqual(directory.get_non_ignored_file_count(), 0)
            self.assertEqual(directory.get_non_ignored_dir_count(), 0)
            self.assertEqual(directory.get_total_tokens(), 0)
            self.assertEqual(directory.get_non_ignored_text_content_size(), 0)
            self.assertEqual(directory.size, 0)
        
        def test_directory_with_one_text_file(self):
            directory = DirectoryAnalysis("test")
            text_file = TextFileAnalysis("test")
            text_file.file_content = "length of this string is 27"
            
            directory.children.append(text_file)
            self.assertEqual(directory.get_non_ignored_file_count(), 1)
            self.assertEqual(directory.get_non_ignored_dir_count(), 0)
            self.assertEqual(directory.get_non_ignored_text_content_size(), 27)
            self.assertEqual(directory.size, 27)

        def test_directory_with_ten_files(self):
            directory = DirectoryAnalysis("test")
            for i in range(10):
                text_file = TextFileAnalysis("test")
                text_file.file_content = "length of this string is 27"
                directory.children.append(text_file)
            self.assertEqual(directory.get_non_ignored_file_count(), 10)
            self.assertEqual(directory.get_non_ignored_dir_count(), 0)
            self.assertEqual(directory.get_non_ignored_text_content_size(), 270)
            self.assertEqual(directory.size, 270)

        def test_directory_with_one_sub_directory(self):
            directory = DirectoryAnalysis("test")
            sub_directory = DirectoryAnalysis("test")
            text_file = TextFileAnalysis("test")
            text_file.file_content = "length of this string is 27"
            sub_directory.children.append(text_file)
            directory.children.append(sub_directory)
            self.assertEqual(directory.get_non_ignored_file_count(), 1)
            self.assertEqual(directory.get_non_ignored_dir_count(), 1)
            self.assertEqual(directory.get_non_ignored_text_content_size(), 27)
            self.assertEqual(directory.size, 27)

        def test_directory_with_one_ignored_file(self):
            directory = DirectoryAnalysis("test")
            text_file = TextFileAnalysis("test")
            text_file.is_ignored = True
            text_file.file_content = "length of this string is 27"
            directory.children.append(text_file)
            self.assertEqual(directory.get_non_ignored_file_count(), 0)
            self.assertEqual(directory.get_non_ignored_dir_count(), 0)
            self.assertEqual(directory.get_non_ignored_text_content_size(), 0)
            self.assertEqual(directory.size, 27)

        def test_directory_with_one_ignored_sub_directory(self):
            directory = DirectoryAnalysis("test")
            sub_directory = DirectoryAnalysis("test")
            sub_directory.is_ignored = True
            text_file = TextFileAnalysis("test")
            text_file.is_ignored = True
            text_file.file_content = "length of this string is 27"
            sub_directory.children.append(text_file)
            directory.children.append(sub_directory)
            self.assertEqual(directory.get_non_ignored_file_count(), 0)
            self.assertEqual(directory.get_non_ignored_dir_count(), 0)
            self.assertEqual(directory.get_non_ignored_text_content_size(), 0)
            self.assertEqual(directory.size, 27)

        def test_directory_with_one_ignored_sub_sub_directory(self):
            directory = DirectoryAnalysis("test")
            sub_directory = DirectoryAnalysis("test")
            sub_sub_directory = DirectoryAnalysis("test")
            sub_sub_directory.is_ignored = True
            text_file = TextFileAnalysis("test")
            text_file.is_ignored = True
            text_file.file_content = "length of this string is 27"
            directory.children.append(sub_directory)
            sub_directory.children.append(sub_sub_directory)
            sub_sub_directory.children.append(text_file)
            
            self.assertEqual(directory.get_non_ignored_file_count(), 0)
            self.assertEqual(directory.get_non_ignored_dir_count(), 1)
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
            self.assertEqual(directory.get_non_ignored_file_count(), 1)
            self.assertEqual(directory.get_non_ignored_dir_count(), 0)
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

        def create_sample_tree(self):
            # Create a sample tree:
            # root
            # ├── file1.txt (non-ignored)
            # ├── dir1 (non-ignored)
            # │   └── file2.txt (non-ignored)
            # └── dir2 (non-ignored)
            #     └── file3.txt (ignored)
            root = DirectoryAnalysis(name="root")
            file1 = TextFileAnalysis(name="file1.txt", file_content="Hello", parent=root)
            dir1 = DirectoryAnalysis(name="dir1", parent=root)
            file2 = TextFileAnalysis(name="file2.txt", file_content="Hello, world!", parent=dir1)
            dir2 = DirectoryAnalysis(name="dir2", parent=root)
            file3 = TextFileAnalysis(name="file3.txt", file_content="Python", parent=dir2, is_ignored=True)

            root.children = [file1, dir1, dir2]
            dir1.children = [file2]
            dir2.children = [file3]
            return root, file1, dir1, file2, dir2, file3

        def test_get_full_path(self):
            # Test correct full path generation
            root = DirectoryAnalysis(name="root")
            child = DirectoryAnalysis(name="child", parent=root)
            file = TextFileAnalysis(name="file.txt", file_content="data", parent=child)
            expected = os.path.join("root", "child", "file.txt")
            assert file.get_full_path() == expected

        def test_get_all_children(self):
            # Test that get_all_children returns all nested nodes.
            root, file1, dir1, file2, dir2, file3 = self.create_sample_tree()
            all_children = root.get_all_children()
            names = {node.name for node in all_children}
            expected_names = {"file1.txt", "dir1", "file2.txt", "dir2", "file3.txt"}
            assert names == expected_names

        def test_get_all_non_ignored_files(self):
            # Test that only non-ignored text files are returned.
            root, file1, dir1, file2, dir2, file3 = self.create_sample_tree()
            non_ignored_files = root.get_all_non_ignored_files()
            names = {f.name for f in non_ignored_files}
            # file3 is ignored.
            expected_names = {"file1.txt", "file2.txt"}
            assert names == expected_names

        def test_get_all_ignored_files(self):
            # Test that only ignored text files are returned.
            root, file1, dir1, file2, dir2, file3 = self.create_sample_tree()
            ignored_files = root.get_all_ignored_files()
            names = {f.name for f in ignored_files}
            expected_names = {"file3.txt"}
            assert names == expected_names

        def test_get_non_ignored_text_content_size(self):
            # Test that the non-ignored text content size is summed correctly.
            root, file1, dir1, file2, dir2, file3 = self.create_sample_tree()
            expected_size = len(file1.file_content) + len(file2.file_content)
            assert root.get_non_ignored_text_content_size() == expected_size

        def test_get_total_tokens(self):
            # Test that total tokens sum matches tokens from non-ignored text files.
            root, file1, dir1, file2, dir2, file3 = self.create_sample_tree()
            # file3 is ignored.
            expected_tokens = file1.count_tokens() + file2.count_tokens()
            assert root.get_total_tokens() == expected_tokens

        def test_get_all_non_ignored_directories(self):
            # Test that all non-ignored directories (excluding root) are returned.
            root, file1, dir1, file2, dir2, file3 = self.create_sample_tree()
            non_ignored_dirs = root.get_all_non_ignored_directories()
            names = {d.name for d in non_ignored_dirs}
            expected_names = {"dir1", "dir2"}
            assert names == expected_names

        def test_get_all_ignored_directories(self):
            # Create a tree with an ignored directory.
            root = DirectoryAnalysis(name="root")
            ignored_dir = DirectoryAnalysis(name="ignored_dir", parent=root, is_ignored=True)
            non_ignored_dir = DirectoryAnalysis(name="non_ignored_dir", parent=root, is_ignored=False)
            root.children = [ignored_dir, non_ignored_dir]
            ignored_dirs = root.get_all_ignored_directories()
            names = {d.name for d in ignored_dirs}
            expected_names = {"ignored_dir"}
            assert names == expected_names

        def test_get_largest_files(self):
            # Create a directory with several files and test ordering by size.
            root = DirectoryAnalysis(name="root")
            file_small = TextFileAnalysis(name="small.txt", file_content="a", parent=root)
            file_medium = TextFileAnalysis(name="medium.txt", file_content="abc", parent=root)
            file_large = TextFileAnalysis(name="large.txt", file_content="abcdef", parent=root)
            ignored_file = TextFileAnalysis(name="ignored.txt", file_content="ignored", parent=root, is_ignored=True)
            root.children = [file_small, file_medium, file_large, ignored_file]
            largest = root.get_largest_files(n=2)
            # Expect largest non-ignored files: "large.txt" then "medium.txt"
            assert [f.name for f in largest] == ["large.txt", "medium.txt"]

        def test_get_largest_directories(self):
            # Create a directory tree with directories having files to determine size.
            root = DirectoryAnalysis(name="root")
            dir1 = DirectoryAnalysis(name="dir1", parent=root)
            dir2 = DirectoryAnalysis(name="dir2", parent=root)
            file1 = TextFileAnalysis(name="file1.txt", file_content="a" * 10, parent=dir1)
            file2 = TextFileAnalysis(name="file2.txt", file_content="a" * 20, parent=dir2)
            dir1.children = [file1]
            dir2.children = [file2]
            root.children = [dir1, dir2]
            largest_dirs = root.get_largest_directories(n=1)
            # Expect dir2 to be the largest because its file is larger.
            assert largest_dirs[0].name == "dir2"