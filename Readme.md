# Readme 

This project is a lightweight version of [Codebase Digest](https://github.com/kamilstanuch/codebase-digest), designed to analyze and summarize your codebase into a single-file dump. The generated output includes:
- Code structure and contents
- A basic summary of the codebase

This output can be used as input for Large Language Models (LLMs) like ChatGPT, Google Gemini, and others for further analysis or to support prompt-based tasks.

For inspiration on possible prompts, refer to the [LLM Prompts section](https://github.com/kamilstanuch/codebase-digest?tab=readme-ov-file#llm-prompts-for-enhanced-analysis) in the Codebase Digest repository.

# How to use

## Installation

### Option 1: Install via pip

You can install codebase-dump directly from PyPI:

```bash
pip install codebase-dump
```

### Option 2: Install by Cloning the Repository

Clone setup repository 

```bash
git clone https://github.com/your-username/codebase-dump.git
cd codebase-dump
pip install -r requirements.txt
```

I recommend opening this project in Visual Studio Code and setting up a virtual environment. 

## Usage

### Command Line
Once installed, you can run codebase-dump from the command line:

```bash
codebase-dump <path_to_codebase> -f <output_filename> -o <output_format>
```

For example, to generate a markdown file of your project’s code structure:

```bash
codebase-dump . -f project_dump_for_llm.md -o markdown
```

### From Source

You can also run codebase-dump directly from the source code:

```bash
python app.py <path_to_codebase> -f <output_filename> -o <output_format>
```

### Usage in GitHub Actions
You can automate codebase-dump in a GitHub Actions workflow to generate and save the code dump as an artifact. Here’s an example workflow configuration (working example available in this own repository: [.github/workflows/codebase_dump.yml](.github/workflows/codebase_dump.yml)).


```yaml
name: Generate Project Dump for LLM

on:
  workflow_dispatch:

jobs:
  generate-file:
    runs-on: ubuntu-latest

    steps:
      - name: Checkout code
        uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v3
        with:
          python-version: "3.10"

      - name: Install codebase-dump
        run: pip install codebase-dump

      - name: Generate Single-File Prompt for LLM
        run: codebase-dump . -f project_dump_for_llm.md -o markdown 

      - name: Upload Prompt File as Artifact
        uses: actions/upload-artifact@v3
        with:
          name: project_dump_for_llm.md
          path: project_dump_for_llm.md
```

In this example:

- The workflow is triggered manually with workflow_dispatch.
- It installs codebase-dump and generates a .md file named project_dump_for_llm.md, containing the code structure and summary.
- The generated file is then uploaded as an artifact for easy access and download.
