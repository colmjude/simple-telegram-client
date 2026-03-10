"""Custom exceptions for simple-telegram-client."""


class TelegramClientError(Exception):
    """Base error for all client exceptions."""


class TelegramConfigError(TelegramClientError):
    """Raised when configuration is missing or invalid."""


class TelegramRequestError(TelegramClientError):
    """Raised when Telegram API calls fail."""


class TelegramFileError(TelegramClientError):
    """Raised when file reading/sending fails."""
