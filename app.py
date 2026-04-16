import os
import re
import tempfile
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
import yt_dlp

app = FastAPI()


class SubtitleRequest(BaseModel):
    url: str
    translate: bool = True


def parse_vtt(content: str) -> list[str]:
    """VTTファイルをパースしてテキストのリストを返す。
    YouTube自動字幕は「前行 + 新行」の2行セットになっているため、
    各cueの最後の行だけを取ることで重複を防ぐ。
    """
    texts = []
    lines = content.splitlines()
    i = 0
    while i < len(lines):
        if "-->" in lines[i]:
            m = re.match(
                r"\d{2}:\d{2}:\d{2}\.\d{3}\s*-->\s*\d{2}:\d{2}:\d{2}\.\d{3}",
                lines[i],
            )
            if m:
                i += 1
                text_parts = []
                while i < len(lines) and lines[i].strip() and "-->" not in lines[i]:
                    cleaned = re.sub(r"<[^>]+>", "", lines[i]).strip()
                    if cleaned:
                        text_parts.append(cleaned)
                    i += 1
                if text_parts:
                    # 複数行の場合は最後の行だけが新しい内容
                    texts.append(text_parts[-1])
                continue
        i += 1
    return texts


def deduplicate(texts: list[str]) -> list[str]:
    """連続する重複テキストを除去する"""
    result = []
    prev = None
    for t in texts:
        if t != prev:
            result.append(t)
            prev = t
    return result


def format_as_text(texts: list[str]) -> str:
    """字幕断片を自然な文章に整形する。
    全断片を結合し、文末（。！？.!?）で改行を入れる。
    """
    joined = "".join(texts)
    # 文末記号の後に改行を入れる
    formatted = re.sub(r'([。！？!?])', r'\1\n', joined)
    # 連続する改行を1つにまとめる
    formatted = re.sub(r'\n+', '\n', formatted).strip()
    return formatted


def download_subtitles(url: str, tmpdir: str) -> tuple[Path | None, str, str]:
    """字幕をダウンロードし (ファイルパス, 言語, タイトル) を返す"""
    title = "Unknown"
    for lang in ["ja", "en"]:
        opts = {
            "writesubtitles": True,
            "writeautomaticsub": True,
            "subtitleslangs": [lang],
            "subtitlesformat": "vtt",
            "skip_download": True,
            "outtmpl": os.path.join(tmpdir, "%(title)s.%(ext)s"),
            "quiet": True,
            "no_warnings": True,
        }
        try:
            with yt_dlp.YoutubeDL(opts) as ydl:
                info = ydl.extract_info(url, download=True)
                title = info.get("title", "Unknown")
            for f in Path(tmpdir).glob("*.vtt"):
                return f, lang, title
        except Exception:
            continue
    return None, "", title


@app.post("/api/subtitles")
async def get_subtitles(request: SubtitleRequest):
    with tempfile.TemporaryDirectory() as tmpdir:
        sub_file, lang, title = download_subtitles(request.url, tmpdir)

        if sub_file is None:
            raise HTTPException(status_code=404, detail="字幕が見つかりませんでした。この動画には字幕がない可能性があります。")

        content = sub_file.read_text(encoding="utf-8")
        texts = deduplicate(parse_vtt(content))

        translated_texts: list[str] = []
        translated = False
        if lang == "en" and request.translate and texts:
            try:
                from deep_translator import GoogleTranslator

                translator = GoogleTranslator(source="en", target="ja")
                batch_size = 30
                for i in range(0, len(texts), batch_size):
                    batch = texts[i : i + batch_size]
                    translated_texts.extend(translator.translate_batch(batch))
                translated = True
            except Exception:
                # 翻訳に失敗しても字幕は返す
                translated_texts = []

        return {
            "title": title,
            "lang": lang,
            "translated": translated,
            "texts": texts,
            "translated_texts": translated_texts,
            "formatted": format_as_text(translated_texts if translated and translated_texts else texts),
        }


app.mount("/", StaticFiles(directory="static", html=True), name="static")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app:app", host="127.0.0.1", port=8000, reload=True)
