from setuptools import setup, find_packages
import os
import sys

src_dir = os.path.join(os.path.dirname(__file__), "src")
if src_dir not in sys.path:
    sys.path.insert(0, src_dir)

from codebase_dump._version import __version__

setup(
    name="codebase-dump",
    version=__version__,
    description="Parse your repository into single-file prompt, so you can use it as an LLM input.",
    author="Mirek Stanek, Kamil Stanuch",
    author_email="mirek@practicalengineering.management, kamil@stanuch.eu",
    packages=find_packages("src"),
    package_dir={"": "src"},
    install_requires=["tiktoken", "gitignore_parser"],
    extras_require={
        "dev": ["pytest", "twine"]
    },
    entry_points={
    'console_scripts': [
        'codebase-dump=codebase_dump.app:main',
    ]},
    python_requires=">=3.7",
)