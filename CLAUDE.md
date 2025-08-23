# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

AutoTerminal is a smart terminal tool based on large language models (LLM) that converts natural language into terminal commands to improve work efficiency.

## Code Architecture

```
autoterminal/
├── __init__.py             # Package initialization
├── main.py                 # Main program entry point
├── config/                 # Configuration management module
│   ├── __init__.py         # Package initialization
│   ├── loader.py           # Configuration loader
│   └── manager.py          # Configuration manager
├── llm/                    # LLM related modules
│   ├── __init__.py         # Package initialization
│   └── client.py           # LLM client
├── history/                # Command history management module
│   ├── __init__.py         # Package initialization
│   └── history.py          # History manager
├── utils/                  # Utility functions
│   ├── __init__.py         # Package initialization
│   └── helpers.py          # Helper functions
```

### Key Components

1. **Main Entry Point** (`autoterminal/main.py`): 
   - Parses command-line arguments
   - Loads configuration
   - Initializes LLM client
   - Generates and executes commands
   - Manages command history

2. **Configuration Management** (`autoterminal/config/`):
   - `loader.py`: Loads configuration from file
   - `manager.py`: Manages configuration saving, validation, and initialization

3. **LLM Integration** (`autoterminal/llm/client.py`):
   - Wraps OpenAI API client
   - Generates terminal commands from natural language input
   - Incorporates context from command history and current directory

4. **Command History** (`autoterminal/history/history.py`):
   - Manages command history storage and retrieval
   - Provides context for LLM generation

5. **Utilities** (`autoterminal/utils/helpers.py`):
   - Provides helper functions like command cleaning

## Common Development Commands

### Installation

Using uv (development mode):
```bash
uv sync
```

Using pip (user installation):
```bash
pip install --user .
```

### Running the Application

Using uv run:
```bash
uv run python autoterminal/main.py "list all files in current directory"
```

After installation, use the `at` command:
```bash
at "list all files in current directory"
```

Using history context:
```bash
at --history-count 5 "based on previous commands, delete all .txt files"
```

### Development

The project uses setuptools for packaging and distribution. Entry point is defined in both `pyproject.toml` and `setup.py`.

## Key Features

- LLM-based intelligent command generation
- Secure command execution mechanism (requires user confirmation)
- Flexible configuration management
- Chinese language support
- Support for multiple LLM models (OpenAI GPT series and compatible APIs)
- Command history tracking and context awareness
- Current directory content context awareness
- Configurable history size