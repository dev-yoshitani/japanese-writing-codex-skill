#!/usr/bin/env python3
"""Offline revision review and user-reported measurement records. No detector."""
import argparse
from collections import Counter
from datetime import datetime
from difflib import unified_diff
import hashlib
import json
from pathlib import Path
import re
import sys


CUES = {
    "negation": r"していない|しなかった|できなかった|できない|ではない|なかった|ません|しない|未確認|未実施",
    "certainty": r"可能性(?:が|は)?ある|かもしれない|示唆(?:する|された|される)|推定(?:する|した|される)|実証(?:した|された|される)|証明(?:した|された)|確認(?:した|された)|明らか(?:である|になった)|確実(?:に|である)",
    "intention": r"予定|したい|希望|検討中|検討している|生かしたい",
}
ROLE_RE = re.compile(r"([一-龥々ァ-ヴーA-Za-z][一-龥々ァ-ヴーA-Za-z0-9_]{0,23})(が|を|に|は|へ)")
LITERAL_RE = re.compile(r"```[^\n]*\n.*?```|~~~[^\n]*\n.*?~~~|`[^`\n]+`|\$\$.*?\$\$|\$[^$\n]+\$|https?://[^\s<>]+", re.S)
PLACEHOLDER_RE = re.compile(r"\[(?:要確認|要本人確認|本人の|具体例|出典)[^\]\n]*\]|〔(?:要確認|要本人確認)[^〕\n]*〕|要本人確認")


def read_text(path):
    # Keep CRLF and BOM in the fingerprint: this binds a record to exact bytes.
    return Path(path).read_bytes().decode("utf-8")


def fingerprint(text):
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def prose(text):
    return LITERAL_RE.sub(lambda match: " " * len(match[0]), text)


def count(text, mode):
    if mode == "no_newlines":
        return len(text.replace("\r", "").replace("\n", ""))
    if mode == "no_whitespace":
        return len(re.sub(r"\s", "", text))
    if mode != "all":
        raise ValueError("Unknown count mode")
    return len(text)


def review(source, target, *, max_chars=None, count_mode="no_newlines", include_diff=False):
    if max_chars is not None and (type(max_chars) is not int or max_chars < 0):
        raise ValueError("Invalid maximum")
    checks = []
    left, right = prose(source), prose(target)
    for name, pattern in CUES.items():
        before, after = Counter(re.findall(pattern, left)), Counter(re.findall(pattern, right))
        if before != after:
            checks.append({"kind": name, "message": "表現の追加・脱落・強さを原文と照合する"})
    if Counter(ROLE_RE.findall(left)) != Counter(ROLE_RE.findall(right)):
        checks.append({"kind": "roles", "message": "主体・対象と助詞の対応を照合する（漢字・カタカナ・英字の語だけを検査）"})
    if PLACEHOLDER_RE.search(right):
        checks.append({"kind": "placeholder", "message": "最終稿に確認待ちの表示が残っている"})
    characters = count(target, count_mode)
    if max_chars is not None and characters > max_chars:
        checks.append({"kind": "length", "message": "指定文字数の上限を超えている"})
    if source.strip() and not target.strip():
        checks.append({"kind": "empty", "message": "原文が空の稿に置き換わっている"})
    result = {
        "schema_version": 1,
        "status": "REVIEW" if checks else "CHECKED",
        "source_sha256": fingerprint(source), "target_sha256": fingerprint(target),
        "characters": characters, "count_mode": count_mode,
        "checks": checks,
        "meaning_verified": False, "detector_measured": False,
        "limitations": [
            "候補がない場合も、意味の保持・本人の文体・AI検出結果を保証しない。",
            "語の出現数だけでは、否定の範囲、数値の帰属、同じ文中の役割交換を判定できない。",
            "事実・数字・引用・条件と、全文の追加・脱落は別途原文と読み比べる。",
        ],
    }
    if include_diff:
        result["diff"] = "".join(unified_diff(source.splitlines(keepends=True), target.splitlines(keepends=True), fromfile="source", tofile="final"))
    return result


def measurement_record(text, metadata):
    required = {"detector", "measured_at", "scope", "settings", "metrics"}
    if not isinstance(metadata, dict) or set(metadata) - required - {"version"} or not required <= set(metadata):
        raise ValueError("Invalid measurement fields")
    if not isinstance(metadata["detector"], str) or not metadata["detector"].strip():
        raise ValueError("Detector required")
    if "version" in metadata and not isinstance(metadata["version"], str):
        raise ValueError("Invalid version")
    if metadata["scope"] != "full_text" or not isinstance(metadata["settings"], dict):
        raise ValueError("Record full text and explicit settings")
    if not isinstance(metadata["measured_at"], str):
        raise ValueError("Measurement time required")
    measured = datetime.fromisoformat(metadata["measured_at"].replace("Z", "+00:00"))
    if measured.tzinfo is None or measured > datetime.now(measured.tzinfo):
        raise ValueError("Use a past or present timezone-aware measurement time")
    metrics = metadata["metrics"]
    if not isinstance(metrics, list) or not metrics:
        raise ValueError("Metrics required")
    for metric in metrics:
        if not isinstance(metric, dict) or set(metric) != {"label", "value"}:
            raise ValueError("Keep exact metric labels and display values")
        if any(not isinstance(metric[key], str) or not metric[key].strip() for key in ("label", "value")):
            raise ValueError("Metrics must be display strings")
    if not text.strip():
        raise ValueError("Empty measurement text")
    return {"schema_version": 1, "input_sha256": fingerprint(text),
            "result_source": "user_reported", "measurement_verified": False,
            "metadata": metadata}


def verify_record(text, record):
    expected_keys = {"schema_version", "input_sha256", "result_source", "measurement_verified", "metadata"}
    if not isinstance(record, dict) or set(record) != expected_keys or record["schema_version"] != 1:
        raise ValueError("Invalid record")
    if record["result_source"] != "user_reported" or record["measurement_verified"] is not False:
        raise ValueError("Invalid provenance")
    # Validate the stored metadata too; a hash match alone cannot validate a report.
    measurement_record(text, record["metadata"])
    matches = record["input_sha256"] == fingerprint(text)
    return {"status": "MATCH" if matches else "STALE", "input_matches": matches,
            "measurement_verified": False, "result_source": "user_reported"}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    compare = commands.add_parser("review")
    compare.add_argument("source")
    compare.add_argument("final")
    compare.add_argument("--max-chars", type=int)
    compare.add_argument("--count-mode", choices=("all", "no_newlines", "no_whitespace"), default="no_newlines")
    compare.add_argument("--include-diff", action="store_true", help="Include private prose only when explicitly requested")
    record = commands.add_parser("record")
    record.add_argument("text")
    record.add_argument("--result", required=True, help="User-supplied displayed results; does not call any detector")
    record.add_argument("--output", required=True, help="New private JSON file; never overwritten")
    verify = commands.add_parser("verify")
    verify.add_argument("text")
    verify.add_argument("--record", required=True)
    args = parser.parse_args(argv)
    try:
        if args.command == "review":
            result = review(read_text(args.source), read_text(args.final), max_chars=args.max_chars,
                            count_mode=args.count_mode, include_diff=args.include_diff)
            exit_code = 0
        elif args.command == "record":
            result = measurement_record(read_text(args.text), json.loads(read_text(args.result)))
            rendered = json.dumps(result, ensure_ascii=False, indent=2, allow_nan=False)
            with Path(args.output).open("x", encoding="utf-8") as handle:
                handle.write(rendered + "\n")
            result = {"status": "RECORDED", "result_source": "user_reported", "measurement_verified": False}
            exit_code = 0
        else:
            result = verify_record(read_text(args.text), json.loads(read_text(args.record)))
            exit_code = 0 if result["input_matches"] else 3
        print(json.dumps(result, ensure_ascii=False, indent=2, allow_nan=False))
        return exit_code
    except (ValueError, OSError, TypeError, KeyError):
        print("voice_check: invalid input or existing output; no overwrite permitted", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
