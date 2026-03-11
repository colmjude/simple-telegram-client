# Product Requirements Document (PRD)

## Product
- Name: `simple-telegram-client`
- Type: Installable Python library for Telegram transport primitives
- Version target: v1.0.0 (initial usable release)

## Problem Statement
Teams and scripts repeatedly re-implement Telegram send logic (config parsing, payload shaping, API requests, and error handling). This creates duplication, inconsistent behaviour, and harder testing.

## Goals
- Provide a small, reusable Python package to send Telegram messages reliably.
- Standardise configuration via a JSON file with a top-level `telegram` block.
- Support sending markdown file contents as message text.
- Support control-centre reply workflows via per-call `chat_id` overrides.
- Expose a thin inbound transport primitive (`get_updates`) without adding bot runtime behaviour.
- Keep the API minimal, readable, and easy to test.

## Non-Goals (v1)
- Inbound polling loops or listener runtime.
- Webhook server handling.
- Command parsing, routing, or execution.
- Authorisation policy, orchestration, scheduling, or retry strategy.
- Telegram document/file upload.
- Opinionated application logging.

## Primary Users
- Local Python projects/scripts that need to send Telegram notifications.
- Developers who want a lightweight dependency rather than a full Telegram SDK.

## Success Criteria
- A local project can install and call the client in under 10 minutes.
- Core flows pass automated tests:
  - load valid config
  - send text message
  - send markdown file contents
  - fail clearly on invalid config/API errors
- Standard development workflow is reproducible via Make targets.

## Functional Requirements

### FR1: Config loading
- The library must accept `config_path` as optional input.
- If absent, default config path is `config.json` in current working directory.
- Config must be JSON with top-level key `telegram`.
- Required keys:
  - `telegram.token`
- Optional key:
  - `telegram.chat_id`
  - `telegram.parse_mode`

### FR2: Message sending
- Provide `TelegramClient.send_message(text, parse_mode=None, chat_id=None)`.
- Must call Telegram Bot API `sendMessage`.
- Must use per-call `chat_id` when provided.
- Must fall back to configured default `chat_id` when per-call value is absent.
- Must raise `TelegramConfigError` if no destination chat can be resolved.
- If per-call `parse_mode` is provided, it overrides config value.
- If no parse mode is set, omit parse mode from payload.
- Return Telegram API response payload(s) to caller.

### FR3: Message chunking
- If message text exceeds Telegram limits, split into chunks and send sequentially.
- v1 default max chunk size: 4000 characters for safe headroom.
- If any chunk send fails, raise a clear request exception and stop.

### FR4: Markdown file sending
- Provide `TelegramClient.send_markdown_file(path, parse_mode=None, chat_id=None)`.
- Read file content as text and send via `send_message`.
- Missing/unreadable file must raise a clear file exception.

### FR5: Thin inbound primitive
- Provide `TelegramClient.get_updates(offset=None, timeout=30, allowed_updates=None)`.
- Must call Telegram Bot API `getUpdates`.
- Must remain a one-shot transport wrapper (no loops/listener abstractions).

### FR6: Exceptions
- Provide a small custom hierarchy:
  - `TelegramClientError`
  - `TelegramConfigError`
  - `TelegramRequestError`
  - `TelegramFileError`
- Error messages must identify cause and failing input/path where relevant.

## Non-Functional Requirements
- Python version: `>=3.10` (validated on `3.10.13`).
- Dependency footprint: minimal (`requests` for HTTP).
- Code style: typed, readable, small functions; avoid monolithic methods.
- Library logging: minimal by default; calling applications own operational logging.

## Public API (v1)
```python
from telegram_client import TelegramClient

client = TelegramClient(config_path="config.json")
client.send_message("Hello")
client.send_message("Reply", chat_id=123456789)
client.send_markdown_file("report.md", chat_id=123456789)
client.get_updates(offset=100, timeout=15, allowed_updates=["message"])
```

## Package Structure (v1)
```text
simple-telegram-client/
  README.md
  pyproject.toml
  requirements/
    dev-requirements.in
    requirements.in
    dev-requirements.txt
    requirements.txt
  Makefile
  src/
    telegram_client/
      __init__.py
      client.py
      config.py
      exceptions.py
      utils.py
  tests/
    test_client.py
    test_config.py
    test_utils.py
```

## Tooling And Development Workflow

### Environment
- Use Python virtual environments for local development.

### Dependency management
- Use `pip-tools` for locked dependency files.
- Maintain:
  - runtime deps in `requirements/requirements.in` -> compiled to `requirements/requirements.txt`
  - dev deps in `requirements/dev-requirements.in` -> compiled to `requirements/dev-requirements.txt`

### Makefile targets
- `make init`: install/upgrade tooling, compile deps, sync deps.
- `make test`: run test suite with `pytest`.
- Recommended additional targets:
  - `make lint`: run `flake8`
  - `make format`: run `isort` then `black`
  - `make check`: run `isort --check-only`, `black --check`, `flake8`, `pytest`

Required `make init` target:

```make
init::
	python -m pip install --upgrade pip
	python -m pip install pip-tools
	python -m piptools compile requirements/dev-requirements.in
	python -m piptools compile requirements/requirements.in
	python -m piptools sync requirements/dev-requirements.txt requirements/requirements.txt
```

### Testing and quality tools
- Test framework: `pytest`
- Formatting: `black`
- Import sorting: `isort`
- Linting: `flake8`

## Acceptance Criteria
- `make init` sets up a working local dev environment from a clean checkout.
- `make test` passes on a clean checkout.
- `make check` passes with no formatting/lint/test failures.
- Unit tests cover:
  - config file not found
  - invalid JSON
  - missing `telegram`
  - missing required token
  - payload composition and parse mode override
  - chat-id resolution (configured default vs per-call override)
  - chunking behaviour
  - send return-value behaviour for single and chunked sends
  - markdown file read failure
  - getUpdates URL/payload handling
  - Telegram API error response handling

## Delivery Plan

### Milestone 1: Project scaffolding
- Add `pyproject.toml`, source layout, tests layout, requirements files, and Makefile.

### Milestone 2: Core implementation
- Implement chat-id resolution, outbound response returns, and `get_updates` helper.

### Milestone 3: Test coverage
- Add/green unit tests for all v1 acceptance paths.

### Milestone 4: Documentation
- Finalise README: setup, config, usage, testing, and manual integration test steps.

## Risks And Mitigations
- Risk: Telegram API edge cases (timeouts/non-JSON errors).
  - Mitigation: wrap request errors in `TelegramRequestError` with concise context.
- Risk: Hidden complexity growth.
  - Mitigation: enforce non-goals and keep v1 module boundaries small.

## Decision Outcomes
- Convenience functions: defer from v1. Class-based API only in initial release.
- Chunking boundary strategy: not material for v1; use a simple strict character split.
- Optional timeout configuration in constructor: defer from v1.
- Keep transport-only boundaries: no listener loops or bot runtime abstractions.
