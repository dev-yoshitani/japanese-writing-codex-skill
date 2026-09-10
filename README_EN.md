# Japanese Writing for Codex

**v2.0.0rc2:** natural Japanese drafting and editing with Astra, including contextual
revision, voice preservation and optional deterministic checks. Read
[the v2 quickstart](README_v2.md), [architecture](docs/architecture.md)
and [evaluation evidence](docs/evaluation.md). This is a prerelease; naturalness improvements have not been established by a controlled model comparison.

[Lite ZIP](https://github.com/dev-yoshitani/japanese-writing-codex-skill/releases/download/v2.0.0rc2/japanese-writing-lite-2.0.0rc2.zip) · [Full ZIP](https://github.com/dev-yoshitani/japanese-writing-codex-skill/releases/download/v2.0.0rc2/japanese-writing-2.0.0rc2.zip)
The original Skill identity and genre references remain compatible.

The sections below document v1.x. Their public download links and historic
evaluations do not describe the v2 candidate or a live-LLM comparison.

## Historical v1.x documentation

[日本語](README.md)

`japanese-writing` is an unofficial Codex Skill for auditing, minimally editing, restructuring, and drafting Japanese prose while preserving facts, numbers, conditions, uncertainty, technical meaning, and the writer's voice.

It is not an AI-detector-evasion tool. The goal is natural and accurate Japanese whose structure follows the content, without intentional errors, forced colloquial language, random short sentences, mechanical sentence-length variation, blanket connective deletion, or invented experiences and emotions.

## Version 1.1.0

Version 1.1.0 integrates one validated core check that discourages unnecessary compliance meta-explanations in the deliverable—for example, repeatedly stating that no unsupported information was added when the user did not request such a note.

Backward compatibility is preserved:

- the Skill name remains `japanese-writing`;
- automatic invocation remains enabled;
- the six genre references are unchanged from v1.0.0; and
- no new executable or runtime dependency is introduced.

The validated improvement was integrated into this Baseline. The redundant public Improved repository has since been deleted.

## Modes and genres

| Mode | Purpose |
| --- | --- |
| `audit` | Identify issues without changing the text |
| `edit` | Make the minimum effective changes to existing prose |
| `rewrite` | Reorganize structure while preserving meaning and facts |
| `draft` | Create new prose only from the facts supplied |

| Genre | Typical use |
| --- | --- |
| `natural` | General prose and ordinary editing |
| `report` | University, laboratory, and research reports |
| `technical` | Engineering, design, analysis, calculations, tests, and specifications |
| `manual` | Procedures, setup guides, SOPs, and operating instructions |
| `essay` | Argumentative and opinion essays |
| `application` | Scholarship, motivation, self-promotion, study-abroad, and internship applications |

## Download and installation

[**Download the latest `japanese-writing.zip`**](https://github.com/yoshitani-dev/japanese-writing-codex-skill/releases/latest/download/japanese-writing.zip)

Extract the archive and place its `japanese-writing` folder at:

```text
%USERPROFILE%\.codex\skills\japanese-writing\
```

On macOS or Linux, use `${CODEX_HOME:-$HOME/.codex}/skills/japanese-writing/`. Restart Codex or begin a new task after installation.

Git installation is also available:

```powershell
git clone https://github.com/yoshitani-dev/japanese-writing-codex-skill.git "$env:USERPROFILE\.codex\skills\japanese-writing"
```

## Usage

The Skill can be selected automatically for matching Japanese-writing requests. It can also be invoked explicitly:

```text
$japanese-writing Edit this report with minimum changes. Preserve all values and units.

$japanese-writing Audit this application statement. Do not add experiences that were not provided.

$japanese-writing Rewrite this technical explanation without changing conditions, equations, or uncertainty.
```

## Verification

The substantive v1.1.0 rule is the exact core instruction evaluated in the independent Improved comparison. The public Regression set passed 24 paired cases across six genres, and the post-lock set passed six paired cases with no Accuracy regression. Fake humanization was not observed.

The original encrypted pre-registered holdout remains `NOT_TESTED` because its AES key was lost across restart. The post-lock set does not replace that holdout. See [VERIFICATION_v1.1.0.md](VERIFICATION_v1.1.0.md) for the evidence boundary and exact runtime hash.

## Security and limitations

The runtime consists only of Markdown and YAML. It does not require network access, shell execution, credentials, installers, hooks, or global configuration changes.

The Skill assists writing but cannot guarantee factual correctness or compliance. Verify technical decisions, standards, submission requirements, quotations, citations, and numeric values against authoritative source material.

## License

No license is granted at this time. Public visibility on GitHub does not by itself grant permission to copy, modify, or redistribute the repository contents.
