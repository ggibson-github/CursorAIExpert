#!/bin/bash
# stop hook. Merges pending agent notes and refreshes the trigger index.
# Stdout is always JSON and never a follow-up, so this cannot loop the agent.
INPUT="$(cat 2>/dev/null || true)"

run_py() {
  if command -v py >/dev/null 2>&1; then
    py -3 "$@"
  elif command -v python >/dev/null 2>&1; then
    python "$@"
  elif command -v python3 >/dev/null 2>&1; then
    python3 "$@"
  else
    return 1
  fi
}

skip_merge=0
if skip_merge="$(printf '%s' "$INPUT" | run_py -c 'import json,sys
raw=sys.stdin.read().strip()
try:
    data=json.loads(raw) if raw else {}
except Exception:
    data={}
if not isinstance(data, dict):
    data={}
active=str(data.get("stop_hook_active", False)).lower() in {"true", "1"}
try:
    loop=int(data.get("loop_count") or 0)
except (TypeError, ValueError):
    loop=0
print("1" if active or loop else "0")
')"; then
  :
else
  skip_merge=0
fi
if [ "$skip_merge" = "1" ]; then
  printf '%s\n' '{}'
  exit 0
fi

bash "$(dirname "$0")/merge-agent-notes.sh" >&2 || true

WORKSPACE_ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
GEN="$WORKSPACE_ROOT/scripts/memory/build_trigger_index.py"
IDX="$WORKSPACE_ROOT/facts/trigger-index.json"
if [ -f "$GEN" ]; then
  stale=0
  if [ ! -f "$IDX" ]; then
    stale=1
  else
    for rf in "$WORKSPACE_ROOT"/facts/rules-developer.md \
      "$WORKSPACE_ROOT"/facts/rules-incident-response.md \
      "$WORKSPACE_ROOT"/facts/rules-operations.md; do
      [ -f "$rf" ] && [ "$rf" -nt "$IDX" ] && stale=1 && break
    done
  fi
  if [ "$stale" -eq 1 ]; then
    run_py "$GEN" >/dev/null 2>&1 || true
  fi
fi
printf '%s\n' '{}'
exit 0
