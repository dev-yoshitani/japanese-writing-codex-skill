"""Small, explicit JSON / flat YAML data loader. Never constructs objects or tags."""
import json
import re
from pathlib import Path


def _scalar(text):
    text = text.strip()
    try:
        value = json.loads(text)
    except json.JSONDecodeError:
        if text.startswith("'") and text.endswith("'"):
            value = text[1:-1].replace("''", "'")
        elif re.search(r"[\[\]{}&*!|>#]", text) or not text:
            raise ValueError("Unsupported YAML syntax; use JSON or flat YAML scalars/lists") from None
        else:
            value = text
    if isinstance(value, (dict, list)):
        raise ValueError("Use YAML block lists or JSON documents")
    return value


def load_data(path):
    content = Path(path).read_text(encoding="utf-8-sig")
    try:
        data = json.loads(content)
    except json.JSONDecodeError:
        data, current = {}, None
        for line in content.splitlines():
            if not line.strip() or line.lstrip().startswith("#"):
                continue
            item = re.fullmatch(r"[ \t]+-[ \t]+(.+)", line)
            if item:
                if current is None or not isinstance(data[current], list):
                    raise ValueError("Unexpected YAML list item")
                data[current].append(_scalar(item[1]))
                continue
            pair = re.fullmatch(r"([A-Za-z_][A-Za-z0-9_]*):[ \t]*(.*)", line)
            if not pair or pair[1] in data:
                raise ValueError("Invalid or duplicate YAML key")
            current = pair[1]
            data[current] = _scalar(pair[2]) if pair[2] else []
    if not isinstance(data, dict):
        raise ValueError("Configuration must be an object")
    return data
