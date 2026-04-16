# YouTube字幕ダウンローダー

## プロジェクト概要
YouTubeの動画から字幕を取得してテキストとして表示・ダウンロードするローカルWebアプリ。

## 技術スタック
- Python 3.12 / FastAPI
- yt-dlp（字幕取得）
- deep-translator（Google Translate経由の翻訳）
- HTML / CSS / JavaScript（vanilla）
- Docker

## テスト駆動開発
必ずRed → Green → Refactorのサイクルで開発すること。
1. **Red**: 失敗するテストを先に書く
2. **Green**: テストが通る最小限のコードを書く
3. **Refactor**: コードをきれいにする

## ブランチ
開発を開始するときは必ずmainから新しいブランチを切ること。
```bash
git checkout main && git pull && git checkout -b feature/作業名
```

## 個人設定
@.claude/local/CLAUDE.md
