"""Recover a JSON object from raw LLM output that isn't guaranteed to be clean JSON."""

import json
import logging
import re
from typing import Any

logger = logging.getLogger(__name__)


def parse_json_from_llm(text: str) -> dict[str, Any]:
    """Safely parse JSON from LLM output, handling markdown blocks and `<think>` tags."""
    text = text.strip()
    text = re.sub(r"<think\b[^>]*>.*?</think>", "", text, flags=re.DOTALL | re.IGNORECASE)

    match = re.search(r"```json\s*(.*?)\s*```", text, re.DOTALL | re.IGNORECASE)
    if match:
        try:
            obj = json.loads(match.group(1).strip())
            if isinstance(obj, dict):
                return obj
        except json.JSONDecodeError:
            logger.debug("Ignoring invalid fenced JSON in LLM output.", exc_info=True)

    # Decode from left to right: nested objects must not hide the outer result.
    # raw_decode accepts explanatory prose after the closing brace and handles
    # braces that occur inside quoted string values.
    decoder = json.JSONDecoder()
    for match in re.finditer(r"\\{", text):
        try:
            obj, _ = decoder.raw_decode(text, match.start())
        except json.JSONDecodeError:
            continue
        if isinstance(obj, dict):
            return obj

    # Nothing above found valid JSON — likely the response was cut off mid-object
    # (hit max_tokens). Try to close whatever was left open, so the fields that were
    # fully generated before the cutoff still come back instead of the whole response
    # being discarded.
    return _repair_truncated_json(text)


def _repair_truncated_json(text: str) -> dict[str, Any]:
    start = text.find("{")
    if start == -1:
        return {}
    snippet = text[start:]

    stack = []
    in_string = False
    escape = False

    for ch in snippet:
        if in_string:
            if escape:
                escape = False
            elif ch == "\\":
                escape = True
            elif ch == '"':
                in_string = False
        else:
            if ch == '"':
                in_string = True
            elif ch in "{[":
                stack.append(ch)
            elif ch in "}]" and stack:
                stack.pop()

    repaired = snippet
    if in_string:
        repaired += '"'
    # Drop a dangling comma or an incomplete "key": fragment with no value at all —
    # neither can be closed into valid JSON by just appending brackets.
    repaired = re.sub(r',\s*"[^"]*"?\s*:?\s*$', "", repaired)
    repaired = re.sub(r',\s*$', "", repaired)

    for opener in reversed(stack):
        repaired += "}" if opener == "{" else "]"

    try:
        obj = json.loads(repaired)
        return obj if isinstance(obj, dict) else {}
    except json.JSONDecodeError:
        return {}
