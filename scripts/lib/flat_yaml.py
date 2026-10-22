"""Minimal parser for the flat metadata format (see templates/metadata.yml).

One `key: value` per line; values may be quoted strings, numbers, null, or
JSON-style inline arrays. Comments and indented lines are ignored.
"""

from __future__ import annotations

import json
import re

# `.` must not match line terminators, so a key line ending in "\r" is skipped
# the same way everywhere.
_LINE = re.compile(r"([A-Za-z_][A-Za-z0-9_]*):\s*([^\r\n  ]*)")
_NUMBER = re.compile(r"-?[0-9]+(?:\.[0-9]+)?")
_COMMENT = re.compile(r"\s+#[^\r\n  ]*$")
_FRONT_MATTER = re.compile(r"^---\r?\n([\s\S]*?)\r?\n---")


def parse_flat_yaml(text: str) -> dict:
    out: dict = {}
    for line in text.split("\n"):
        m = _LINE.fullmatch(line)
        if m:
            out[m.group(1)] = _parse_value(m.group(2))
    return out


def _parse_value(value: str):
    raw = value.strip()
    if raw.startswith('"'):
        end = _closing_quote(raw)
        if end > 0:
            return json.loads(raw[: end + 1])
    raw = _COMMENT.sub("", raw).strip()
    if raw in ("", "null", "~"):
        return None
    if raw.startswith("["):
        for candidate in (raw, raw.replace("'", '"')):
            try:
                return json.loads(candidate)
            except ValueError:
                continue
        return []
    if _NUMBER.fullmatch(raw):
        number = float(raw)
        return int(number) if number.is_integer() else number
    if raw.startswith("'"):
        raw = raw[1:]
    if raw.endswith("'"):
        raw = raw[:-1]
    return raw


def _closing_quote(raw: str) -> int:
    i = 1
    while i < len(raw):
        if raw[i] == "\\":
            i += 1
        elif raw[i] == '"':
            return i
        i += 1
    return -1


def parse_front_matter(text: str) -> dict:
    """Reads the `---` front matter block of a Markdown file, or {} if none."""
    m = _FRONT_MATTER.match(text)
    return parse_flat_yaml(m.group(1)) if m else {}
