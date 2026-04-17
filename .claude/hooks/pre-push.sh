#!/bin/bash

cd "$CLAUDE_PROJECT_DIR"

source ~/.local/bin/env

if [ ! -d ".venv" ]; then
  uv venv
  uv pip install -r requirements-dev.txt
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
