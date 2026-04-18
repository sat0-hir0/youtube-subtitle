#!/bin/bash

cd "$CLAUDE_PROJECT_DIR"

source ~/.local/bin/env

echo "=== ruff format ==="
if ! ruff format --quiet .; then
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
if ! ruff check --quiet .; then
  jq -n '{
    "hookSpecificOutput": {
      "hookEventName": "PreToolUse",
      "permissionDecision": "deny",
      "permissionDecisionReason": "ruff check に失敗しました。lintエラーを修正してください。"
    }
  }'
  exit 0
fi

echo "=== format/lint チェックが通りました ==="
exit 0
