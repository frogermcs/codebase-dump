from setuptools import setup, find_packages

setup(
    name="codebase-dump",
    version="0.1.7",
    description="Generate a single-file dump of your repository, so you can use it as LLM input",
    author="Mirek Stanek, Kamil Stanuch",
    author_email="mirek@practicalengineering.management, kamil@stanuch.eu",
    packages=find_packages("src"),
    package_dir={"": "src"},
    install_requires=["tiktoken", "gitignore_parser"],  # List core dependencies here
    extras_require={
        "dev": ["pytest", "twine"]  # Development dependencies
    },
    entry_points={
    'console_scripts': [
        'codebase-dump=codebase_dump.app:main',
    ]},
    python_requires=">=3.7",
)
