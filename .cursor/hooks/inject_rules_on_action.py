"""preToolUse hook. Inject expert rules that match the action about to run.

Reads facts/trigger-index.json and writes Cursor hook JSON:
{"continue": true, "additional_context": "..."} when a rule matches.
Always exits 0. Also emits hookSpecificOutput.additionalContext.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

WRITE_TOOLS = {"Write", "StrReplace", "Edit", "MultiEdit", "EditNotebook"}
SHELL_TOOLS = {"Shell", "Bash"}


def _tool_input(payload: dict) -> dict:
    raw = payload.get("tool_input")
    if isinstance(raw, dict):
        return raw
    if isinstance(raw, str) and raw.strip():
        try:
            parsed = json.loads(raw)
        except json.JSONDecodeError:
            return {"command": raw}
        if isinstance(parsed, dict):
            return parsed
    return {}


def _file_path(payload: dict, tool_input: dict) -> str:
    for source in (tool_input, payload):
        for key in ("file_path", "path", "target_file"):
            value = source.get(key)
            if isinstance(value, str) and value.strip():
                return value.replace("\\", "/")
    return ""


def _add(tokens: list[str], seen: set[str], *names: str) -> None:
    for name in names:
        if name not in seen:
            seen.add(name)
            tokens.append(name)


def classify(tool_name: str, file_path: str, command: str) -> list[str]:
    tokens: list[str] = []
    seen: set[str] = set()
    path = file_path.lower()
    if tool_name in WRITE_TOOLS:
        if path.endswith(".sql"):
            _add(tokens, seen, "write:sql", "sql:generate")
        if path.endswith(".html"):
            _add(tokens, seen, "write:doc")
        if "/outputs/" in path or "walkthrough" in path:
            _add(tokens, seen, "write:customer-html")
        if path.endswith(".md") or path.endswith(".markdown"):
            _add(tokens, seen, "write:doc")
    elif tool_name in SHELL_TOOLS:
        if "gh pr create" in command:
            _add(tokens, seen, "pr:open")
        if "git push" in command:
            _add(tokens, seen, "git:push")
        if "git commit" in command:
            _add(tokens, seen, "git:commit")
        if "config" in command:
            _add(tokens, seen, "config:change")
    return tokens


def matching_rules(index: dict, tokens: list[str]) -> list[dict]:
    found: list[dict] = []
    seen: set[str] = set()
    for token in tokens:
        entries = index.get(token)
        if not isinstance(entries, list):
            continue
        for entry in entries:
            if not isinstance(entry, dict):
                continue
            key = f"{entry.get('file')}|{entry.get('line')}"
            if key in seen:
                continue
            body = entry.get("body")
            if not isinstance(body, str) or not body.strip():
                continue
            seen.add(key)
            found.append(entry)
    return found


def context_text(tokens: list[str], rules: list[dict]) -> str:
    if not rules:
        return ""
    bodies = "\n\n".join("---\n" + str(rule.get("body") or "") for rule in rules)
    joined = ", ".join(tokens)
    return (
        "Expert rules for the action you are about to take "
        f"(matched triggers: {joined}). "
        "These apply regardless of the current workflow:\n\n"
        f"{bodies}"
    )


def emit(text: str) -> None:
    payload: dict = {"continue": True}
    if text:
        payload["additional_context"] = text
        payload["hookSpecificOutput"] = {
            "hookEventName": "PreToolUse",
            "additionalContext": text,
        }
    json.dump(payload, sys.stdout)
    sys.stdout.write("\n")


def main() -> int:
    raw = sys.stdin.read()
    try:
        payload = json.loads(raw) if raw.strip() else {}
    except json.JSONDecodeError:
        payload = {}
    if not isinstance(payload, dict):
        payload = {}
    index_path = Path.cwd() / "facts" / "trigger-index.json"
    if not index_path.is_file():
        emit("")
        return 0
    try:
        index = json.loads(index_path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError):
        emit("")
        return 0
    if not isinstance(index, dict):
        emit("")
        return 0
    tool_input = _tool_input(payload)
    tokens = classify(
        str(payload.get("tool_name") or ""),
        _file_path(payload, tool_input),
        str(tool_input.get("command") or ""),
    )
    emit(context_text(tokens, matching_rules(index, tokens)))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
