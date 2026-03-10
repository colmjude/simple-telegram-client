from telegram_client import TelegramClient


def test_client_stores_config_path() -> None:
    client = TelegramClient("config.json")
    assert client.config_path.name == "config.json"
