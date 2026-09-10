# ADR 0001: deterministic gates with explicit lexical coverage

Status: accepted for the v2 candidate.

The initial proposal described semantic preservation and unsourced-claim detection.
Regex and normalization cannot prove either. Treating such a result as PASS would
misrepresent the engine's capability and could hide changed negation or causality.

Decision: hard gates use observable protected occurrences, explicit constraints,
schema/patch validity and nonempty replacement text. Lint is advisory. Reports
declare `semantic_verification: false`. Numeric normalization uses exact Decimal
tuples to avoid ambient-precision rounding. Original literals are restored from
per-sentence placeholders; user text is never normalized in place.

Consequences: reproducible tests are possible, including malformed-model output.
Unknown names, claims, certainty, negation and semantic attribution still need
review. Strong semantic claims and a numerical LLM self-rating are excluded.

Alternatives: an LLM judge may provide auxiliary review later, but its opinion
must not override a deterministic failure or become an uncalibrated 0–100 score.
