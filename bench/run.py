"""Score fixed fixtures against gold; never generates a baseline LLM result."""
import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from jw import __version__
from jw.core.extract import extract
from jw.core.report import compare


def evaluate(directory):
    groups, failures, digest = {}, [], hashlib.sha256()
    for path in sorted(Path(directory).glob("*.json")):
        raw = path.read_bytes()
        digest.update(path.name.encode() + b"\0" + raw)
        cases = json.loads(raw)
        for case in cases:
            if case.get("synthetic") is not True:
                raise ValueError("Only explicitly synthetic fixtures are permitted")
            report = compare(case["source"], case["candidate"], terms=case["terms"], genre=case["genre"])
            predicted = report["status"] == "FAIL"
            gold = Counter((f["kind"], f["value"]) for f in case["source_facts"])
            actual = Counter((f.kind, f.value) for f in extract(case["source"], case["terms"]))
            group = groups.setdefault(case["genre"], Counter())
            group["cases"] += 1
            group["tp" if predicted and case["expected_fail"] else "fp" if predicted else "fn" if case["expected_fail"] else "tn"] += 1
            group["extraction_tp"] += sum((gold & actual).values())
            group["extraction_fp"] += sum((actual - gold).values())
            group["extraction_fn"] += sum((gold - actual).values())
            if predicted != case["expected_fail"] or gold != actual:
                failures.append(case["id"])
    if not groups:
        raise ValueError("No benchmark fixtures found")
    rows = {}
    for genre, counts in groups.items():
        def rate(top, bottom):
            return round(top / bottom, 6) if bottom else None
        rows[genre] = {key: counts[key] for key in ("cases", "tp", "fp", "fn", "tn", "extraction_tp", "extraction_fp", "extraction_fn")}
        rows[genre].update(detection_precision=rate(counts["tp"], counts["tp"] + counts["fp"]),
                           detection_recall=rate(counts["tp"], counts["tp"] + counts["fn"]),
                           extraction_precision=rate(counts["extraction_tp"], counts["extraction_tp"] + counts["extraction_fp"]),
                           extraction_recall=rate(counts["extraction_tp"], counts["extraction_tp"] + counts["extraction_fn"]))
    return {"version": __version__, "dataset_sha256": digest.hexdigest(), "kind": "synthetic_development_regression",
            "base_llm_comparison": "NOT_RUN", "independent_holdout": "NOT_RUN", "genres": rows, "failed_case_ids": failures}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--datasets", default=str(Path(__file__).with_name("datasets")))
    parser.add_argument("--output")
    args = parser.parse_args()
    result = evaluate(args.datasets)
    rendered = json.dumps(result, ensure_ascii=False, indent=2) + "\n"
    if args.output:
        with Path(args.output).open("x", encoding="utf-8") as output:
            output.write(rendered)
    else:
        print(rendered, end="")
    return int(bool(result["failed_case_ids"]))


if __name__ == "__main__":
    raise SystemExit(main())
