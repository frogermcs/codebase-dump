import os
import fnmatch

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

        self.init_ignore_patterns()


    def init_ignore_patterns(self):
        patterns = set()

        if self.load_default_ignore_patterns:
            patterns.update(IgnorePatternManager.DEFAULT_IGNORE_PATTERNS)
        
        if self.extra_ignore_patterns:
            patterns.update(self.extra_ignore_patterns)
        
        cdigestignore_path = os.path.join(self.base_path, '.cdigestignore')
        if self.load_cdigestignore and os.path.exists(cdigestignore_path):
            with open(cdigestignore_path, 'r') as f:
                file_patterns = {line.strip() for line in f if line.strip() and not line.startswith('#')}
            patterns.update(file_patterns)
        
        gitignore_path = os.path.join(self.base_path, '.gitignore')
        if self.load_gitignore and os.path.exists(gitignore_path):
            with open(gitignore_path, 'r') as f:
                file_patterns = {line.strip() for line in f if line.strip() and not line.startswith('#')}
            patterns.update(file_patterns)

        self.ignore_patterns = patterns
    
    def should_ignore(self, path, base_path):
        """Checks if a file or directory should be ignored based on patterns."""
        name = os.path.basename(path)
        rel_path = os.path.relpath(path, base_path)
        abs_path = os.path.abspath(path)
        
        for pattern in self.ignore_patterns:
            if fnmatch.fnmatch(name, pattern) or \
            fnmatch.fnmatch(rel_path, pattern) or \
            fnmatch.fnmatch(abs_path, pattern) or \
            (pattern.startswith('/') and fnmatch.fnmatch(abs_path, os.path.join(base_path, pattern[1:]))) or \
            any(fnmatch.fnmatch(part, pattern) for part in rel_path.split(os.sep)):
                return True
        return False