# iwadi - CLI Research Assistant

![Python Version](https://img.shields.io/badge/python-3.8%2B-blue)
![License](https://img.shields.io/badge/license-MIT-green)

A command-line tool for managing academic papers with AI-powered search, organization, and analysis.


## Development Setup

### Prerequisites
- Python 3.8+
- pip 20.3+


### macOS/Linux
```bash
python3 -m venv .venv # only needed once
source .venv/bin/activate # run each time
pip install -e . # not sure how often this should be

```

### install requirements
```bash
pip install -r requirements.txt
```

### updating requirements.txt
```bash
pip freeze > requirements.txt
```

### formatting and linting
```bash
make build
```
runs: `ruff format && ruff check . && mypy .`

### Testing
```bash
pip uninstall iwadi
rm -rf src/iwadi.egg-info
pip install -e .
```