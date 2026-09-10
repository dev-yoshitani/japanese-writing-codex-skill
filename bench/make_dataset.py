"""Deterministically materialize synthetic fixtures from explicit gold labels.

Run deliberately when editing fixtures, never during scoring or CI. These are
public development templates, not an independent holdout or real model outputs.
"""
import json
from pathlib import Path


def build_cases():
    # source, candidate, expected hard failure, manually authored source facts
    scenarios = [
        ("荷重は14 Nである。", "荷重は41 Nである。", True, [("quantity", "14 N")]),
        ("変位は8 mmである。", "変位を測った。", True, [("quantity", "8 mm")]),
        ("測定を行った。", "測定を9回行った。", True, []),
        ("費用は800円である。", "費用は800円と800円である。", True, [("quantity", "800円")]),
        ("長さは16 mである。", "長さは16 mmである。", True, [("quantity", "16 m")]),
        ("日付は2025年6月8日である。", "日付は2025年6月9日である。", True, [("date", "2025年6月8日")]),
        ("資料は <https://example.org/Study> を参照する。", "資料は <https://example.org/study> を参照する。", True, [("url", "https://example.org/Study")]),
        ("式は$y=x+7$である。", "式は$y=x-7$である。", True, [("equation", "$y=x+7$")]),
        ("限界荷重を確認する。", "終極荷重を確認する。", True, [("term", "限界荷重")]),
        ("入力は18 N。出力は27 N。", "入力は27 N。出力は18 N。", True, [("quantity", "18 N"), ("quantity", "27 N")]),
        ("荷重は14 Nである。", "荷重は14 Nである。", False, [("quantity", "14 N")]),
        ("幅は４２ mmである。", "幅は42 mmである。", False, [("quantity", "４２ mm")]),
        ("参加者は2,400人である。", "参加者は2400人である。", False, [("quantity", "2,400人")]),
        ("参加者は二百人である。", "参加者は200人である。", False, [("quantity", "二百人")]),
        ("荷重は2.3e3 Nである。", "荷重は2300 Nである。", False, [("quantity", "2.3e3 N")]),
        ("日付は2025年6月8日である。", "日付は2025-06-08である。", False, [("date", "2025年6月8日")]),
        ("入力は18 N。出力は27 N。", "出力は27 N。入力は18 N。", False, [("quantity", "18 N"), ("quantity", "27 N")]),
        ("温度は240 Kであり、圧力は80 Paである。", "温度は240 Kである。圧力は80 Paである。", False, [("quantity", "240 K"), ("quantity", "80 Pa")]),
        ("実際に測定を行った。", "実測した。", False, []),
        ("赤、青、白を選んだ。", "赤、青、白を選んだ。", False, []),
    ]
    contexts = {
        "natural": "記録を読み返した。", "report": "観察結果を以下に示す。",
        "technical": "試験条件を記録する。", "manual": "記録欄を確認する。",
        "essay": "資料に基づいて考える。", "application": "取り組みを振り返る。",
    }
    for genre, context in contexts.items():
        for index, (source, candidate, fail, facts) in enumerate(scenarios, 1):
            yield {"id": f"{genre}-{index:02d}", "genre": genre, "synthetic": True,
                   "source": context + source, "candidate": context + candidate,
                   "terms": ["限界荷重", "終極荷重"], "expected_fail": fail,
                   "source_facts": [{"kind": kind, "value": value} for kind, value in facts]}


if __name__ == "__main__":
    destination = Path(__file__).with_name("datasets")
    destination.mkdir(exist_ok=True)
    for genre in ("natural", "report", "technical", "manual", "essay", "application"):
        cases = [case for case in build_cases() if case["genre"] == genre]
        (destination / (genre + ".json")).write_text(json.dumps(cases, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
