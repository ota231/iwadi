# 🧠 iwadi - CLI Research Assistant

![Python Version](https://img.shields.io/badge/python-3.8%2B-blue)
![License](https://img.shields.io/badge/license-MIT-green)

Originating from the yoruba translation of "investigation" iwadi is a command-line research assistant designed to streamline your academic workflow. It helps you manage papers, extract metadata, and leverage local LLMs for AI-powered search, summarization, and conversational queries — all while keeping your data fully local and private.


📚 Full documentation: https://ota231.github.io/iwadi/

## ✨ Features
- 🗂️ Browse different scholarly websites from the comfort of your CLI

- 🔍 Automated management and storage of desired papers

- 🤖 (still under development): AI support including chatting with papers, finding similar papers, and visualizing relevent data

## Installation

Clone the repository

```bash
git clone https://github.com/ota231/iwadi
cd iwadi
```

Create and activate virtual environment
```bash
python3 -m venv .venv  # One-time setup
source .venv/bin/activate  # Run each time you work
```

Install requirements
```bash
pip install -r requirements.txt
```

Set your IEEE API key in a local `.env` file:
```bash
echo "IEEE_API_KEY=your_key_here" > .env
```

## 🛠️ Development & Build
```bash
make format     # Format code with Ruff
make check      # Run type checking with mypy
make test       # Run tests
make docs       # Build Sphinx docs
make build      # Package the project
pip freeze > requirements.txt  # Update dependency list
```


## ⚙️ Simulating the CLI Locally
To test the CLI on your machine as if installed via `pip`:
```bash
pip uninstall iwadi
rm -rf src/iwadi.egg-info  # If it exists
pip install -e .  # Editable install
```