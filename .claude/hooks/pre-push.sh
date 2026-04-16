#!/bin/bash

# git push コマンドの場合のみ実行
COMMAND=$(jq -r '.tool_input.command // empty' < /dev/stdin)

if ! echo "$COMMAND" | grep -q "git push"; then
  exit 0
fi

PROJECT_DIR="$CLAUDE_PROJECT_DIR"
cd "$PROJECT_DIR"

source ~/.local/bin/env

# 仮想環境がなければ作成
if [ ! -d ".venv" ]; then
  uv venv
  uv pip install -r requirements.txt
fi

echo "=== ruff format ==="
if ! ruff format .; then
  jq -n '{
    "hookSpecificOutput": {
      "hookEventName": "PreToolUse",
      "permissionDecision": "deny",
      "permissionDecisionReason": "ruff format に失敗しました。コードを確認してください。"
    }
  }'
  exit 0
fi

echo "=== ruff check ==="
if ! ruff check .; then
  jq -n '{
    "hookSpecificOutput": {
      "hookEventName": "PreToolUse",
      "permissionDecision": "deny",
      "permissionDecisionReason": "ruff check に失敗しました。lintエラーを修正してください。"
    }
  }'
  exit 0
fi

echo "=== pytest ==="
if ! .venv/bin/pytest; then
  jq -n '{
    "hookSpecificOutput": {
      "hookEventName": "PreToolUse",
      "permissionDecision": "deny",
      "permissionDecisionReason": "テストが失敗しました。テストを修正してください。"
    }
  }'
  exit 0
fi

echo "=== すべてのチェックが通りました ==="
exit 0
