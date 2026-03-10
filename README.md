# simple-telegram-client

Small reusable Python client for sending Telegram messages from JSON config.

## Milestone 1 scaffold

Project scaffolding now includes:
- `src/telegram_client/` package skeleton
- `tests/` skeleton with pytest baseline
- `requirements/` with `requirements.in` and `dev-requirements.in`
- `Makefile` with `init`, `test`, `lint`, `format`, `check`
- `pyproject.toml` build and tool configuration

## Quick start

### 1. Create and activate a virtualenv

macOS/Linux:

```bash
python -m venv .venv
source .venv/bin/activate
```

Windows (PowerShell):

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```

### 2. Install and sync dependencies

```bash
make init
```

### 3. Run tests

```bash
make test
```

### 4. Run lint/format checks (optional)

```bash
make check
```
