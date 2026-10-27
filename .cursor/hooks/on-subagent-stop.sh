#!/bin/bash
# subagentStop hook. Merges notes that are ready, then returns empty JSON
# so Cursor does not schedule a follow-up for the subagent.
cat >/dev/null 2>&1
bash "$(dirname "$0")/merge-agent-notes.sh" >&2 || true
printf '%s\n' '{}'
exit 0
