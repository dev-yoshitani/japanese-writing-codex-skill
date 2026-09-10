from .extract import VERBATIM, MATH, URL
from .model import Sentence


def segment(text):
    """Lossless sentence chunks including whitespace; offsets are Python code points."""
    protected = [m.span() for p in (VERBATIM, MATH, URL) for m in p.finditer(text)]
    result, start, i = [], 0, 0
    while i < len(text):
        inside = next((end for begin, end in protected if begin <= i < end), None)
        if inside is not None:
            i = inside
            continue
        char = text[i]
        terminal = char in "。！？!?\n" or (char == "." and (i + 1 == len(text) or text[i + 1].isspace()))
        i += 1
        if terminal:
            while i < len(text) and text[i] in "」』）\"' \t\r\n":
                i += 1
            result.append(Sentence(len(result), text[start:i], start, i))
            start = i
    if start < len(text):
        result.append(Sentence(len(result), text[start:], start, len(text)))
    return tuple(result)
