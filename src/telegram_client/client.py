"""Telegram client public interface."""

from __future__ import annotations

from pathlib import Path

from .config import load_telegram_config
from .utils import (
    build_send_message_payload,
    build_send_message_url,
    chunk_text,
    post_json,
    read_text_file,
)


class TelegramClient:
    """Client for sending outbound Telegram messages."""

    def __init__(self, config_path: str | Path = "config.json") -> None:
        self.config_path = Path(config_path)
        telegram_config = load_telegram_config(self.config_path)
        self.token = telegram_config["token"]
        self.chat_id = telegram_config["chat_id"]
        self.parse_mode = telegram_config.get("parse_mode")
        self._send_message_url = build_send_message_url(self.token)

    def send_message(self, text: str, parse_mode: str | None = None) -> None:
        effective_parse_mode = self.parse_mode if parse_mode is None else parse_mode
        message_chunks = chunk_text(text)

        for message_chunk in message_chunks:
            payload = build_send_message_payload(
                chat_id=self.chat_id,
                text=message_chunk,
                parse_mode=effective_parse_mode,
            )
            post_json(self._send_message_url, payload)

    def send_markdown_file(self, path: str | Path, parse_mode: str | None = None) -> None:
        markdown_content = read_text_file(path)
        self.send_message(markdown_content, parse_mode=parse_mode)
