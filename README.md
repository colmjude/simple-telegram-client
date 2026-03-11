# simple-telegram-client

Small reusable Python client for sending Telegram messages from JSON config.

## What it does

- Sends Telegram text messages through the Bot API.
- Sends markdown file contents as message text.
- Supports per-call `chat_id` overrides for dynamic replies.
- Provides a thin `get_updates()` wrapper for one-shot update fetches.
- Loads config from JSON (`telegram` top-level block).
- Uses clear custom exceptions for config/file/request failures.

## v1 scope

Included:
- outbound message sending
- config loading and validation
- markdown file content sending
- thin one-shot `get_updates` transport helper

Not included:
- polling loops or listener runtime
- webhook server handling
- command parsing/routing
- authz or permissions policy
- script execution/orchestration
- scheduling/retry policy
- document/file upload

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

### 4. Run main checks (optional)

```bash
make check
```

This runs `isort`, `black`, and `flake8` against `src/`, plus `pytest`.

### 5. Run test-file style checks separately (optional)

```bash
make check-tests
```

## Configuration

Create `config.json` in the project root (or pass a custom path to `TelegramClient`):

```json
{
  "telegram": {
    "token": "YOUR_BOT_TOKEN",
    "chat_id": "YOUR_CHAT_ID",
    "parse_mode": "Markdown"
  }
}
```

Required:
- `telegram.token`

Optional:
- `telegram.chat_id` (default destination for outbound sends)
- `telegram.parse_mode`

## Usage

```python
from telegram_client import TelegramClient

client = TelegramClient(config_path="config.json")
client.send_message("Hello from simple-telegram-client")
```

### Reply to a specific chat ID per call

```python
client.send_message("Reply text", chat_id=123456789)
```

### Send markdown file contents

```python
from telegram_client import TelegramClient

client = TelegramClient(config_path="config.json")
client.send_markdown_file("report.md", chat_id="123456789")
```

### Override parse mode per call

```python
client.send_message("*Bold message*", parse_mode="Markdown")
```

### Fetch updates (thin transport wrapper)

```python
updates = client.get_updates(offset=100, timeout=15, allowed_updates=["message"])
```

This method only wraps Telegram `getUpdates`. Polling loops and command handling belong in the consuming application.

## Error handling

The library raises:
- `TelegramConfigError`
- `TelegramFileError`
- `TelegramRequestError`

All derive from `TelegramClientError`.

## Manual integration test (see it in action)

1. Create a Telegram bot with `@BotFather` and copy the bot token.
2. Send any message to your bot in Telegram.
3. Get your chat id using:

```bash
curl "https://api.telegram.org/bot<YOUR_BOT_TOKEN>/getUpdates"
```

4. Put `token` and `chat_id` into `config.json`.
5. Run this one-liner from the repo root:

```bash
PYTHONPATH=src python -c "from telegram_client import TelegramClient; TelegramClient('config.json').send_message('Hello from local test')"
```

If successful, you should receive the message in Telegram immediately.

## BotFather setup guide

### 1. Create your bot

1. Open Telegram and search for `@BotFather`.
2. Start a chat and run:
   - `/newbot`
3. Follow prompts:
   - bot display name (for example `Simple Telegram Client Bot`)
   - bot username ending in `bot` (for example `simple_telegram_client_bot`)

### 2. Copy your bot token

- BotFather returns an HTTP API token that looks like:
  - `123456789:AA...`
- Keep this secret and store it in your local `config.json` as `telegram.token`.

### 3. Get your chat ID

1. Open your bot chat and send a message (for example `hello`).
2. Run:

```bash
curl "https://api.telegram.org/bot<YOUR_BOT_TOKEN>/getUpdates"
```

3. In the JSON response, find:
   - `result[0].message.chat.id`
4. Put this value in `config.json` as `telegram.chat_id`.

### 4. Optional BotFather commands

- `/setdescription` to set bot description
- `/setuserpic` to set bot profile image
- `/mybots` to manage existing bots

## Example script

An executable example is included at:
- `examples/send_test_message.py`

Run it with:

```bash
PYTHONPATH=src python examples/send_test_message.py --config config.json --text "Hello from example script"
```
