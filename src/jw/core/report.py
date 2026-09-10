from collections import Counter
from dataclasses import asdict
from difflib import SequenceMatcher
from .align import align
from .constraints import Constraints, GENRES, check_constraints, count_characters
from .extract import extract
from .lint import lint
from .model import Finding
from .segment import segment

LIMITATIONS = [
    "PASS means only that the configured deterministic checks found no violation.",
    "Unregistered names, new semantic claims, negation, certainty and causal meaning are not verified.",
    "Alignment is heuristic; equations need explicit math delimiters or glossary locks for reliable coverage.",
    "Equal fact values do not prove that their attribution or conditions were preserved.",
]


def edit_ratio(source, target):
    """Changed share of the directional SequenceMatcher alignment, in [0, 1].

    Each aligned span has width max(deleted, inserted). Equal spans also count
    toward the denominator, so insertions and deletions in different locations
    cannot make the ratio exceed one. This is not Levenshtein distance or a
    naturalness score; reversing the texts can produce a different alignment.
    """
    if source == target:
        return 0.0
    matcher = SequenceMatcher(None, source, target, autojunk=False)
    spans = [(op, max(b - a, d - c)) for op, a, b, c, d in matcher.get_opcodes()]
    cost = sum(width for op, width in spans if op != "equal")
    return cost / sum(width for _, width in spans)


def _differences(left, right):
    remaining = list(right)
    lost = []
    for fact in left:
        index = next((i for i, f in enumerate(remaining) if f.key == fact.key), None)
        if index is None:
            lost.append(fact)
        else:
            remaining.pop(index)
    return lost, remaining


def compare(source, target=None, *, terms=(), constraints=None, genre="natural", include_values=False):
    """Audit one text, or verify a revision. Reports contain no prose by default."""
    if genre not in GENRES:
        raise ValueError("Unknown genre")
    if len(source) > 50000 or (target is not None and len(target) > 50000):
        raise ValueError("Documents must contain at most 50000 code points")
    constraints = constraints or Constraints()
    revision = target is not None
    target = source if target is None else target
    ss, ts = segment(source), segment(target)
    mappings = align(ss, ts)
    findings = []
    if revision and source.strip() and not target.strip():
        findings.append(Finding("content.empty", "FAIL", "Nonempty source was replaced with empty prose", tuple(s.id for s in ss)))
    source_facts, target_facts = extract(source, terms), extract(target, terms)
    # Extract within aligned chunks so moving a value between different sentences
    # does not disappear in a document-wide set comparison. Multiplicity matters.
    for mapping in mappings if revision else ():
        left_text = "".join(ss[i].text for i in mapping.source_ids)
        right_text = "".join(ts[i].text for i in mapping.target_ids)
        lost, added = _differences(extract(left_text, terms), extract(right_text, terms))
        if mapping.confidence < 0.45:
            findings.append(Finding("alignment.uncertain", "WARN", "Review sentence correspondence", mapping.source_ids, mapping.target_ids))
        # Only pair same-kind changes within a matched block. Other facts retain
        # explicit removed/added classifications rather than implying causality.
        for old in lost:
            index = next((i for i, f in enumerate(added) if f.kind == old.kind), None)
            new = added.pop(index) if index is not None else None
            details = {"kind": old.kind}
            if include_values:
                details.update(before=old.value, after=new.value if new else None)
            findings.append(Finding("fact.changed" if new else "fact.removed", "FAIL", "Protected item changed" if new else "Protected item removed", mapping.source_ids, mapping.target_ids, details))
        for new in added:
            details = {"kind": new.kind}
            if include_values:
                details["after"] = new.value
            findings.append(Finding("fact.added", "FAIL", "Protected item absent from the aligned source", mapping.source_ids, mapping.target_ids, details))
    ratio = edit_ratio(source, target) if revision else 0.0
    findings.extend(check_constraints(target, constraints, ratio if revision else None))
    findings.extend(lint(target))
    status = "FAIL" if any(f.severity == "FAIL" for f in findings) else "WARN" if findings else "PASS"
    removed_count = sum(f.rule in ("fact.changed", "fact.removed") for f in findings)
    added_count = sum(f.rule in ("fact.changed", "fact.added") for f in findings)
    source_changed = sum(len(m.source_ids) for m in mappings if "".join(ss[i].text for i in m.source_ids) != "".join(ts[i].text for i in m.target_ids))
    return {
        "schema_version": "1.0", "status": status, "mode": "compare" if revision else "audit", "genre": genre,
        "coverage": {"protected_kinds": ["number", "quantity", "date", "time", "url", "equation", "term", "verbatim"], "semantic_verification": False, "limitations": LIMITATIONS},
        "metrics": {"source_chars": count_characters(source, constraints.count_mode), "target_chars": count_characters(target, constraints.count_mode),
                    "count_mode": constraints.count_mode, "edit_ratio": round(ratio, 6),
                    "sentence_edit_ratio": round(source_changed / max(len(ss), 1), 6),
                    "source_facts": len(source_facts), "target_facts": len(target_facts),
                    "removed_or_changed": removed_count, "added_or_changed": added_count,
                    "lint_before": len(lint(source)), "lint_after": sum(f.rule.startswith("lint.") for f in findings)},
        "alignments": [asdict(m) for m in mappings], "findings": [asdict(f) for f in findings],
    }


def summary(report):
    counts = Counter(f["severity"] for f in report["findings"])
    m = report["metrics"]
    return f"{report['status']}: FAIL={counts['FAIL']}, WARN={counts['WARN']}; chars={m['target_chars']} ({m['count_mode']}), edit_ratio={m['edit_ratio']:.3f}. Lexical checks only."
