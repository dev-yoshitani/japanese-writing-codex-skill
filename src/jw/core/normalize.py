"""Normalization with offsets into the original string; never rewrites user text."""
import re
import unicodedata
from decimal import Decimal, InvalidOperation


def mapped_nfkc(text):
    chars, offsets = [], []
    for i, char in enumerate(text):
        normalized = unicodedata.normalize("NFKC", char)
        chars.extend(normalized)
        offsets.extend([i] * len(normalized))
    return "".join(chars), offsets


def nfkc(text):
    return unicodedata.normalize("NFKC", text)


def japanese_integer(text):
    digits = {c: i for i, c in enumerate("〇一二三四五六七八九")}
    digits["零"] = 0
    if all(c in digits for c in text):
        return int("".join(str(digits[c]) for c in text))
    total = section = number = 0
    previous_small = 10000
    previous_large = 10**16
    for c in text:
        if c in digits:
            if number:
                raise ValueError("Ambiguous Japanese numeral")
            number = digits[c]
        elif c in "十百千":
            unit = {"十": 10, "百": 100, "千": 1000}[c]
            if unit >= previous_small:
                raise ValueError("Invalid Japanese numeral order")
            section += (number or 1) * unit
            previous_small, number = unit, 0
        elif c in "万億兆":
            large = {"万": 10**4, "億": 10**8, "兆": 10**12}[c]
            if large >= previous_large:
                raise ValueError("Invalid Japanese numeral order")
            total += (section + number or 1) * large
            previous_large = large
            section = number = 0
            previous_small = 10000
        else:
            raise ValueError("Unsupported numeral")
    return total + section + number


def number_key(text):
    value = nfkc(text).replace(",", "").replace("−", "-")
    if re.fullmatch(r"[〇零一二三四五六七八九十百千万億兆]+", value):
        try:
            value = str(japanese_integer(value))
        except ValueError:
            return value
    try:
        numeric = Decimal(value)
        if numeric.is_finite():
            # Decimal.normalize() uses ambient precision and can silently round
            # long integers. Canonicalize the exact tuple without arithmetic.
            sign, raw_digits, exponent = numeric.as_tuple()
            digits = list(raw_digits)
            if not any(digits):
                return "0e0"
            while digits[-1] == 0:
                digits.pop()
                exponent += 1
            return ("-" if sign else "") + "".join(map(str, digits)) + "e" + str(exponent)
    except InvalidOperation:
        pass
    return value
