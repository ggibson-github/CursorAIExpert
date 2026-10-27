#!/bin/bash
# preToolUse wrapper. The loader is Python so it runs without jq.
cd "$(dirname "$0")/../.." || exit 0
if command -v py >/dev/null 2>&1; then
  exec py -3 .cursor/hooks/inject_journal_context.py
fi
if command -v python >/dev/null 2>&1; then
  exec python .cursor/hooks/inject_journal_context.py
fi
if command -v python3 >/dev/null 2>&1; then
  exec python3 .cursor/hooks/inject_journal_context.py
fi
printf '%s\n' '{"continue": true}'
exit 0
