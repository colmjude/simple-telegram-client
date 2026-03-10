"""Utility helpers for payloads, files, and HTTP transport."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import requests

from .exceptions import TelegramFileError, TelegramRequestError

TELEGRAM_MAX_MESSAGE_LENGTH = 4000


def chunk_text(text: str, max_length: int = TELEGRAM_MAX_MESSAGE_LENGTH) -> list[str]:
    """Split text into strict character chunks."""
    if max_length <= 0:
        raise ValueError("max_length must be greater than 0")
    if len(text) <= max_length:
        return [text]
    return [text[i : i + max_length] for i in range(0, len(text), max_length)]


def build_send_message_payload(
    chat_id: str,
    text: str,
    parse_mode: str | None = None,
) -> dict[str, str]:
    """Build Telegram sendMessage payload."""
    payload: dict[str, str] = {"chat_id": chat_id, "text": text}
    if parse_mode:
        payload["parse_mode"] = parse_mode
    return payload


def build_send_message_url(token: str) -> str:
    """Build Telegram sendMessage URL."""
    return f"https://api.telegram.org/bot{token}/sendMessage"


def read_text_file(path: str | Path) -> str:
    """Read UTF-8 text content from a file path."""
    file_path = Path(path)
    try:
        return file_path.read_text(encoding="utf-8")
    except FileNotFoundError as exc:
        raise TelegramFileError(f"File not found: {file_path}") from exc
    except OSError as exc:
        raise TelegramFileError(f"Unable to read file: {file_path}") from exc


def post_json(url: str, payload: dict[str, str], timeout: int = 30) -> dict[str, Any]:
    """POST JSON payload and validate Telegram API response."""
    try:
        response = requests.post(url, json=payload, timeout=timeout)
    except requests.RequestException as exc:
        raise TelegramRequestError(f"Telegram request failed: {exc}") from exc

    try:
        response_data: dict[str, Any] = response.json()
    except ValueError as exc:
        raise TelegramRequestError(
            f"Telegram returned non-JSON response (status={response.status_code})"
        ) from exc

    if not response.ok or response_data.get("ok") is False:
        description = response_data.get("description") or "Unknown Telegram API error"
        raise TelegramRequestError(
            f"Telegram API request failed (status={response.status_code}): {description}"
        )

    return response_data
