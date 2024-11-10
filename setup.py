from setuptools import setup, find_packages

setup(
    name="codebase-dump",
    version="0.1.0",
    description="Generate a single-file dump of your repository, so you can use it as LLM input",
    author="Mirek Stanek, Kamil Stanuch",
    author_email="mirek@practicalengineering.management, kamil@stanuch.eu",
    packages=find_packages("src"),
    package_dir={"": "src"},
    install_requires=["tiktoken"],  # List core dependencies here
    extras_require={
        "dev": ["pytest"]  # Development dependencies
    },
    python_requires=">=3.7",
)