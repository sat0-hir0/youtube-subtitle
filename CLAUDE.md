# YouTube字幕ダウンローダー

## プロジェクト概要
YouTubeの動画から字幕を取得してテキストとして表示・ダウンロードするローカルWebアプリ。

## 技術スタック
- Python 3.12 / FastAPI
- yt-dlp（字幕取得）
- deep-translator（Google Translate経由の翻訳）
- HTML / CSS / JavaScript（vanilla）
- Docker

## 起動方法
```bash
wsl -d Ubuntu -u claude -- bash -c "sudo service docker start && cd /mnt/c/Users/hiroki/code/youtube-subtitle && docker compose up -d"
```

## コードを変更した後
```bash
wsl -d Ubuntu -u claude -- bash -c "cd /mnt/c/Users/hiroki/code/youtube-subtitle && docker compose up -d --build"
```

## Gitルール
- commit と push は別々に実行する
- commit後は必ずgit statusでpush漏れを確認する

## 個人設定
@.claude/local/CLAUDE.md
