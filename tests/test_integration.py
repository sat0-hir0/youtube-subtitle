"""結合テスト: 実際にyt-dlpでYouTubeから字幕を取得する。

実行方法:
    pytest -m integration -v

通常のテスト実行では自動的にスキップされる。
"""

import pytest

from app import deduplicate, download_subtitles, parse_vtt

# yt-dlpのドキュメントで使われている安定した動画（英語字幕あり）
YOUTUBE_URL_EN = "https://www.youtube.com/watch?v=PRU2ShMzQRg"


@pytest.mark.integration
def test_download_subtitles_returns_file(tmp_path):
    sub_file, lang, title = download_subtitles(YOUTUBE_URL_EN, str(tmp_path))

    assert sub_file is not None, "字幕ファイルが取得できなかった"
    assert sub_file.exists()
    assert lang in ("en", "ja")
    assert title != "Unknown"


@pytest.mark.integration
def test_download_subtitles_content_is_parseable(tmp_path):
    sub_file, lang, title = download_subtitles(YOUTUBE_URL_EN, str(tmp_path))

    assert sub_file is not None
    content = sub_file.read_text(encoding="utf-8")
    texts = deduplicate(parse_vtt(content))

    assert len(texts) > 0, "字幕テキストが1件も取得できなかった"
    # 英語字幕なので英字が含まれるはず
    joined = "".join(texts)
    assert any(c.isalpha() for c in joined)
