from codebase_dump.core.models import DirectoryAnalysis, NodeAnalysis, TextFileAnalysis
from typing import List
import os

class OutputFormatterBase:
    def output_file_extension(self):
        raise NotImplemented

    def format(self, data: DirectoryAnalysis, ignore_patterns: set) -> str:
        raise NotImplemented
    
    def generate_tree_string(self, node: NodeAnalysis, prefix="", is_last=True, show_size=False, show_ignored=False):
        """Generates a string representation of the directory tree."""
        if node.is_ignored and not show_ignored:
            return ""

        result = prefix + ("└── " if is_last else "├── ") + node.name

        if show_size and isinstance(node, TextFileAnalysis):
            result += f" ({node.size} bytes)"

        if node.is_ignored:
            result += " [Status: IGNORED]"

        result += "\n"

        if isinstance(node, DirectoryAnalysis):
            prefix += "    " if is_last else "│   "
            children = node.children
            if not show_ignored:
                children = [child for child in children if not child.is_ignored]
            for i, child in enumerate(children):
                result += self.generate_tree_string(child, prefix, i == len(children) - 1, show_size, show_ignored)
        return result
    
    def generate_tree_string_for_LLM(self, node: NodeAnalysis):
        """Generates a string representation of the directory tree readable by LLM."""

        if node.is_ignored:
            return ""

        result = "- " + node.get_full_path()

        if isinstance(node, DirectoryAnalysis):
            result += "/"

        if isinstance(node, TextFileAnalysis):
            result += f" ({node.size} bytes)"

        result += "\n"

        if isinstance(node, DirectoryAnalysis):
            children = node.children
            for i, child in enumerate(children):
                result += self.generate_tree_string_for_LLM(child)
        return result

    def generate_content_string(self, data: NodeAnalysis):
        """Generates a structured representation of file contents."""
        content = []

        def add_file_content(node, path=""):
            if isinstance(node, TextFileAnalysis) and not node.is_ignored and node.file_content != "[Non-text file]":
                content.append({
                    "path": os.path.join(path, node.name),
                    "content": node.file_content
                })
            elif isinstance(node, DirectoryAnalysis):
                for child in node.children:
                    add_file_content(child, os.path.join(path, node.name))

        add_file_content(data)
        return content
    
    def generate_summary_string(self, data: DirectoryAnalysis):
        output = ""
        output += f"- Total files: {len(data.get_all_non_ignored_files())}\n"
        output += f"- Total directories: {data.get_non_ignored_dir_count()}\n"
        output += f"- Total text file size (including ignored): {data.size / 1024:.2f} KB\n"
        output += f"- Total tokens: {data.get_total_tokens()}\n"
        output += f"- Analyzed text content size: {data.get_non_ignored_text_content_size() / 1024:.2f} KB\n\n"
        output += f"Top largest non-ignored files:\n{self.generate_top_files_string(data.get_largest_files())}\n"
        output += f"Top largest non-ignored directories:\n{self.generate_top_directories_string(data.get_largest_directories())}\n"       

        return output
    
    def generate_ignored_files_summary(self, data: DirectoryAnalysis, ignore_patterns: set):
        output = "During the analysis, some files were ignored:\n"
        output += f"- No of files ignored during parsing: {len(data.get_all_ignored_files())}\n"
        output += f"- Patterns used to ignore files: {ignore_patterns}\n"
        return output


    def generate_top_files_string(self, files: List[TextFileAnalysis], prefix=""):
        if not files:
            return f"{prefix}No large files found.\n"

        output = ""
        for file in files:
             output += f"{prefix}- {file.get_full_path()} ({file.size / 1024:.2f} kB)\n"

        return output

    def generate_top_directories_string(self, directories: List[DirectoryAnalysis], prefix=""):
        if not directories:
           return f"{prefix}No large directories found.\n"

        output = ""
        for directory in directories:
            output += f"{prefix}- {directory.get_full_path()} ({directory.size / 1024:.2f} kB)\n"
        return output
    
class PlainTextOutputFormatter(OutputFormatterBase):
    def output_file_extension(self):
        return ".txt"
    
    def format(self, data: DirectoryAnalysis, ignore_patterns: set) -> str:
        output = f"Parsed codebase for the project: {data.name}\n\n"
        output += "\nDirectory Structure:\n"
        output += self.generate_tree_string_for_LLM(data)
        output += "\n\n"
        output += "Summary\n\n"
        output += self.generate_summary_string(data)
        output += "Ignore summary:\n"
        output += self.generate_ignored_files_summary(data, ignore_patterns)
        output += "Files:\n\n"
        for file in self.generate_content_string(data):
            output += f"File: {file['path']}\n"
            output += f"---\n"
            output += f"Content:\n"
            output += file['content']
            output += "\n\n"
        return output

class MarkdownOutputFormatter(OutputFormatterBase):
    def output_file_extension(self):
        return ".md"
    
    def format(self, data: DirectoryAnalysis, ignore_patterns: set) -> str:
        output = f"# Parsed codebase for the project: {data.name}\n\n"
        output += "\n## Directory Structure\n"
        output += self.generate_tree_string_for_LLM(data)
        output += "\n## Summary\n"
        output += self.generate_summary_string(data)
        output += "\n## Ignore summary:\n"
        output += self.generate_ignored_files_summary(data, ignore_patterns)
        output += "\n## Files:\n"
        for file in self.generate_content_string(data):
            output += f"### {file['path']}\n\n```\n{file['content']}\n```\n\n"
        return output