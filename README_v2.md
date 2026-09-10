# Japanese Writing — Natural prose with Astra

Japanese Writing helps Astra draft and revise natural Japanese while preserving
facts and the writer's voice. It focuses on sentence connections, reading load,
information order and appropriate vocabulary. The optional Python engine checks
protected occurrences and explicit constraints before and after an edit.
**Version 2.0.0rc2 is a prerelease, not a final stable release.**

## Write with Astra

Use the Skill with Astra selected in your host. The Skill does not select or
switch models, install a provider SDK or call a paid API on its own. Existing
text defaults to local editing; a full rewrite requires an explicit request.

Example requests:

- `自然な文章に整えて。語彙や調子は残し、必要な箇所だけ直して。`
- `この資料から大学レポートを書いて。だ・である調で、段落が自然につながるように。`
- `構成から書き直して。事実と断定の強さは維持して。`

The [Astra writing guide](references/astra-writing.md) supports whole-context
reading, selective revision and a final meaning/voice review. It avoids mandatory
outlines, repeated scoring and decorative formatting. The six genre guides and
four modes remain available. Lint warnings can remain when wording is appropriate.
See [the worked examples](docs/natural-writing-examples.ja.md) and
[evaluation evidence](docs/evaluation.md) for the limits of the current checks.

The LLM proposes; deterministic code verifies a declared lexical subset.
`PASS` is not a guarantee of semantic preservation.

## Quickstart

Python 3.10+ is sufficient. No dependencies, API keys or network access are needed:

```console
python scripts/jw.py audit examples/source.txt --genre technical --json
python scripts/jw.py compare examples/source.txt examples/changed.txt --json
python -m unittest discover -s tests -v
```

The second command deliberately exits with code **1** because `12 mm` was changed
to `21 mm`. Audit and comparison emit reports; they never edit either input.
Exit 0 means PASS/WARN, exit 1 means a gate failure, and exit 2 means invalid input,
configuration or output path. To install the optional Python console command,
use `python -m pip install .` in a suitable environment; this invokes the declared
setuptools build dependency. Running the script directly avoids package installation.

## What is implemented

- Numbers, units, numeric dates/times, URLs, explicit equations/code and glossary locks.
- Sentence correspondence, occurrence-aware removed/changed/added findings,
  character and sentence edit ratios, ten advisory lint rules, character bounds
  and required/forbidden phrases.
- Exact placeholder restoration, JSON response/report contracts, deterministic
  hard/soft gates, and at most two repairs restricted to finding-related chunks.
- Model-neutral protocol, a caller-supplied function adapter and explicit replay.
- Fixed synthetic gold, regression/golden/replay/adversarial tests and offline CI.

For the complete boundary, read [scope](docs/scope.md), [architecture](docs/architecture.md)
and [design decisions](docs/adr/0001-deterministic-gates.md).

## Report example

```json
{
  "status": "FAIL",
  "coverage": {"semantic_verification": false},
  "metrics": {"removed_or_changed": 1, "added_or_changed": 1},
  "findings": [{"rule": "fact.changed", "severity": "FAIL", "details": {"kind": "quantity"}}]
}
```

This is an excerpt; the full versioned schema is in
[report.schema.json](src/jw/contracts/report.schema.json).
Reports omit source prose and protected values by default. `--include-values`
explicitly reveals changed protected values in a comparison report.

## Configuration and replay

```console
python scripts/jw.py compare original.txt revised.txt --config examples/.jw.yaml --json
python scripts/jw.py audit original.txt --max-chars 400 --count-mode no_newlines --require 根拠 --forbid 必ず成功
python scripts/jw.py replay examples/source.txt examples/replay.json --output accepted.txt --json
```

`accepted.txt` must be a new path. If the final gate fails, it is not created.
The replay fixture is hand-authored synthetic data; it is not recorded LLM output.

Configuration supports JSON and a flat YAML subset (top-level scalar keys and
indented scalar lists). Unsupported YAML constructs and unknown keys fail closed.
`--glossary glossary/example.yaml` adds exact normalized term locks. There is no
automatic configuration discovery or object construction.

`--max-edit-ratio` enforces an explicit threshold. Optional `--strictness`
presets are conservative 0.15, balanced 0.35 and broad 0.65. These are engineering
defaults, not calibrated writing-quality scores; no threshold is applied by default.
Since rc2, the character ratio is the sum of `max(deleted, inserted)` per
SequenceMatcher non-equal opcode divided by the sum of those widths over **all**
opcodes, including equal spans. It is bounded by 0–1. This fixes rc1's ratio above
1 for edits with deletions and insertions at different locations. It is a directional
alignment measure, not Levenshtein distance or a writing-quality score. Thresholds
chosen for rc1 should be reviewed because the denominator changed.

## Evaluation evidence

The fixed development benchmark contains **120 cases: 20 scenario templates
reused across six genre contexts**. It is not 120 independent natural-language
examples and is not a holdout. The 300 numeric mutation/width subcases are
additional generated regression checks, not LLM quality evaluations.
Measured results and limitations are recorded in [evaluation.md](docs/evaluation.md).

| Comparison | Status |
| --- | --- |
| Deterministic engine vs synthetic gold | Implemented and locally tested |
| Base LLM vs Japanese Writing | NOT_RUN |
| Independent holdout | NOT_RUN |
| GitHub-hosted CI execution for v2 | NOT_RUN; workflow added locally |
| Provider-specific live integration | NOT_RUN; caller-supplied adapter interface only |

No AI-detector evasion, fabricated experience, arbitrary 0–100 quality score,
semantic correctness guarantee or unsupported performance claim is provided.

## Skill compatibility and packages

The Skill keeps its `japanese-writing` name, implicit invocation metadata, four
modes and six genre references. The optional verifier is additive. Lite retains
Markdown/YAML operation; Full includes the Python engine, examples, tests and docs.
Neither archive is automatically installed.

```console
python tools/package_v2.py --output-dir dist
```

This creates verified Full and Lite ZIPs plus SHA-256 checksums, tests archive
contents and runs the extracted Full CLI and suite. Output archives are never
overwritten. [Download Lite](https://github.com/dev-yoshitani/japanese-writing-codex-skill/releases/download/v2.0.0rc2/japanese-writing-lite-2.0.0rc2.zip) or
[download Full](https://github.com/dev-yoshitani/japanese-writing-codex-skill/releases/download/v2.0.0rc2/japanese-writing-2.0.0rc2.zip). Public v1.x links remain historical.

## License and provenance

The inherited repository states that no license is granted. This candidate
preserves that status and does not claim an MIT or Apache license.
[THIRD_PARTY_SOURCES.md](THIRD_PARTY_SOURCES.md) retains the existing provenance.
New benchmark fixtures and examples were authored synthetically for this
implementation; no personal application documents were used.
