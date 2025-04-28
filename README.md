# iwadi - CLI Research Assistant

![Python Version](https://img.shields.io/badge/python-3.8%2B-blue)
![License](https://img.shields.io/badge/license-MIT-green)

A command-line tool for managing academic papers with AI-powered search, organization, and analysis.


## Development Setup

### Prerequisites
- Python 3.8+
- pip 20.3+

### Windows (PowerShell)
```powershell
python -m venv .venv # only needed once
.venv\Scripts\activate # run each time

pip install -e . # only when dependencies change/new .venv
```
### macOS/Linux
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -e .
```

### proper encoding with requirements.txt
```bash
pip freeze | Out-File -Encoding utf8 requirements.txt
```

### formatting and linting
```bash
ruff format && ruff check . && mypy .
```