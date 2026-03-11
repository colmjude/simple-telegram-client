from pathlib import Path

import pytest

from telegram_client import TelegramClient
from telegram_client import exceptions as exc


def test_client_stores_loaded_config_fields(tmp_path) -> None:
    config_file = tmp_path / "config.json"
    config_file.write_text(
        (
            '{"telegram": {"token": "token-1", "chat_id": "chat-1", '
            '"parse_mode": "Markdown"}}'
        ),
        encoding="utf-8",
    )

    client = TelegramClient(config_file)

    assert client.config_path == Path(config_file)
    assert client.token == "token-1"
    assert client.chat_id == "chat-1"
    assert client.parse_mode == "Markdown"


def test_send_message_sends_payload(monkeypatch, tmp_path) -> None:
    config_file = tmp_path / "config.json"
    config_file.write_text(
        '{"telegram": {"token": "token-1", "chat_id": "chat-1"}}',
        encoding="utf-8",
    )
    sent_payloads: list[dict[str, object]] = []

    def fake_post_json(url: str, payload: dict[str, object]) -> dict[str, bool]:
        sent_payloads.append(payload)
        return {"ok": True}

    monkeypatch.setattr("telegram_client.client.post_json", fake_post_json)
    client = TelegramClient(config_file)

    result = client.send_message("abcdefghij", parse_mode="Markdown")

    assert result == {"ok": True}
    assert len(sent_payloads) == 1
    assert sent_payloads[0]["chat_id"] == "chat-1"
    assert sent_payloads[0]["text"] == "abcdefghij"
    assert sent_payloads[0]["parse_mode"] == "Markdown"


def test_send_message_posts_each_chunk(monkeypatch, tmp_path) -> None:
    config_file = tmp_path / "config.json"
    config_file.write_text(
        '{"telegram": {"token": "token-1", "chat_id": "chat-1"}}',
        encoding="utf-8",
    )
    sent_payloads: list[dict[str, object]] = []

    def fake_chunk_text(text: str) -> list[str]:
        return ["part-1", "part-2"]

    def fake_post_json(url: str, payload: dict[str, object]) -> dict[str, object]:
        sent_payloads.append(payload)
        return {"ok": True, "result": {"text": payload["text"]}}

    monkeypatch.setattr("telegram_client.client.chunk_text", fake_chunk_text)
    monkeypatch.setattr("telegram_client.client.post_json", fake_post_json)
    client = TelegramClient(config_file)

    result = client.send_message("ignored")

    assert result == [
        {"ok": True, "result": {"text": "part-1"}},
        {"ok": True, "result": {"text": "part-2"}},
    ]
    assert len(sent_payloads) == 2
    assert sent_payloads[0]["text"] == "part-1"
    assert sent_payloads[1]["text"] == "part-2"


def test_send_markdown_file_reads_and_sends_content(monkeypatch, tmp_path) -> None:
    config_file = tmp_path / "config.json"
    config_file.write_text(
        '{"telegram": {"token": "token-1", "chat_id": "chat-1"}}',
        encoding="utf-8",
    )
    markdown_file = tmp_path / "report.md"
    markdown_file.write_text("# Report", encoding="utf-8")
    sent_payloads: list[dict[str, object]] = []

    def fake_post_json(url: str, payload: dict[str, object]) -> dict[str, bool]:
        sent_payloads.append(payload)
        return {"ok": True}

    monkeypatch.setattr("telegram_client.client.post_json", fake_post_json)
    client = TelegramClient(config_file)

    result = client.send_markdown_file(markdown_file)

    assert result == {"ok": True}
    assert len(sent_payloads) == 1
    assert sent_payloads[0]["text"] == "# Report"


def test_send_markdown_file_raises_for_missing_file(tmp_path) -> None:
    config_file = tmp_path / "config.json"
    config_file.write_text(
        '{"telegram": {"token": "token-1", "chat_id": "chat-1"}}',
        encoding="utf-8",
    )
    client = TelegramClient(config_file)

    with pytest.raises(exc.TelegramFileError, match="File not found"):
        client.send_markdown_file(tmp_path / "missing.md")


def test_send_message_uses_config_parse_mode_when_no_override(
    monkeypatch, tmp_path
) -> None:
    config_file = tmp_path / "config.json"
    config_file.write_text(
        (
            '{"telegram": {"token": "token-1", "chat_id": "chat-1", '
            '"parse_mode": "MarkdownV2"}}'
        ),
        encoding="utf-8",
    )
    sent_payloads: list[dict[str, object]] = []

    def fake_post_json(url: str, payload: dict[str, object]) -> dict[str, bool]:
        sent_payloads.append(payload)
        return {"ok": True}

    monkeypatch.setattr("telegram_client.client.post_json", fake_post_json)
    client = TelegramClient(config_file)

    client.send_message("hello")

    assert sent_payloads[0]["parse_mode"] == "MarkdownV2"


def test_send_message_omits_parse_mode_when_not_configured(
    monkeypatch, tmp_path
) -> None:
    config_file = tmp_path / "config.json"
    config_file.write_text(
        '{"telegram": {"token": "token-1", "chat_id": "chat-1"}}',
        encoding="utf-8",
    )
    sent_payloads: list[dict[str, object]] = []

    def fake_post_json(url: str, payload: dict[str, object]) -> dict[str, bool]:
        sent_payloads.append(payload)
        return {"ok": True}

    monkeypatch.setattr("telegram_client.client.post_json", fake_post_json)
    client = TelegramClient(config_file)

    client.send_message("hello")

    assert "parse_mode" not in sent_payloads[0]


def test_send_message_uses_per_call_chat_id_override(monkeypatch, tmp_path) -> None:
    config_file = tmp_path / "config.json"
    config_file.write_text(
        '{"telegram": {"token": "token-1", "chat_id": "default-chat"}}',
        encoding="utf-8",
    )
    sent_payloads: list[dict[str, object]] = []

    def fake_post_json(url: str, payload: dict[str, object]) -> dict[str, bool]:
        sent_payloads.append(payload)
        return {"ok": True}

    monkeypatch.setattr("telegram_client.client.post_json", fake_post_json)
    client = TelegramClient(config_file)

    client.send_message("reply", chat_id=123456789)

    assert sent_payloads[0]["chat_id"] == "123456789"


def test_send_message_uses_per_call_chat_id_when_no_default(
    monkeypatch, tmp_path
) -> None:
    config_file = tmp_path / "config.json"
    config_file.write_text('{"telegram": {"token": "token-1"}}', encoding="utf-8")
    sent_payloads: list[dict[str, object]] = []

    def fake_post_json(url: str, payload: dict[str, object]) -> dict[str, bool]:
        sent_payloads.append(payload)
        return {"ok": True}

    monkeypatch.setattr("telegram_client.client.post_json", fake_post_json)
    client = TelegramClient(config_file)

    client.send_message("reply", chat_id="chat-dynamic")

    assert sent_payloads[0]["chat_id"] == "chat-dynamic"


def test_send_message_raises_when_no_default_or_per_call_chat_id(tmp_path) -> None:
    config_file = tmp_path / "config.json"
    config_file.write_text('{"telegram": {"token": "token-1"}}', encoding="utf-8")
    client = TelegramClient(config_file)

    with pytest.raises(exc.TelegramConfigError, match="No chat ID available"):
        client.send_message("reply")


def test_send_markdown_file_supports_chat_id_override(monkeypatch, tmp_path) -> None:
    config_file = tmp_path / "config.json"
    config_file.write_text('{"telegram": {"token": "token-1"}}', encoding="utf-8")
    markdown_file = tmp_path / "report.md"
    markdown_file.write_text("# Report", encoding="utf-8")
    sent_payloads: list[dict[str, object]] = []

    def fake_post_json(url: str, payload: dict[str, object]) -> dict[str, bool]:
        sent_payloads.append(payload)
        return {"ok": True}

    monkeypatch.setattr("telegram_client.client.post_json", fake_post_json)
    client = TelegramClient(config_file)

    client.send_markdown_file(markdown_file, chat_id="chat-override")

    assert sent_payloads[0]["chat_id"] == "chat-override"


def test_get_updates_posts_expected_payload(monkeypatch, tmp_path) -> None:
    config_file = tmp_path / "config.json"
    config_file.write_text('{"telegram": {"token": "token-1"}}', encoding="utf-8")
    captured: dict[str, object] = {}

    def fake_post_json(
        url: str, payload: dict[str, object], timeout: int = 30
    ) -> dict[str, object]:
        captured["url"] = url
        captured["payload"] = payload
        captured["timeout"] = timeout
        return {"ok": True, "result": []}

    monkeypatch.setattr("telegram_client.client.post_json", fake_post_json)
    client = TelegramClient(config_file)

    result = client.get_updates(
        offset=42,
        timeout=15,
        allowed_updates=["message", "callback_query"],
    )

    assert result == {"ok": True, "result": []}
    assert captured["url"] == "https://api.telegram.org/bottoken-1/getUpdates"
    assert captured["payload"] == {
        "offset": 42,
        "timeout": 15,
        "allowed_updates": ["message", "callback_query"],
    }
    assert captured["timeout"] == 15


def test_get_updates_propagates_request_error(monkeypatch, tmp_path) -> None:
    config_file = tmp_path / "config.json"
    config_file.write_text('{"telegram": {"token": "token-1"}}', encoding="utf-8")

    def fake_post_json(
        url: str, payload: dict[str, object], timeout: int = 30
    ) -> dict[str, object]:
        raise exc.TelegramRequestError("boom")

    monkeypatch.setattr("telegram_client.client.post_json", fake_post_json)
    client = TelegramClient(config_file)

    with pytest.raises(exc.TelegramRequestError, match="boom"):
        client.get_updates()
