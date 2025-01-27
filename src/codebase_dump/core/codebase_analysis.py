import os
from codebase_dump.core.ignore_patterns_manager import IgnorePatternManager
from codebase_dump.core.models import DirectoryAnalysis, TextFileAnalysis

class CodebaseAnalysis:

    def is_text_file(self, file_path):
        try:
            with open(file_path, 'r') as file:
                 file.read()
            return True
        except UnicodeDecodeError:
            return False
        except FileNotFoundError:
            print("File not found.")
            return False

    def read_file_content(self, file_path):
        """Reads the content of a file, handling potential encoding errors."""
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                return f.read()
        except Exception as e:
            print(f"Error reading file: {file_path}. Details: {str(e)}")
            return f"Error reading file: {str(e)}"

    def _list_directory_items(self, path):
         try:
            return [os.path.join(path, item) for item in os.listdir(path)]
         except FileNotFoundError:
             print(f"Directory not found: {path}")
             return []
         except PermissionError:
             print(f"Permission denied for: {path}")
             return []

    def _analyze_file(self, item_path, is_ignored, parent):
        file_size = os.path.getsize(item_path)
        if self.is_text_file(item_path):
             content = self.read_file_content(item_path)
             print(f"Debug: Text file {item_path}, size: {file_size}, content size: {len(content)}")
        else:
             content = "[Non-text file]"
             print(f"Debug: Non-text file {item_path}, size: {file_size}")
        return TextFileAnalysis(name=os.path.basename(item_path), file_content=content, is_ignored=is_ignored, parent=parent)
    
    def _create_node(self, item_path, ignore_patterns_manager, parent):
        """Creates a node (file or directory) for a given path."""

        is_ignored = ignore_patterns_manager.should_ignore(item_path)
        print(f"Debug: Checking {item_path}, ignored: {is_ignored}")

        if is_ignored:
             return None

        if os.path.isfile(item_path):
            try:
              return self._analyze_file(item_path, is_ignored, parent)
            except FileNotFoundError:
              print(f"File not found {item_path}")
              return None
        elif os.path.isdir(item_path):
            return DirectoryAnalysis(name=os.path.basename(item_path), is_ignored=is_ignored, parent=parent)
        
        return None
    
    def analyze_directory(self, 
                          path, 
                          ignore_patterns_manager: IgnorePatternManager, 
                          base_path, 
                          parent=None, 
                          max_depth=None, 
                          current_depth=0) -> DirectoryAnalysis:
        """Recursively analyzes a directory and its contents."""

        if max_depth is not None and current_depth > max_depth:
            return None

        if path == ".":
            path = os.getcwd()

        result = DirectoryAnalysis(name=os.path.basename(path), parent=parent)
        
        for item_path in self._list_directory_items(path):
            node = self._create_node(item_path, ignore_patterns_manager, result)
            if node:
                if isinstance(node, DirectoryAnalysis):
                   subdir = self.analyze_directory(item_path, ignore_patterns_manager, base_path, node, max_depth, current_depth + 1)
                   if subdir:
                        result.children.append(subdir)
                else:
                    result.children.append(node)
        return result