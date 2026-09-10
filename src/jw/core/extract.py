"""Conservative lexical subset. No named-entity or semantic claim inference."""
import re
from .model import Fact
from .normalize import mapped_nfkc, nfkc, number_key

ARABIC = r"[+\-−]?(?:(?:\d{1,3}(?:,\d{3})+|\d+)(?:\.\d+)?|\.\d+)(?:[eE][+\-]?\d+)?"
KANJI = r"[〇零一二三四五六七八九十百千万億兆]+"
UNITS = ("m/s²", "m/s^2", "m/s2", "m/s", "km/h", "N/mm²", "N/mm^2", "N/mm2",
         "kg/m³", "kg/m^3", "kg/m3", "MPa", "GPa", "kPa", "hPa", "Pa", "kN", "N",
         "mm²", "mm^2", "mm2", "m²", "m^2", "m2", "mm", "cm", "km", "m", "kg", "mg", "g",
         "ms", "s", "Hz", "kHz", "MHz", "V", "A", "W", "kW", "°C", "K", "%", "‰",
         "万円", "円", "人", "個", "件", "回", "点", "字", "倍", "時間", "分", "秒", "日", "年")
UNIT = "(?:" + "|".join(re.escape(nfkc(u)) for u in sorted(set(UNITS), key=len, reverse=True)) + ")(?![A-Za-z0-9])"
NUMERIC = re.compile(ARABIC + r"[ \t]*" + UNIT)
# A separate unbounded numeric extractor covers numbers attached to Japanese text.
BARE_NUMBER = re.compile(ARABIC)
GENERIC_QUANTITY = re.compile(ARABIC + r"[ \t]*[A-Za-zµμ°][A-Za-z0-9µμ°/*^+\-]*")
KANJI_QUANTITY = re.compile(KANJI + r"[ \t]*" + UNIT)
DATE = re.compile(r"\d{4}(?:年\d{1,2}月\d{1,2}日|[-/]\d{1,2}[-/]\d{1,2})(?!\d)")
TIME = re.compile(r"(?<!\d)\d{1,2}:\d{2}(?::\d{2})?(?!\d)")
URL = re.compile(r"https?://[^\s<>\"「」『』。！？、）]+")
VERBATIM = re.compile(r"```[\s\S]*?```|~~~[\s\S]*?~~~|`[^`\n]+`")
MATH = re.compile(r"\$\$[\s\S]*?\$\$|\$[^$\n]+\$|\\\[[\s\S]*?\\\]|\\\([^\n]*?\\\)")
# Plain-text equations deliberately exclude prose and ambiguous open-ended terms.
PLAIN_MATH = re.compile(r"[A-Za-zΑ-ω][A-Za-zΑ-ω0-9_]*[ \t]*=[ \t]*[A-Za-zΑ-ω0-9_.+\-*/^() ]+")


def extract(text, terms=()):
    normalized, offsets = mapped_nfkc(text)
    accepted = []

    def add(kind, start, end, canonical):
        if start >= end or any(start < f.end and end > f.start for f in accepted):
            return
        accepted.append(Fact(kind, text[start:end], canonical, start, end))

    # Exact preservation for code, equations, and URL paths. Normalization must
    # never equate mathematically distinct Unicode symbols or case-sensitive URLs.
    for kind, pattern in (("verbatim", VERBATIM), ("equation", MATH), ("url", URL), ("equation", PLAIN_MATH)):
        for match in pattern.finditer(text):
            value = match.group().rstrip(".,;:!?)]}" if kind == "url" else " \t")
            add(kind, match.start(), match.start() + len(value), value)

    def mapped_add(kind, match, canonical):
        add(kind, offsets[match.start()], offsets[match.end() - 1] + 1, canonical)

    for term in sorted(set(terms), key=lambda t: (-len(t), t)):
        if not isinstance(term, str) or not term.strip():
            raise ValueError("Locked terms must be nonempty strings")
        for match in re.finditer(re.escape(nfkc(term)), normalized):
            mapped_add("term", match, nfkc(term))
    for match in DATE.finditer(normalized):
        year, month, day = map(int, re.findall(r"\d+", match.group()))
        # Preserve lexical dates even if invalid; this engine is not a calendar validator.
        mapped_add("date", match, f"{year:04d}-{month:02d}-{day:02d}")
    for match in TIME.finditer(normalized):
        mapped_add("time", match, ":".join(str(int(n)) for n in match.group().split(":")))
    for pattern in (NUMERIC, KANJI_QUANTITY, GENERIC_QUANTITY, BARE_NUMBER):
        for match in pattern.finditer(normalized):
            if pattern is GENERIC_QUANTITY and re.fullmatch(ARABIC, match.group()):
                continue
            number = re.match(ARABIC + "|" + KANJI, match.group())
            rest = match.group()[number.end():].strip()
            mapped_add("quantity" if rest else "number", match, number_key(number.group()) + (" " + rest if rest else ""))
    return tuple(sorted(accepted, key=lambda f: f.start))
