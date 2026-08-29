# v1.1.0 Verification Summary

This is a sanitized public summary for the v1.1.0 runtime. It excludes local absolute paths, private identity maps, raw generation traces, internal workflow logs, case bodies, and encrypted holdout material.

## Runtime composition

Version 1.1.0 preserves the v1.0.0 `SKILL.md`, `agents/openai.yaml`, and all six genre references. Its only runtime instruction change is the exact validated `references/core.md` item from the independently evaluated Improved candidate.

| Property | v1.1.0 status |
| --- | --- |
| Skill name | `japanese-writing` |
| Automatic invocation | enabled; unchanged |
| Runtime files | 9 |
| Genre-reference changes | none |
| Executable runtime files | none |
| Canonical runtime tree SHA-256 | `527ab92c9048ba7f6f270942a20cb7699e4cdf3eab112d0ca3ba81cc698849ad` |
| Release ZIP SHA-256 | `fa6f5677a92ca56880ca070a7baa76abb88f7f3096ba650f56271bfd34893f59` |

The canonical tree hash is the SHA-256 of sorted rows in the form `normalized-relative-path<TAB>lowercase-file-sha256`, joined with LF and no trailing LF.

## Behavioral evidence for the adopted rule

- Public Regression: 24 paired cases across `natural`, `report`, `technical`, `manual`, `essay`, and `application` passed for both Baseline and Improved, with no Accuracy regression.
- Later paired observations: unnecessary compliance meta-explanations appeared in five Baseline cases and two Improved cases.
- Post-lock verification: six new paired cases created after the Improved tree freeze passed the Style gate and Accuracy checks.
- Post-lock Accuracy: 6/6 cases and 12/12 outputs passed, with zero Improved regressions.
- Fake humanization: none observed.
- Post-lock Style detail: five ties and one local, non-material preference for the Baseline report output; no repeated new defect was found.

The v1.1.0 package changes no evaluated genre instruction and introduces no additional Style rule beyond the validated core item.

## Required holdout separation

```text
Original pre-registered holdout:
- status: NOT_TESTED
- reason: AES key lost across restart
- encrypted cases intact: YES

Post-lock verification:
- cases: 6
- created after improved freeze: YES
- result: PASS
- accuracy regression: NO
```

The post-lock verification set does not replace the original pre-registered holdout and is not reported as a pre-registered holdout.

## Accuracy boundary

Accuracy takes precedence over Style. Protected content includes numbers, units, dates, proper nouns, quotations, equations, conditions, uncertainty, negation, causality, technical terminology, calculated and experimental values, Limit/Ultimate distinctions, and personal experience.

Technical and manual regularity required for accuracy or reproducibility is not treated as a Style defect. Artificial irregularity is not treated as an improvement.

## Remaining limitations

- The original encrypted pre-registered holdout remains `NOT_TESTED`; its performance distribution is unknown.
- A model or runtime change can alter generated output even when Skill files are unchanged.
- One post-lock report case showed a local, non-material over-summary tendency. It did not recur and did not justify a new rule.

Any later runtime change requires renewed validation before it can inherit the v1.1.0 PASS claims.
