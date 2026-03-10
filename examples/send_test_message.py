"""Send a Telegram message using local config.

Usage:
    PYTHONPATH=src python examples/send_test_message.py --config config.json --text "hello"
"""

from __future__ import annotations

import argparse

from telegram_client import TelegramClient


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Send a Telegram test message")
    parser.add_argument(
        "--config",
        default="config.json",
        help="Path to JSON config file (default: config.json)",
    )
    parser.add_argument(
        "--text",
        default="Hello from simple-telegram-client",
        help="Message text to send",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    client = TelegramClient(config_path=args.config)
    client.send_message(args.text)
    print("Message sent")


if __name__ == "__main__":
    main()
