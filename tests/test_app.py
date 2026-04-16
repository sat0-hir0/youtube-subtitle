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


def test_parse_vtt_empty():
    content = "WEBVTT\n\n"
    assert parse_vtt(content) == []
