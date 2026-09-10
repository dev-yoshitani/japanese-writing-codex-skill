"""Ten deterministic advisory rules; findings never authorize automatic rewrites."""
import re
from collections import Counter
from .model import Finding
from .segment import segment

RULES = {
    "long_sentence": "A sentence exceeds the configured length",
    "repeated_ending": "Three adjacent sentences share an ending",
    "duplicate_sentence": "An identical sentence occurs again",
    "emphasis_density": "Three or more emphasis expressions in one sentence",
    "repeated_triad": "Adjacent sentences both contain a three-item enumeration",
    "compliance_meta": "A task-compliance statement appears in the prose",
    "repeated_opening": "Three adjacent sentences share the same opening",
    "connective_run": "Three adjacent sentences begin with connectives",
    "verbose_phrase": "A potentially verbose phrase appears",
    "mixed_register": "Polite and plain endings coexist",
}


def lint(text, long_sentence=120):
    sentences = segment(text)
    findings, endings, openings, connectives, triads, registers = [], [], [], [], [], []
    seen = Counter()
    for sentence in sentences:
        value = sentence.text.strip()
        # Code and explicit equations are outside prose-style rules.
        if value.startswith(("```", "~~~", "$$", "\\[")):
            endings.append(""); openings.append(""); connectives.append(False); triads.append(False); registers.append("")
            continue
        ids = (sentence.id,)

        def warn(rule):
            findings.append(Finding("lint." + rule, "WARN", RULES[rule], target_ids=ids))

        if len(value) > long_sentence:
            warn("long_sentence")
        ending = re.search(r"(である|だった|ました|ません|です|ます|だ)[。！？!?」』]*$", value)
        endings.append(ending[1] if ending else "")
        openings.append(value[:5] if len(value) >= 5 else "")
        connectives.append(bool(re.match(r"(?:また|さらに|一方で|このように|そのため)[、,]", value)))
        triads.append(bool(re.search(r"[^、。]{1,20}、[^、。]{1,20}、[^、。]{1,20}(?:を|が|は|に)", value)))
        registers.append("polite" if endings[-1] in ("です", "ます", "ました", "ません") else "plain" if endings[-1] else "")
        seen[value] += 1
        if value and seen[value] > 1:
            warn("duplicate_sentence")
        if len(re.findall(r"非常に|極めて|大変|圧倒的|絶対に|極大", value)) >= 3:
            warn("emphasis_density")
        if re.search(r"(?:指示|ご要望|条件)(?:に|を).{0,10}(?:従|遵守|守)|(?:事実|情報)を追加していません", value):
            warn("compliance_meta")
        if re.search(r"することが可能である|ということができる|という点において", value):
            warn("verbose_phrase")
        i = sentence.id
        for rule, items in (("repeated_ending", endings), ("repeated_opening", openings)):
            if i >= 2 and items[-1] and items[-1] == items[-2] == items[-3]:
                warn(rule)
        if i >= 2 and all(connectives[-3:]):
            warn("connective_run")
        if i >= 1 and all(triads[-2:]):
            warn("repeated_triad")
    if "polite" in registers and "plain" in registers:
        findings.append(Finding("lint.mixed_register", "WARN", RULES["mixed_register"], target_ids=tuple(s.id for s, r in zip(sentences, registers) if r)))
    return tuple(findings)
