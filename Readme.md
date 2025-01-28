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

### Available Arguments

| Option | Description |
|--------|-------------|
| `path_to_directory` | Path to the directory you want to analyze |
| `-o, --output-format` | Output format (text, markdown). Default: text |
| `-f, --file` | Output file name |
| `--max-size` | Maximum allowed text content size in KB (default: 10240 KB) |
| `--ignore-top-large-files` | Number of largest files to ignore (default: 0) |
| `--audit-upload` | Send the output to the audits API as defined by `--audit-base-url` parameter |
| `--audit-base-url`  | API Base URL to send the audit to (default: https://codeaudits.ai/) |

### Examples

Generate a markdown file of your project’s code structure:

```bash
codebase-dump . -f project_dump_for_llm.md -o markdown
```

---

Generate a markdown file and push it to the audits app codeaudits.ai:

```bash
codebase-dump . -o markdown --audit-upload
```

---

Generate a markdown file and push it to custom instance of audits app:

```bash
codebase-dump . -o markdown --audit-upload --audit-base-url https://your-audit-instance.com/
```

---

Generate a markdown file while ignoring top 5 largest files and push it to the audits app codeaudits.ai:

```bash
codebase-dump . -o markdown --audit-upload --ignore-top-large-files=5
```


### From Source

You can also run codebase-dump directly from the source code:

```bash
pip install -e .
python src/codebase_dump/app.py <path_to_codebase> -f <output_filename> -o <output_format>
```

### Try online with Google Colab

You can try codebase-dump in an online environment, Google Colab. It can be a good option if you don't have a Python environment on your computer. Just launch it here: [codebase-dump Colab](https://colab.research.google.com/drive/1dchobm2d5V8vYBYtlMVosP7jGeDKhDiJ?usp=sharing). To test it out, run all the code via Runtime -> Run All.



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
        run: codebase-dump . -f project_dump_for_llm.md -o markdown --audit-upload

      - name: Upload Prompt File as Artifact
        uses: actions/upload-artifact@v3
        with:
          name: project_dump_for_llm.md
          path: project_dump_for_llm.md
```

In this example:

- The workflow is triggered manually with workflow_dispatch.
- It installs codebase-dump and generates a .md file named project_dump_for_llm.md, containing the code structure and summary.
- The --audit-upload flag sends the output to the audits API on https://codeaudits.ai/
- The generated file is then uploaded as an artifact for easy access and download.

## What next?

### Use it on your own
Once you get your codebase dump, copy that into one of LLMs as input prompt and start asking Gemini, ChatGPT, Claude and others questions related to your codebase. For example, ask about "what are suggested steps to refactor this code into //your choice// architecture.". 

For inspiration on possible prompts, check [LLM Prompts section](https://github.com/kamilstanuch/codebase-digest?tab=readme-ov-file#llm-prompts-for-enhanced-analysis) in the Codebase Digest repository.

## Use Code Audits

Parsed codebase was also uploaded to https://codeaudits.ai/ application. When you launch the link which was returned to you, you can run some pre-configured code audits, like architecture refactoring hints, missing tests or simplification hints. 