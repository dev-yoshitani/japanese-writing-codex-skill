# v2 candidate scope and release criteria

The rc2 Skill adds an Astra-oriented natural-writing workflow with authored
examples. Its optional engine implements the Verification Core portion of the
supplied roadmap. It does
not publish a release, install over the existing Skill, or assert a live-LLM gain.

| Proposed capability | Candidate implementation and evidence boundary |
| --- | --- |
| Sentence alignment | Exact matching plus deterministic 1:1 / 1:2 / 2:1 DP; low-confidence warnings |
| Protected facts | Numbers, recognized units and conservative ASCII units, numeric dates/times, URLs, explicit equations/code, registered glossary terms |
| Equation/symbol/terminology lock | Delimited equations and code; bare symbols and technical terms via glossary |
| Placeholder masking | Per-original-chunk tokens with exact occurrence/order validation and restoration |
| Unsourced addition detector | Added extracted items only; arbitrary new names/claims are outside coverage |
| Edit ratio | Character opcode cost and source sentence change fraction; optional explicit thresholds |
| Ten-rule deterministic linter | Warnings only; no automatic correction |
| Constraints | Character bounds, required/forbidden phrases, count modes, optional edit ratio limit |
| Quality gate/report | Deterministic PASS/WARN/FAIL, redacted JSON and human-readable summary |
| Revision loop | One initial proposal and at most two finding-limited repairs; edit mode only |
| Structured contract | Published JSON schemas, stdlib keyword-subset validator, ID/scope checks |
| Model adapter | Protocol, callable wrapper, replay adapter; vendor-specific wrappers/live tests not run |
| Prompt injection guard | Instruction/data separation, typed patch scope, masking and gate regression cases; no claim of semantic injection immunity |
| Project glossary | Explicit flat YAML or JSON `terms` list, without unsafe constructors |
| Evaluation and CI | Fixed synthetic gold fixtures, unit/golden/replay/adversarial tests, offline CI matrix |
| Base LLM vs pipeline | NOT_RUN: needs a selected provider/model and an authorized live benchmark |

The six genre policies remain the existing Skill references; core detection
behavior is shared. Genre labels enable regression reporting and do not imply
six separately calibrated detection engines.

Before calling the final v2.0.0 release measured against real LLMs, run a separate
provider benchmark with fixed model/version, parameters, source prompts, paired
cases, item gold labels and preserved raw execution metadata. Seeds are not
universally supported or a guarantee of determinism. Save failures and report
false positives as well as recall, including each genre. Do not reuse these
development fixtures as a claimed independent holdout.

Deferred: polarity/hedging and application evidence checks, statistical voice,
surface consistency, live-provider/nightly evaluation, general rule plugins,
multiple reviewers, source citation alignment, stateful memory and a Web UI.
No runtime behavior is claimed for these roadmap items.
