from codebase_dump.core.models import DirectoryAnalysis, NodeAnalysis, TextFileAnalysis
from typing import List
import os

class OutputFormatterBase:
    def output_file_extension(self):
        raise NotImplemented

    def format(self, data: DirectoryAnalysis) -> str:
        raise NotImplemented
    
    def generate_tree_string(self, node: NodeAnalysis, prefix="", is_last=True, show_size=False, show_ignored=False):
        """Generates a string representation of the directory tree."""
        if node.is_ignored and not show_ignored:
            return ""

        result = prefix + ("└── " if is_last else "├── ") + node.name

        if show_size and isinstance(node, TextFileAnalysis):
            result += f" ({node.size} bytes)"

        if node.is_ignored:
            result += " [IGNORED]"

        result += "\n"

        if isinstance(node, DirectoryAnalysis):
            prefix += "    " if is_last else "│   "
            children = node.children
            if not show_ignored:
                children = [child for child in children if not child.is_ignored]
            for i, child in enumerate(children):
                result += self.generate_tree_string(child, prefix, i == len(children) - 1, show_size, show_ignored)
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
        summary = "\nSummary:\n"
        summary += f"Total files analyzed: {data.get_file_count()}\n"
        summary += f"Total directories analyzed: {data.get_dir_count()}\n"
        summary += f"Estimated output size: {data.size / 1024:.2f} KB\n"
        summary += f"Actual analyzed size: {data.get_non_ignored_text_content_size() / 1024:.2f} KB\n"
        summary += f"Total tokens: {data.get_total_tokens()}\n"
        summary += f"Actual text content size: {data.size / 1024:.2f} KB\n"
        summary += f"Top largest files: {self.generate_top_files_string(data.get_largest_files())}\n"
        summary += f"Top largest directories: {self.generate_top_directories_string(data.get_largest_directories())}\n"

        ignored_files_string = self.generate_top_files_string([f for f in data._get_all_files() if f.is_ignored], prefix="- ")
        if  ignored_files_string and ignored_files_string != "- Top 0 largest files:\n":
            summary += f"\nTop ignored files (due to --ignore-top-files):\n {ignored_files_string}"

        return summary

    def generate_top_files_string(self, files: List[TextFileAnalysis], prefix=""):
        if not files:
            return f"{prefix}No large files found.\n"

        output = f"{prefix}Top {len(files)} largest files:\n"
        for file in files:
             output += f"{prefix}- {file.get_full_path()} ({file.size} bytes)\n"

        return output

    def generate_top_directories_string(self, directories: List[DirectoryAnalysis], prefix=""):
        if not directories:
           return f"{prefix}No large directories found.\n"

        output = f"{prefix}Top {len(directories)} largest directories:\n"
        for directory in directories:
            output += f"{prefix}- {directory.get_full_path()} ({directory.size} bytes)\n"
        return output
    
class PlainTextOutputFormatter(OutputFormatterBase):
    def output_file_extension(self):
        return ".txt"
    
    def format(self, data: DirectoryAnalysis) -> str:
        output = f"Parsed codebase for the project: {data.name}\n"
        output += "\nDirectory Structure:\n"
        output += self.generate_tree_string(data, show_size=True, show_ignored=True)
        output += self.generate_summary_string(data)
        output += "\nFile Contents:\n"
        for file in self.generate_content_string(data):
            output += f"\n{'=' * 50}\n"
            output += f"File: {file['path']}\n"
            output += f"{'=' * 50}\n"
            output += file['content']
            output += "\n"
        return output

class MarkdownOutputFormatter(OutputFormatterBase):
    def output_file_extension(self):
        return ".md"
    
    def format(self, data: DirectoryAnalysis) -> str:
        output = f"# Parsed codebase for the project: {data.name}\n\n"
        output += "## Directory Structure\n\n"
        output += "```\n"
        output += self.generate_tree_string(data, show_size=True, show_ignored=True)
        output += "```\n\n"
        output += "## Summary\n\n"
        output += f"- Total files: {data.get_file_count()}\n"
        output += f"- Total directories: {data.get_dir_count()}\n"
        output += f"- Total text file size (including ignored): {data.size / 1024:.2f} KB\n"
        output += f"- Total tokens: {data.get_total_tokens()}\n"
        output += f"- Analyzed text content size: {data.get_non_ignored_text_content_size() / 1024:.2f} KB\n\n"
        output += "## Top 10 Largest Files\n\n"
        output += self.generate_top_files_string(data.get_largest_files(), prefix="- ")
        output += "\n## Top 10 Largest Directories\n\n"
        output += self.generate_top_directories_string(data.get_largest_directories(), prefix="- ")
        output += "## File Contents\n\n"
        for file in self.generate_content_string(data):
            output += f"### {file['path']}\n\n```\n{file['content']}\n```\n\n"
        return output