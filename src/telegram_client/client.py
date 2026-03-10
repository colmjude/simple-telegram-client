"""Telegram client public interface (Milestone 1 scaffold)."""

from __future__ import annotations

from pathlib import Path


class TelegramClient:
    """Placeholder client implementation for Milestone 1 scaffolding."""

    def __init__(self, config_path: str | Path = "config.json") -> None:
        self.config_path = Path(config_path)

    def send_message(self, text: str, parse_mode: str | None = None) -> None:
        raise NotImplementedError("Implemented in Milestone 2")

    def send_markdown_file(self, path: str | Path, parse_mode: str | None = None) -> None:
        raise NotImplementedError("Implemented in Milestone 2")
