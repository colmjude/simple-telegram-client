import pytest
import requests

from telegram_client import exceptions as exc
from telegram_client import utils


def test_chunk_text_returns_single_chunk_when_short() -> None:
    chunks = utils.chunk_text("hello", max_length=10)
    assert chunks == ["hello"]


def test_chunk_text_splits_long_text_strictly_by_length() -> None:
    text = "a" * (utils.TELEGRAM_MAX_MESSAGE_LENGTH + 10)
    chunks = utils.chunk_text(text)
    assert len(chunks) == 2
    assert len(chunks[0]) == utils.TELEGRAM_MAX_MESSAGE_LENGTH
    assert len(chunks[1]) == 10


def test_chunk_text_raises_for_invalid_max_length() -> None:
    with pytest.raises(ValueError, match="greater than 0"):
        utils.chunk_text("hello", max_length=0)


def test_build_send_message_payload_omits_parse_mode_when_none() -> None:
    payload = utils.build_send_message_payload(chat_id="123", text="hello")
    assert payload == {"chat_id": "123", "text": "hello"}


def test_build_send_message_payload_includes_parse_mode() -> None:
    payload = utils.build_send_message_payload(
        chat_id="123",
        text="hello",
        parse_mode="Markdown",
    )
    assert payload["parse_mode"] == "Markdown"


def test_build_send_message_url() -> None:
    assert (
        utils.build_send_message_url("abc")
        == "https://api.telegram.org/botabc/sendMessage"
    )


def test_read_text_file_reads_content(tmp_path) -> None:
    file_path = tmp_path / "note.md"
    file_path.write_text("hello", encoding="utf-8")
    assert utils.read_text_file(file_path) == "hello"


def test_read_text_file_raises_for_missing_file(tmp_path) -> None:
    missing_path = tmp_path / "missing.md"
    with pytest.raises(exc.TelegramFileError, match="File not found"):
        utils.read_text_file(missing_path)


def test_post_json_returns_response_data_on_success(monkeypatch) -> None:
    class FakeResponse:
        status_code = 200
        ok = True

        @staticmethod
        def json():
            return {"ok": True, "result": {"message_id": 1}}

    def fake_post(url, json, timeout):  # noqa: A002
        return FakeResponse()

    monkeypatch.setattr("telegram_client.utils.requests.post", fake_post)

    result = utils.post_json("https://example.com", {"chat_id": "1", "text": "hello"})
    assert result["ok"] is True


def test_post_json_raises_for_non_json_response(monkeypatch) -> None:
    class FakeResponse:
        status_code = 500
        ok = False

        @staticmethod
        def json():
            raise ValueError("invalid json")

    def fake_post(url, json, timeout):  # noqa: A002
        return FakeResponse()

    monkeypatch.setattr("telegram_client.utils.requests.post", fake_post)

    with pytest.raises(exc.TelegramRequestError, match="non-JSON"):
        utils.post_json("https://example.com", {"chat_id": "1", "text": "hello"})


def test_post_json_raises_for_telegram_api_error(monkeypatch) -> None:
    class FakeResponse:
        status_code = 400
        ok = False

        @staticmethod
        def json():
            return {"ok": False, "description": "Bad Request: chat not found"}

    def fake_post(url, json, timeout):  # noqa: A002
        return FakeResponse()

    monkeypatch.setattr("telegram_client.utils.requests.post", fake_post)

    with pytest.raises(exc.TelegramRequestError, match="chat not found"):
        utils.post_json("https://example.com", {"chat_id": "1", "text": "hello"})


def test_post_json_raises_for_request_exception(monkeypatch) -> None:
    def fake_post(url, json, timeout):  # noqa: A002
        raise requests.RequestException("network boom")

    monkeypatch.setattr("telegram_client.utils.requests.post", fake_post)

    with pytest.raises(exc.TelegramRequestError, match="Telegram request failed"):
        utils.post_json("https://example.com", {"chat_id": "1", "text": "hello"})
