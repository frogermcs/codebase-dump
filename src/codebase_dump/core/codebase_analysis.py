import os

from codebase_dump.core.ignore_patterns_manager import IgnorePatternManager
from codebase_dump.core.models import DirectoryAnalysis, TextFileAnalysis

class CodebaseAnalysis:

    def is_text_file_old(self, file_path):
        """Determines if a file is likely a text file based on its content."""
        try:
            with open(file_path, 'rb') as file:
                chunk = file.read(1024)
            return not bool(chunk.translate(None, bytes([7, 8, 9, 10, 12, 13, 27] + list(range(0x20, 0x100)))))
        except IOError:
            return False

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
            return f"Error reading file: {str(e)}"

    def analyze_directory(self, path, ignore_patterns_manager: IgnorePatternManager, base_path, max_depth=None, current_depth=0) -> DirectoryAnalysis:
        """Recursively analyzes a directory and its contents."""
        if max_depth is not None and current_depth > max_depth:
            return None

        result = DirectoryAnalysis(name=os.path.basename(path))
        try:
            for item in os.listdir(path):                
                item_path = os.path.join(path, item)
                
                is_ignored = ignore_patterns_manager.should_ignore(item_path)
                print(f"Debug: Checking {item_path}, ignored: {is_ignored}")  # Debug line

                if os.path.isfile(item_path) and self.is_text_file(item_path):
                    file_size = os.path.getsize(item_path)

                if is_ignored:
                    continue  # Skip ignored items for further analysis

                if os.path.isfile(item_path):
                    file_size = os.path.getsize(item_path)
                    if self.is_text_file(item_path):
                        content = self.read_file_content(item_path)
                        print(f"Debug: Text file {item_path}, size: {file_size}, content size: {len(content)}")
                    else:
                        content = "[Non-text file]"
                        print(f"Debug: Non-text file {item_path}, size: {file_size}")

                    child = TextFileAnalysis(name=item, file_content=content, is_ignored=is_ignored)
                    result.children.append(child)
                elif os.path.isdir(item_path):
                    subdir = self.analyze_directory(item_path, ignore_patterns_manager, base_path, max_depth, current_depth + 1)
                    if subdir:
                        subdir.is_ignored = is_ignored
                        result.children.append(subdir)
                        
        except PermissionError:
            print(f"Permission denied: {path}")

        return result