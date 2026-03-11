"""Telegram client public interface."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from .config import load_telegram_config
from .exceptions import TelegramConfigError
from .utils import (
    build_get_updates_payload,
    build_get_updates_url,
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
        self.chat_id = telegram_config.get("chat_id")
        self.parse_mode = telegram_config.get("parse_mode")
        self._send_message_url = build_send_message_url(self.token)
        self._get_updates_url = build_get_updates_url(self.token)

    def _resolve_chat_id(self, chat_id: str | int | None = None) -> str:
        if chat_id is not None:
            return str(chat_id)
        if self.chat_id:
            return self.chat_id
        raise TelegramConfigError(
            "No chat ID available. Provide chat_id per call or set "
            "'telegram.chat_id' in config."
        )

    def send_message(
        self,
        text: str,
        parse_mode: str | None = None,
        chat_id: str | int | None = None,
    ) -> dict[str, Any] | list[dict[str, Any]]:
        effective_parse_mode = self.parse_mode if parse_mode is None else parse_mode
        effective_chat_id = self._resolve_chat_id(chat_id=chat_id)
        message_chunks = chunk_text(text)
        responses: list[dict[str, Any]] = []

        for message_chunk in message_chunks:
            payload = build_send_message_payload(
                chat_id=effective_chat_id,
                text=message_chunk,
                parse_mode=effective_parse_mode,
            )
            responses.append(post_json(self._send_message_url, payload))

        if len(responses) == 1:
            return responses[0]
        return responses

    def send_markdown_file(
        self,
        path: str | Path,
        parse_mode: str | None = None,
        chat_id: str | int | None = None,
    ) -> dict[str, Any] | list[dict[str, Any]]:
        markdown_content = read_text_file(path)
        return self.send_message(
            markdown_content,
            parse_mode=parse_mode,
            chat_id=chat_id,
        )

    def get_updates(
        self,
        offset: int | None = None,
        timeout: int = 30,
        allowed_updates: list[str] | None = None,
    ) -> dict[str, Any]:
        payload = build_get_updates_payload(
            offset=offset,
            timeout=timeout,
            allowed_updates=allowed_updates,
        )
        return post_json(self._get_updates_url, payload, timeout=timeout)
