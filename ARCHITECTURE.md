# Architecture

For the v2 candidate, see [Verification Core architecture](docs/architecture.md).
The sections below preserve the historical v1.x design and source snapshot.

## Decision

一つのumbrella Skill `japanese-writing`を採用した。6個の独立Skillには分割しない。

理由は、すべてのgenreで「事実・数値・意味・声の保持」「捏造禁止」「modeの編集範囲」「最終validation」を共有し、差分がgenre固有の判断基準に集中するためである。独立Skillにすると、同じ依頼で複数Skillが競合し、modeとgenreの組合せが分散する。umbrella構成ならrouterを一か所で管理し、必要なreferenceだけを読むprogressive disclosureを実現できる。

現時点で、分割によるrouting精度向上、context削減、Eval上の改善は確認されていない。したがって、ユーザーが示した第一候補を維持した。

## Current Codex specification

現行のOpenAI公式Skill仕様と同梱`skill-creator`を基準にした。

- directoryのentrypointは`SKILL.md`
- YAML frontmatterの必須fieldは`name`と`description`
- `references/`をprogressive disclosureに使用できる
- `agents/openai.yaml`はUI metadataとimplicit invocation policyに使用できる
- validatorは同梱`skill-creator/scripts/quick_validate.py`を使用する

公式資料: [Build skills](https://learn.chatgpt.com/docs/build-skills)

## Why this is not a plugin

この成果物は個人の日本語writing workflowであり、外部connector、MCP server、配布用package manifestを必要としない。公式のplugin guidanceも、個人workflowはまずSkillから始め、共有・配布・connectorが必要な場合にpluginを選ぶとしている。そのため`.codex-plugin/plugin.json`やmarketplace entryは追加しない。

公式資料: [Build plugins](https://learn.chatgpt.com/docs/build-plugins)

## Runtime topology

```text
User request
  -> mode: audit | edit | rewrite | draft
  -> primary genre
  -> SKILL.md
  -> references/core.md
  -> one genre reference
  -> output
  -> validation
```

複合成果物でgenre固有要件が実際に重なる場合だけ、二つ目のgenre referenceを読む。`research/`、`evals/`、`THIRD_PARTY_SOURCES.md`はdevelopment provenanceであり、runtime contextへ読み込まない。

## Mode boundaries

- `audit`: 本文を変更しない。
- `edit`: minimum effective edit。既存文章のdefault。
- `rewrite`: 明示的な全面修正時だけ構成まで変更する。
- `draft`: 与えられた資料から新規作成する。

modeで第三者Source間のminimum edit対aggressive rewriteの競合を解消した。

## Genre routing

明示された提出形式を起点にする。ただし、数値、単位、数式、設計判定、試験条件が中心なら`technical`を主genreとする。操作の再現が中心なら`manual`、課題への論証なら`essay`、応募設問なら`application`、大学・授業の結果と考察なら`report`、それ以外は`natural`とする。

## Independence

Runtime ruleはSource名を含まず、10 Sourceの削除後も動作する。GitHub、skills.sh、Source Skill、Source scriptへ問い合わせない。既存の`japanese-tech-writing`、`balanced-tech-writing`、`cognitive-rhythm-writing`にもruntime依存しない。
