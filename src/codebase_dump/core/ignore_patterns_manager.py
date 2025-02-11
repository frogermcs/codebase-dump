import os

from py_walk import get_parser_from_list

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

        self.ignore_patterns_as_str = set()
        
        self.init_ignore_patterns()
        print("Ignore Patterns: ", self.ignore_patterns_as_str)

        if base_path == ".":
            self.base_path = os.getcwd()
        else:
            self.base_path = base_path


    def init_ignore_patterns(self):
        """Initializes the ignore patterns based on the configuration."""
        if self.load_default_ignore_patterns:
            for pattern in IgnorePatternManager.DEFAULT_IGNORE_PATTERNS:
                self.ignore_patterns_as_str.add(pattern)
        
        if self.extra_ignore_patterns:
            for pattern in self.extra_ignore_patterns:
                self.ignore_patterns_as_str.add(pattern)
        
        cdigestignore_path = os.path.join(self.base_path, '.cdigestignore')
        if self.load_cdigestignore and os.path.exists(cdigestignore_path):
            self.parse_gitignore(cdigestignore_path)
        
        gitignore_path = os.path.join(self.base_path, '.gitignore')
        if self.load_gitignore and os.path.exists(gitignore_path):
            self.parse_gitignore(gitignore_path)
        
    def parse_gitignore(self, gitignore_path=".gitignore"):
        """Parses a .gitignore file and returns a list of compiled regex patterns."""
        with open(gitignore_path, "r") as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith("#"):
                    continue
                                
                self.ignore_patterns_as_str.add(line)
   
    def should_ignore(self, path):
        parser = get_parser_from_list(self.ignore_patterns_as_str, base_dir=self.base_path)
        return parser.match(path)