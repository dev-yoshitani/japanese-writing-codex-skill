# Changelog

## v2.0.0rc2 — 2026-09-10 (prerelease)

- Prioritize natural prose with Astra: context, reading flow, writer voice and
  selective editing; consolidate repeated core instructions without changing
  the Skill name, invocation policy, four modes or six genre guides.
- Add worked examples with semantic review notes and deterministic checks;
  these are authored examples, not a live model benchmark or human preference study.
- Give the edit adapter masked read-only context for the whole original document.
  Allow an empty proposal to retain appropriate WARN wording without more retries.
- Fix character edit ratios exceeding 100%. The aligned-span denominator replaces
  the larger-document denominator; review any rc1 thresholds before reusing them.
- Retain rc1 evaluation and packages as historical evidence. Distribute rc2 as
  a prerelease with Full/Lite ZIPs. No provider integration or global model setting is included.

## v2.0.0rc1 — 2026-09-09 (local candidate)

- Add an optional stdlib verification engine: lexical protected-fact extraction,
  lossless segmentation, sentence alignment, occurrence-aware diff, exact masking,
  ten advisory lint rules, explicit constraints and redacted PASS/WARN/FAIL reports.
- Add schema-validated sentence patches, finding-limited repair (at most two
  retries), callable/replay model adapters, audit/compare/replay CLI and flat YAML
  or JSON glossary/configuration support.
- Add fixed synthetic gold fixtures, regression/golden/replay/adversarial tests,
  offline CI, architecture/ADRs and verified Full/Lite packaging.
- Preserve the Skill name, invocation metadata, four modes and six genre files.
- Keep semantic checks and live-provider benchmarks explicitly outside measured
  coverage; no published v2 release or license change is asserted.

See [evaluation](docs/evaluation.md) for current evidence. The root `SHA256SUMS`
remains the historical v1.1.0 asset checksum. v2 archive checksums are generated
alongside the v2 ZIPs by `tools/package_v2.py`.

## v1.1.0 — 2026-08-29

### Added

- One validated core check against unnecessary compliance meta-explanations in the deliverable.
- Full English documentation in `README_EN.md`.
- A sanitized public verification summary in `VERIFICATION_v1.1.0.md`.

### Preserved

- Skill identity: `japanese-writing`.
- Automatic invocation behavior.
- All six genre references from v1.0.0.
- Accuracy-first handling of facts, values, units, conditions, uncertainty, technical meaning, and personal experience.

### Not added

- Intentional errors or forced colloquial language.
- Mechanical sentence-length variation or connective deletion.
- Invented experiences, emotions, failures, facts, or values.
- AI-detector-evasion processing.

## v1.0.0 — 2026-08-27

- Initial public release.
