from pathlib import Path

from telegram_client import TelegramClient


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


def test_send_message_sends_chunked_payloads(monkeypatch, tmp_path) -> None:
    config_file = tmp_path / "config.json"
    config_file.write_text(
        '{"telegram": {"token": "token-1", "chat_id": "chat-1"}}',
        encoding="utf-8",
    )
    sent_payloads: list[dict[str, str]] = []

    def fake_post_json(url: str, payload: dict[str, str]) -> dict[str, bool]:
        sent_payloads.append(payload)
        return {"ok": True}

    monkeypatch.setattr("telegram_client.client.post_json", fake_post_json)
    client = TelegramClient(config_file)

    client.send_message("abcdefghij", parse_mode="Markdown")

    assert len(sent_payloads) == 1
    assert sent_payloads[0]["chat_id"] == "chat-1"
    assert sent_payloads[0]["text"] == "abcdefghij"
    assert sent_payloads[0]["parse_mode"] == "Markdown"


def test_send_markdown_file_reads_and_sends_content(monkeypatch, tmp_path) -> None:
    config_file = tmp_path / "config.json"
    config_file.write_text(
        '{"telegram": {"token": "token-1", "chat_id": "chat-1"}}',
        encoding="utf-8",
    )
    markdown_file = tmp_path / "report.md"
    markdown_file.write_text("# Report", encoding="utf-8")
    sent_payloads: list[dict[str, str]] = []

    def fake_post_json(url: str, payload: dict[str, str]) -> dict[str, bool]:
        sent_payloads.append(payload)
        return {"ok": True}

    monkeypatch.setattr("telegram_client.client.post_json", fake_post_json)
    client = TelegramClient(config_file)

    client.send_markdown_file(markdown_file)

    assert len(sent_payloads) == 1
    assert sent_payloads[0]["text"] == "# Report"


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
    sent_payloads: list[dict[str, str]] = []

    def fake_post_json(url: str, payload: dict[str, str]) -> dict[str, bool]:
        sent_payloads.append(payload)
        return {"ok": True}

    monkeypatch.setattr("telegram_client.client.post_json", fake_post_json)
    client = TelegramClient(config_file)

    client.send_message("hello")

    assert sent_payloads[0]["parse_mode"] == "MarkdownV2"
