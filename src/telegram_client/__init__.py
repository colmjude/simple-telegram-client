"""simple-telegram-client package."""

__all__ = [
    "TelegramClient",
    "TelegramClientError",
    "TelegramConfigError",
    "TelegramRequestError",
    "TelegramFileError",
]

from .client import TelegramClient
from .exceptions import (
    TelegramClientError,
    TelegramConfigError,
    TelegramFileError,
    TelegramRequestError,
)
