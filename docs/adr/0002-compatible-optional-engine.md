# ADR 0002: preserve the Skill and add an optional engine

Status: accepted for the v2 candidate.

Existing users install a root `SKILL.md` and seven references. Moving it into a
different directory or requiring Python for normal prose editing would break
those workflows.

Decision: retain the root and invocation policy. Add `src/jw`, a dependency-free
script entry point, a Lite archive and a full source/runtime archive. No live
provider calls, keys or secrets are needed for the default tests.
Expose a protocol plus callable and replay adapters. Future provider-specific
wrappers can use the same protocol without changing core verification.

No license was granted in the inherited repository. This candidate preserves
that status; MIT/Apache licensing requires an owner decision and provenance review.
The work is not presented as a completed open-source license transition.
