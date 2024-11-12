import os
import fnmatch
import re

# TODO: Add support for negation patterns
class IgnorePatternManager:

    DEFAULT_IGNORE_PATTERNS = [
        '*.pyc', '*.pyo', '*.pyd', '__pycache__',  # Python
        'node_modules', 'bower_components',        # JavaScript
        '.git', '.svn', '.hg', '.gitignore',       # Version control
        'venv', '.venv', 'env',                    # Virtual environments
        '.idea', '.vscode',                        # IDEs
        '*.log', '*.bak', '*.swp', '*.tmp',        # Temporary and log files
        '.DS_Store',                               # macOS
        'Thumbs.db',                               # Windows
        'build', 'dist',                           # Build directories
        '*.egg-info',                              # Python egg info
        '*.so', '*.dylib', '*.dll'                 # Compiled libraries
    ]

    def __init__(self, 
                 base_path,
                 load_default_ignore_patterns=True, 
                 load_gitignore=True, 
                 load_cdigestignore=True,
                 extra_ignore_patterns=set()):
        self.base_path = base_path
        self.load_default_ignore_patterns=load_default_ignore_patterns
        self.load_gitignore=load_gitignore
        self.load_cdigestignore = load_cdigestignore
        self.extra_ignore_patterns = extra_ignore_patterns

        self.ignore_patterns = set()
        self.ignore_patterns_as_str = set()

        self.init_ignore_patterns()


    def init_ignore_patterns(self):
        self.ignore_patterns = set()

        if self.load_default_ignore_patterns:
            for pattern in IgnorePatternManager.DEFAULT_IGNORE_PATTERNS:
                self.ignore_patterns_as_str.add(pattern)
                self.ignore_patterns.add(self.str_to_regex(pattern))
        
        if self.extra_ignore_patterns:
            for pattern in self.extra_ignore_patterns:
                self.ignore_patterns_as_str.add(pattern)
                self.ignore_patterns.add(self.str_to_regex(pattern))
        
        cdigestignore_path = os.path.join(self.base_path, '.cdigestignore')
        if self.load_cdigestignore and os.path.exists(cdigestignore_path):
            regex_patterns, string_patterns = self.parse_gitignore(cdigestignore_path)
            self.ignore_patterns_as_str.update(string_patterns)
            self.ignore_patterns.update(regex_patterns)
        
        gitignore_path = os.path.join(self.base_path, '.gitignore')
        if self.load_gitignore and os.path.exists(gitignore_path):
            regex_patterns, string_patterns = self.parse_gitignore(gitignore_path)
            self.ignore_patterns_as_str.update(string_patterns)
            self.ignore_patterns.update(regex_patterns)

    
    def parse_gitignore(self, gitignore_path=".gitignore"):
        """Parses a .gitignore file and returns a list of compiled regex patterns."""
        regex_patterns = []
        string_patterns = []
        with open(gitignore_path, "r") as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith("#"):
                    continue
                
                string_patterns.append(line)
                regex_patterns.append(self.str_to_regex(line))
        return regex_patterns, string_patterns

    def str_to_regex(self, pattern):
        """Converts a glob pattern to a regex pattern."""
        if pattern is None:
            return None

        is_directory_pattern = pattern.endswith("/")

        regex = re.escape(pattern).replace(r"\*", ".*").replace(r"\?", ".")

        if is_directory_pattern:
            # Match directories by ensuring a trailing slash or end of path
            regex = f"(?:.*/)?{regex.rstrip('/')}/?$"
        else:
            # Match regular files or paths
            regex = f"(?:.*/)?{regex}(?:/.*)?$"

        return re.compile(regex)

    def should_ignore(self, path, base_path):
        """Checks if a file or directory should be ignored based on patterns."""
        for pattern in self.ignore_patterns:
            if pattern.match(path):
                return True
        return False