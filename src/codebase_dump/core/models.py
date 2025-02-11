from dataclasses import dataclass, field
from typing import List, Union, Optional
import tiktoken
import os

@dataclass
class NodeAnalysis:
    name: str = ""
    is_ignored: bool = False
    parent: Optional["NodeAnalysis"] = None  

    @property
    def type(self) -> str:
        return NotImplemented
    
    @property
    def size(self) -> int:
        return NotImplemented
    
    def to_dict(self):
        return NotImplemented
    
    def get_full_path(self) -> str:
        """Returns the full path of the node."""
        if self.parent is None:
            return self.name  # Base case: root node
        return os.path.join(self.parent.get_full_path(), self.name)

@dataclass
class TextFileAnalysis(NodeAnalysis):
    file_content: str = ""

    @property
    def type(self) -> str:
        return "text_file"
    
    @property
    def size(self) -> int:
        return len(self.file_content)
    
    def count_tokens(self):
        """Counts the number of tokens in a text string."""
        enc = tiktoken.get_encoding("cl100k_base")
        try:
            return len(enc.encode(self.file_content, disallowed_special=()))
        except Exception as e:
            print(f"Warning: Error counting tokens: {str(e)}")
            return 0
        
    def to_dict(self):
        return {
            "name": self.name,
            "type": self.type,
            "size": self.size,
            "is_ignored": self.is_ignored,
            "content": self.file_content
        }

@dataclass
class DirectoryAnalysis(NodeAnalysis):
    children: List[Union["DirectoryAnalysis", TextFileAnalysis]] = field(default_factory=list)

    def get_all_children(self) -> List[NodeAnalysis]:
        all_children = []
        for child in self.children:
            all_children.append(child)
            if isinstance(child, DirectoryAnalysis):
                all_children.extend(child.get_all_children())
        return all_children
    
    def get_non_ignored_children(self) -> List[NodeAnalysis]:
        non_ignored_children = []
        for child in self.children:
            if not child.is_ignored:
                non_ignored_children.append(child)
        return non_ignored_children

    @property
    def type(self) -> str:
        return "directory"

    def get_file_count(self) -> int:
        count = 0
        for child in self.children:
            if child.is_ignored:
                continue

            if isinstance(child, TextFileAnalysis):
                count += 1
            if isinstance(child, DirectoryAnalysis):
                count += child.get_file_count()
        return count
    
    def get_dir_count(self) -> int:
       count = 0
       for child in self.children:
           if child.is_ignored:
               continue 
           
           if isinstance(child, DirectoryAnalysis):
               count += 1 + child.get_dir_count()
       return count


    def get_total_tokens(self) -> int:
        tokens = 0
        for child in self.children:
            if child.is_ignored:
                continue

            if isinstance(child, TextFileAnalysis):
                tokens += child.count_tokens()
            elif isinstance(child, DirectoryAnalysis):
                tokens += child.get_total_tokens()
        return tokens

    @property
    def size(self) -> int:
        size = 0
        for child in self.children:
            if isinstance(child, TextFileAnalysis):
                 size += child.size
            elif isinstance(child, DirectoryAnalysis):
                 size += child.size

        return size

    def get_non_ignored_text_content_size(self) -> int:
        size = 0
        for child in self.children:
            if child.is_ignored:
                continue    

            if isinstance(child, TextFileAnalysis) and child.file_content:
                size += len(child.file_content)
            elif isinstance(child, DirectoryAnalysis):
               size += child.get_non_ignored_text_content_size()
        return size
    
    def _get_all_non_ignored_files(self):
            files = []
            for child in self.get_non_ignored_children():
                if isinstance(child, TextFileAnalysis):
                   files.append(child)
                if isinstance(child, DirectoryAnalysis):
                   files.extend(child._get_all_non_ignored_files())
            return files
            

    def get_largest_files(self, n=10) -> List[TextFileAnalysis]:
        """Returns a list of the n largest non-ignored files in this directory and its subdirectories."""
        all_files = self._get_all_non_ignored_files()
        sorted_files = sorted(all_files, key=lambda file: file.size, reverse=True)
        return sorted_files[:n]

    def _get_all_non_ignored_directories(self):
        directories = []
        for child in self.get_non_ignored_children():
            if isinstance(child, DirectoryAnalysis):
                directories.append(child)
                directories.extend(child._get_all_non_ignored_directories())

        return directories


    def get_largest_directories(self, n=10) -> List["DirectoryAnalysis"]:
        """Returns a list of the n largest non-ignored directories in this directory and its subdirectories."""
        all_directories = self._get_all_non_ignored_directories()
        sorted_directories = sorted(all_directories, key=lambda directory: directory.size, reverse=True)
        return sorted_directories[:n]


    def to_dict(self):
        return {
            "name": self.name,
            "type": self.type,
            "size": self.size,
            "is_ignored": self.is_ignored,
            "non_ignored_text_content_size": self.get_non_ignored_text_content_size(),
            "total_tokens": self.get_total_tokens(),
            "file_count": self.get_file_count(),
            "dir_count": self.get_dir_count(),
            "children": [child.to_dict() for child in self.children]
        }