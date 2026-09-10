import re
from dataclasses import dataclass
from .extract import extract

TOKEN = re.compile(r"⟦JW\d+:\d+⟧")


@dataclass(frozen=True)
class MaskedText:
    text: str
    replacements: tuple[tuple[str, str], ...]


def mask(text, terms=(), namespace=0):
    if "⟦JW" in text:
        raise ValueError("Input uses the reserved placeholder namespace")
    result, cursor, replacements = [], 0, []
    for i, fact in enumerate(extract(text, terms)):
        token = f"⟦JW{namespace}:{i}⟧"
        result.extend((text[cursor:fact.start], token))
        replacements.append((token, fact.value))
        cursor = fact.end
    result.append(text[cursor:])
    return MaskedText("".join(result), tuple(replacements))


def restore(text, masked):
    expected = [token for token, _ in masked.replacements]
    found = TOKEN.findall(text)
    if found != expected:
        raise ValueError("Placeholder loss, duplication, movement or unknown token")
    stripped = TOKEN.sub("", text)
    if "⟦JW" in stripped:
        raise ValueError("Malformed placeholder")
    values = dict(masked.replacements)
    return TOKEN.sub(lambda match: values[match.group()], text)
