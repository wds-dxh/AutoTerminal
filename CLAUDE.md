# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

AutoTerminal is an LLM-powered terminal assistant that converts natural language into shell commands. It's a Python CLI tool that uses OpenAI-compatible APIs to generate and execute terminal commands based on user input, with context awareness from command history and current directory contents.

## Development Commands

### Package Management
```bash
# Install dependencies (development mode)
uv sync

# Install package locally for testing
pip install --user -e .

# Uninstall
pip uninstall autoterminal
```

### Running the Tool
```bash
# Using uv run (development)
uv run python autoterminal/main.py "your command request"

# After installation
at "your command request"

# With history context
at --history-count 5 "command based on previous context"

# Command recommendation mode (no input)
at
```

### Building and Distribution
```bash
# Build distribution packages
python -m build

# Upload to PyPI (requires twine)
twine upload dist/*
```

## Architecture

### Core Flow
1. **User Input** → CLI argument parsing (`main.py`)
2. **Configuration Loading** → ConfigLoader/ConfigManager retrieve user settings from `~/.autoterminal/config.json`
3. **Context Gathering** → HistoryManager fetches recent commands + glob current directory contents
4. **LLM Generation** → LLMClient sends prompt with context to OpenAI-compatible API
5. **Command Execution** → User confirms, then command executes via `os.system()`
6. **History Persistence** → Executed command saved to `~/.autoterminal/history.json`

### Key Components

**autoterminal/main.py**
- Entry point for `at` command
- Argument parsing and orchestration
- Two modes: command generation (with user input) and recommendation mode (without input)
- Uses `glob.glob("*")` to gather current directory context

**autoterminal/llm/client.py**
- `LLMClient` class wraps OpenAI API
- `generate_command()` constructs prompts with history and directory context
- Two prompt modes: default (user command) and recommendation (auto-suggest)
- System prompt includes recent command history and current directory files

**autoterminal/config/**
- `ConfigLoader`: Reads from `~/.autoterminal/config.json`
- `ConfigManager`: Interactive setup wizard, validation, and persistence
- Required fields: `api_key`, `base_url`, `model`
- Optional: `max_history`, `default_prompt`, `recommendation_prompt`

**autoterminal/history/**
- `HistoryManager`: Persists commands to `~/.autoterminal/history.json`
- Stores: `timestamp`, `user_input`, `generated_command`, `executed` flag
- `get_last_executed_command()` prevents duplicate recommendations

**autoterminal/utils/helpers.py**
- `clean_command()`: Strips quotes and whitespace from LLM output
- `get_shell_history(count)`: Reads shell history from `~/.bash_history` or `~/.zsh_history`
  - Filters sensitive commands (password, key, token, etc.)
  - Handles zsh extended history format
  - Deduplicates commands (keeps last occurrence)
  - Returns up to N most recent commands

**autoterminal/utils/logger.py**
- Configures `loguru` for structured logging
- Console output to stderr (colored, configurable via `AUTOTERMINAL_LOG_LEVEL` env var)
- File output to `~/.autoterminal/autoterminal.log` (rotation: 10MB, retention: 7 days)
- Logging levels: ERROR for console (default, production mode), DEBUG for file
- Enable verbose console logging: `AUTOTERMINAL_LOG_LEVEL=INFO` or `DEBUG`
- Disable file logging: `AUTOTERMINAL_FILE_LOG=false`

### Configuration Storage
All user data lives in `~/.autoterminal/`:
- `config.json`: API credentials and settings
- `history.json`: Command execution history
- `autoterminal.log`: Application logs (rotated at 10MB, compressed)

### Installation Mechanism
`pyproject.toml` defines:
- Entry point: `at = "autoterminal.main:main"`
- Dependencies: `openai>=1.0.0`, `loguru>=0.7.0`
- Python requirement: `>=3.10`
- Build system: setuptools

## Important Implementation Details

### Context-Aware Command Generation
The LLM receives four critical context inputs:
1. **Command History**: Last N commands from AutoTerminal (user input + generated command pairs)
2. **Directory Contents**: Output of `glob.glob("*")` in current working directory
3. **Shell History**: Last 20 commands from user's shell history (bash/zsh) via `get_shell_history()`
4. **Last Executed Command**: Used in recommendation mode to avoid repeats

### Two Operating Modes
1. **Command Generation Mode** (`at "do something"`):
   - Uses `default_prompt` from config
   - Generates command from user's natural language request

2. **Recommendation Mode** (`at` with no args):
   - Uses `recommendation_prompt` from config
   - Analyzes context to suggest next likely command
   - Returns empty string if context insufficient
   - Special logic to avoid recommending `echo` commands for listing files

### Safety Mechanism
Commands are always displayed before execution with "Press Enter to execute..." prompt. User must explicitly confirm (Enter key) before execution via `os.system()`.

### Command Cleaning
LLM output is processed through `clean_command()` to remove:
- Leading/trailing quotes (single or double)
- Excess whitespace
- Prevents common LLM wrapping artifacts

## Development Notes

### When modifying prompts:
- System prompts are in `config/manager.py` defaults and configurable via `config.json`
- Recommendation prompt explicitly instructs against `echo` for file listing
- Context is appended to system prompt, not injected into user message

### When working with history:
- History is capped at `max_history` entries (default: 10)
- Stored in reverse chronological order
- `get_recent_history()` returns oldest-to-newest slice for context

### When extending LLM support:
- Client uses `openai` package with custom `base_url`
- Compatible with any OpenAI API-compatible service
- Temperature fixed at 0.1, max_tokens at 100 for deterministic short outputs

### Configuration initialization:
- First run triggers interactive setup wizard
- Config validation checks for all required keys
- Command-line args (`--api-key`, `--base-url`, `--model`) override config file

### Logging and Debugging:
- All modules use centralized `loguru` logger from `autoterminal.utils.logger`
- **Production mode**: Console only shows ERROR messages (default)
- **Debug mode**: `AUTOTERMINAL_LOG_LEVEL=DEBUG at "command"` shows all logs
- File logs: Always DEBUG level at `~/.autoterminal/autoterminal.log` (unless disabled)
- View logs: `tail -f ~/.autoterminal/autoterminal.log`
- Key events logged: config loading, LLM calls, command execution, history updates, shell history reading

### Shell History Integration:
- `get_shell_history()` automatically detects bash/zsh history files
- Detection strategy:
  1. Tries `$HISTFILE` environment variable
  2. Detects `$SHELL` to determine shell type (zsh/bash)
  3. Prioritizes history files based on detected shell
  4. Falls back to common locations (`~/.bash_history`, `~/.zsh_history`, etc.)
- Sensitive keyword filtering prevents leaking credentials
- Shell history provides additional context beyond AutoTerminal's own history
- Failure to read shell history is non-fatal (returns empty list with warning)
