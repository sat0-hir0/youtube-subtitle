from unittest.mock import MagicMock, patch

from app import deduplicate, format_as_text, parse_vtt


def test_deduplicate_removes_consecutive_duplicates():
    texts = ["hello", "hello", "world", "world", "world", "foo"]
    assert deduplicate(texts) == ["hello", "world", "foo"]


def test_deduplicate_keeps_non_consecutive_duplicates():
    texts = ["hello", "world", "hello"]
    assert deduplicate(texts) == ["hello", "world", "hello"]


def test_format_as_text_adds_newline_after_punctuation():
    texts = ["こんにちは。", "今日はいい天気ですね。"]
    result = format_as_text(texts)
    assert result == "こんにちは。\n今日はいい天気ですね。"


def test_format_as_text_joins_fragments():
    texts = ["こんに", "ちは。", "今日は。"]
    result = format_as_text(texts)
    assert result == "こんにちは。\n今日は。"


def test_format_as_text_empty_list():
    assert format_as_text([]) == ""


def test_format_as_text_no_punctuation():
    assert format_as_text(["hello", "world"]) == "helloworld"


def test_format_as_text_english_punctuation():
    texts = ["Hello.", "How are you?", "I am fine!"]
    assert format_as_text(texts) == "Hello.\nHow are you?\nI am fine!"


def test_parse_vtt_empty():
    content = "WEBVTT\n\n"
    assert parse_vtt(content) == []


def test_parse_vtt_single_cue():
    content = "WEBVTT\n\n00:00:00.000 --> 00:00:02.000\nこんにちは\n"
    assert parse_vtt(content) == ["こんにちは"]


def test_parse_vtt_multiple_cues():
    content = (
        "WEBVTT\n\n"
        "00:00:00.000 --> 00:00:02.000\nこんにちは\n\n"
        "00:00:02.000 --> 00:00:04.000\n世界\n"
    )
    assert parse_vtt(content) == ["こんにちは", "世界"]


def test_parse_vtt_strips_html_tags():
    content = (
        "WEBVTT\n\n00:00:00.000 --> 00:00:02.000\n<v Speaker>こんにちは<c.colorFFFFFF> 世界</c>\n"
    )
    assert parse_vtt(content) == ["こんにちは 世界"]


def test_parse_vtt_youtube_duplicate_pattern():
    # YouTube自動字幕は「前行 + 新行」の2行セット → 最後の行だけ抽出
    content = (
        "WEBVTT\n\n"
        "00:00:00.000 --> 00:00:02.000\n"
        "こんにちは\n\n"
        "00:00:01.500 --> 00:00:03.500\n"
        "こんにちは\n"
        "今日は\n"
    )
    assert parse_vtt(content) == ["こんにちは", "今日は"]


def test_health(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_get_subtitles_not_found(client):
    with patch("app.download_subtitles", return_value=(None, "", "Unknown", "Unknown")):
        response = client.post(
            "/api/subtitles",
            json={"url": "https://www.youtube.com/watch?v=dummy", "translate": False},
        )
    assert response.status_code == 404
    assert "字幕が見つかりません" in response.json()["detail"]


def test_get_subtitles_japanese(tmp_path, client):
    vtt_file = tmp_path / "video.ja.vtt"
    vtt_file.write_text("WEBVTT\n\n00:00:00.000 --> 00:00:02.000\nこんにちは\n", encoding="utf-8")
    with patch(
        "app.download_subtitles",
        return_value=(vtt_file, "ja", "テスト動画", "テストチャンネル"),
    ):
        response = client.post(
            "/api/subtitles",
            json={"url": "https://www.youtube.com/watch?v=dummy", "translate": False},
        )
    assert response.status_code == 200
    body = response.json()
    assert body["title"] == "テスト動画"
    assert body["channel"] == "テストチャンネル"
    assert body["url"] == "https://www.youtube.com/watch?v=dummy"
    assert body["lang"] == "ja"
    assert body["translated"] is False
    assert body["texts"] == ["こんにちは"]
    assert body["translated_texts"] == []
    assert "こんにちは" in body["formatted"]


def test_get_subtitles_english_translated(tmp_path, client):
    vtt_file = tmp_path / "video.en.vtt"
    vtt_file.write_text("WEBVTT\n\n00:00:00.000 --> 00:00:02.000\nHello\n", encoding="utf-8")
    mock_translator = MagicMock()
    mock_translator.translate_batch.return_value = ["こんにちは"]
    with (
        patch(
            "app.download_subtitles", return_value=(vtt_file, "en", "Test Video", "Test Channel")
        ),
        patch("deep_translator.GoogleTranslator", return_value=mock_translator),
    ):
        response = client.post(
            "/api/subtitles",
            json={"url": "https://www.youtube.com/watch?v=dummy", "translate": True},
        )
    assert response.status_code == 200
    body = response.json()
    assert body["url"] == "https://www.youtube.com/watch?v=dummy"
    assert body["channel"] == "Test Channel"
    assert body["lang"] == "en"
    assert body["translated"] is True
    assert body["texts"] == ["Hello"]
    assert body["translated_texts"] == ["こんにちは"]
    assert "こんにちは" in body["formatted"]
