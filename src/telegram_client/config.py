"""Config loading and validation helpers."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from .exceptions import TelegramConfigError


def load_json_config(config_path: str | Path) -> dict[str, Any]:
    """Load and parse a JSON config file."""
    path = Path(config_path)

    try:
        content = path.read_text(encoding="utf-8")
    except FileNotFoundError as exc:
        raise TelegramConfigError(f"Config file not found: {path}") from exc
    except OSError as exc:
        raise TelegramConfigError(f"Unable to read config file: {path}") from exc

    try:
        data = json.loads(content)
    except json.JSONDecodeError as exc:
        raise TelegramConfigError(f"Invalid JSON in config file: {path}") from exc

    if not isinstance(data, dict):
        raise TelegramConfigError(f"Config root must be a JSON object: {path}")

    return data


def get_telegram_config(config: dict[str, Any]) -> dict[str, Any]:
    """Extract the top-level telegram config block."""
    telegram_config = config.get("telegram")
    if not isinstance(telegram_config, dict):
        raise TelegramConfigError("Missing or invalid top-level 'telegram' config section")
    return telegram_config


def validate_telegram_config(telegram_config: dict[str, Any]) -> dict[str, str]:
    """Validate required Telegram config fields and return a normalised mapping."""
    token = telegram_config.get("token")
    chat_id = telegram_config.get("chat_id")
    parse_mode = telegram_config.get("parse_mode")

    if not isinstance(token, str) or not token.strip():
        raise TelegramConfigError("Missing or invalid 'telegram.token'")
    if not isinstance(chat_id, str) or not chat_id.strip():
        raise TelegramConfigError("Missing or invalid 'telegram.chat_id'")
    if parse_mode is not None and not isinstance(parse_mode, str):
        raise TelegramConfigError("Invalid 'telegram.parse_mode': must be a string")

    validated: dict[str, str] = {"token": token, "chat_id": chat_id}
    if parse_mode is not None and parse_mode.strip():
        validated["parse_mode"] = parse_mode
    return validated


def load_telegram_config(config_path: str | Path) -> dict[str, str]:
    """Load and validate Telegram config from file."""
    config = load_json_config(config_path)
    telegram_config = get_telegram_config(config)
    return validate_telegram_config(telegram_config)
