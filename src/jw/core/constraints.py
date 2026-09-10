from dataclasses import dataclass
import math
from .model import Finding

GENRES = ("natural", "report", "technical", "manual", "essay", "application")


@dataclass(frozen=True)
class Constraints:
    min_chars: int | None = None
    max_chars: int | None = None
    required: tuple[str, ...] = ()
    forbidden: tuple[str, ...] = ()
    count_mode: str = "all"
    max_edit_ratio: float | None = None

    def __post_init__(self):
        for value in (self.min_chars, self.max_chars):
            if value is not None and (type(value) is not int or value < 0):
                raise ValueError("Character bounds must be nonnegative integers")
        if self.min_chars is not None and self.max_chars is not None and self.min_chars > self.max_chars:
            raise ValueError("min_chars must not exceed max_chars")
        if self.count_mode not in ("all", "no_newlines", "no_whitespace"):
            raise ValueError("Unsupported count mode")
        if self.max_edit_ratio is not None and (type(self.max_edit_ratio) not in (int, float) or not math.isfinite(self.max_edit_ratio) or not 0 <= self.max_edit_ratio <= 1):
            raise ValueError("max_edit_ratio must be between 0 and 1")
        for items in (self.required, self.forbidden):
            if not isinstance(items, (tuple, list)) or any(not isinstance(x, str) or not x for x in items):
                raise ValueError("Constraint phrases must be nonempty strings")


def count_characters(text, mode="all"):
    if mode == "no_newlines":
        text = text.replace("\r", "").replace("\n", "")
    elif mode == "no_whitespace":
        text = "".join(text.split())
    elif mode != "all":
        raise ValueError("Unsupported count mode")
    return len(text)


def check_constraints(text, constraints, edit_ratio=None):
    count = count_characters(text, constraints.count_mode)
    result = []
    for rule, failed in (("min_chars", constraints.min_chars is not None and count < constraints.min_chars),
                         ("max_chars", constraints.max_chars is not None and count > constraints.max_chars)):
        if failed:
            result.append(Finding("constraint." + rule, "FAIL", "Character-count constraint violated", details={"count": count}))
    for rule, items in (("required", constraints.required), ("forbidden", constraints.forbidden)):
        for index, phrase in enumerate(items):
            if (phrase not in text) if rule == "required" else (phrase in text):
                result.append(Finding("constraint." + rule, "FAIL", "Phrase constraint violated", details={"phrase_index": index}))
    if edit_ratio is not None and constraints.max_edit_ratio is not None and edit_ratio > constraints.max_edit_ratio:
        result.append(Finding("constraint.edit_ratio", "FAIL", "Explicit edit-ratio limit exceeded"))
    return tuple(result)
