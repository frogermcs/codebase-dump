from setuptools import setup, find_packages

setup(
    name="codebase-dump",
    version="0.5.2",
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
