# YouTube字幕ダウンローダー

YouTubeの動画から字幕を取得してテキストとして表示・ダウンロードできるローカルWebアプリです。

## 機能

- YouTube URLを貼り付けるだけで字幕を取得
- 日本語字幕を優先取得（なければ英語字幕を取得）
- 英語字幕は日本語に翻訳（オプション）
- 字幕を自然な文章に整形（タイムスタンプなし）
- テキストのコピー / TXTダウンロード

## 必要な環境

- Docker

## セットアップ

```bash
git clone git@github.com:sat0-hir0/youtube-subtitle.git
cd youtube-subtitle
```

## 起動

```bash
docker compose up -d
```

ブラウザで http://localhost:8000 を開く。

## 停止

```bash
docker compose down
```

## 技術スタック

| 用途 | 技術 |
|------|------|
| バックエンド | Python / FastAPI |
| 字幕取得 | yt-dlp |
| 翻訳 | deep-translator (Google Translate) |
| フロントエンド | HTML / CSS / JavaScript (vanilla) |
| 実行環境 | Docker |
