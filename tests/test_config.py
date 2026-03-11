import json

import pytest

from telegram_client import config as config_module
from telegram_client import exceptions as exc


def test_load_telegram_config_returns_validated_config(tmp_path) -> None:
    config_file = tmp_path / "config.json"
    config_file.write_text(
        json.dumps(
            {
                "telegram": {
                    "token": "token-1",
                    "chat_id": "chat-1",
                    "parse_mode": "Markdown",
                }
            }
        ),
        encoding="utf-8",
    )

    config = config_module.load_telegram_config(config_file)

    assert config["token"] == "token-1"
    assert config["chat_id"] == "chat-1"
    assert config["parse_mode"] == "Markdown"


def test_load_telegram_config_allows_token_only(tmp_path) -> None:
    config_file = tmp_path / "config.json"
    config_file.write_text(
        json.dumps({"telegram": {"token": "token-1"}}),
        encoding="utf-8",
    )

    config = config_module.load_telegram_config(config_file)

    assert config["token"] == "token-1"
    assert "chat_id" not in config


def test_load_telegram_config_raises_for_missing_file(tmp_path) -> None:
    missing_path = tmp_path / "missing.json"

    with pytest.raises(exc.TelegramConfigError, match="Config file not found"):
        config_module.load_telegram_config(missing_path)


def test_load_telegram_config_raises_for_invalid_json(tmp_path) -> None:
    config_file = tmp_path / "config.json"
    config_file.write_text("{invalid json", encoding="utf-8")

    with pytest.raises(exc.TelegramConfigError, match="Invalid JSON"):
        config_module.load_telegram_config(config_file)


def test_load_telegram_config_raises_for_missing_telegram_block(tmp_path) -> None:
    config_file = tmp_path / "config.json"
    config_file.write_text(json.dumps({"not_telegram": {}}), encoding="utf-8")

    with pytest.raises(exc.TelegramConfigError, match="top-level 'telegram'"):
        config_module.load_telegram_config(config_file)


def test_load_telegram_config_raises_for_missing_required_keys(tmp_path) -> None:
    config_file = tmp_path / "config.json"
    config_file.write_text(
        json.dumps({"telegram": {"chat_id": "chat-1"}}),
        encoding="utf-8",
    )

    with pytest.raises(exc.TelegramConfigError, match="telegram.token"):
        config_module.load_telegram_config(config_file)


def test_load_telegram_config_raises_for_invalid_chat_id_type(tmp_path) -> None:
    config_file = tmp_path / "config.json"
    config_file.write_text(
        json.dumps({"telegram": {"token": "token-1", "chat_id": 123}}),
        encoding="utf-8",
    )

    with pytest.raises(exc.TelegramConfigError, match="telegram.chat_id"):
        config_module.load_telegram_config(config_file)


def test_load_telegram_config_raises_for_invalid_parse_mode_type(tmp_path) -> None:
    config_file = tmp_path / "config.json"
    config_file.write_text(
        json.dumps(
            {
                "telegram": {
                    "token": "token-1",
                    "chat_id": "chat-1",
                    "parse_mode": 123,
                }
            }
        ),
        encoding="utf-8",
    )

    with pytest.raises(exc.TelegramConfigError, match="telegram.parse_mode"):
        config_module.load_telegram_config(config_file)
