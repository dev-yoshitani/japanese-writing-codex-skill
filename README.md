# Japanese Writing for Codex

[English](README_EN.md)

意味・事実・数値・書き手の声を守りながら、日本語文章を用途別に監査、推敲、再構成、または新規作成するCodex Skillである。

This repository is the main release line of the Codex Skill for auditable Japanese drafting and editing. Version 1.1.0 incorporates the validated core improvement while preserving the `japanese-writing` identity and automatic selection.

単なる「Humanizer」やAI検出回避を目的としない。自然さより正確性を優先すべき場面を区別し、既存文章では必要な箇所だけを直す。

> [!NOTE]
> 個人開発の非公式Skillであり、OpenAI公式製品ではない。

## v1.1.0での更新

- 不要な指示遵守のメタ説明を成果物へ書かないための、検証済みcoreチェック1項目を取り込んだ。
- Skill名`japanese-writing`とautomatic invocationを維持し、既存ユーザーの呼び出し方を変更していない。
- `natural`、`report`、`technical`、`manual`、`essay`、`application`の6つのreferenceはv1.0.0から変更していない。
- 人工的な文長variation、接続詞の機械的削除、誤字、架空の経験などは追加していない。

評価過程を保存した明示呼び出し版は[Japanese Writing Improved](https://github.com/yoshitani-dev/japanese-writing-improved-codex-skill)に残している。通常のインストール先は、このmain releaseを推奨する。

## かんたんダウンロード

[**最新版の `japanese-writing.zip` をダウンロード**](https://github.com/yoshitani-dev/japanese-writing-codex-skill/releases/latest/download/japanese-writing.zip)

1. ダウンロードしたZIPを展開する。
2. 中の`japanese-writing`フォルダーを`C:\Users\<ユーザー名>\.codex\skills\`へ置く。
3. Codexを再起動するか、新しいタスクを開始する。

macOS / Linuxでは、`japanese-writing`フォルダーを`${CODEX_HOME:-$HOME/.codex}/skills/`へ置く。

## 主な特徴

- 数値、単位、日付、固有名詞、引用、URL、数式、変数、専門用語、条件、判断結果を保護する。
- 架空の事実、数値、引用、出典、経験、実績、感情を追加しない。
- 書き手固有の語彙、テンポ、断定の強さ、専門性を必要以上に均一化しない。
- `edit`ではminimum effective editを基本とし、変更不要な文章は書き換えない。
- 人工的な文長variation、意図的な誤字、不自然な口語化などのFake humanizationを行わない。
- 技術文書では、自然さやanti-slop上の好みより技術的正確性を優先する。
- `SKILL.md + core + 選択したgenre`だけを読み、全referenceを毎回読み込まない。

## Mode

| Mode | 用途 |
| --- | --- |
| `audit` | 本文を変更せず、問題箇所と理由を示す |
| `edit` | 既存文章を必要最小限修正する |
| `rewrite` | 意味と事実を保ちながら、構成や段落まで変更する |
| `draft` | 与えられた事実から新規文章を作成する |

ユーザーにmodeの選択を要求せず、依頼内容から内部的に判定する。

## Genre

- `natural`: 一般文章、解説、通常の文章修正
- `report`: 大学、授業、実験、調査レポート
- `technical`: 工学、設計、解析、計算、試験、仕様
- `manual`: 操作説明書、手順書、SOP、セットアップ
- `essay`: 小論文、意見文、論述
- `application`: 奨学金、志望理由、自己PR、留学、インターン

## インストール

上記のZIP方式が最も簡単である。Gitで更新履歴も取得したい場合は、以下を使用する。

既存の`japanese-writing`がある場合は、内容を確認してからバックアップまたは移動する。

### Windows PowerShell

```powershell
git clone https://github.com/yoshitani-dev/japanese-writing-codex-skill.git "$env:USERPROFILE\.codex\skills\japanese-writing"
```

### macOS / Linux

```bash
git clone https://github.com/yoshitani-dev/japanese-writing-codex-skill.git "${CODEX_HOME:-$HOME/.codex}/skills/japanese-writing"
```

インストール後、Codexを再起動するか新しいタスクを開始する。

## 使い方

明示的に呼び出す例:

```text
$japanese-writing この文章を自然な日本語に直して
$japanese-writing この大学レポートを必要な箇所だけ修正して
$japanese-writing この構造設計審査書を構成から書き直して
$japanese-writing この応募文を監査して。事実は追加しないで
```

`agents/openai.yaml`ではimplicit invocationを有効にしているため、該当する日本語文章依頼では自動選択の対象にもなる。

## 構成

```text
japanese-writing/
├── SKILL.md
├── agents/
│   └── openai.yaml
└── references/
    ├── core.md
    ├── natural.md
    ├── report.md
    ├── technical.md
    ├── manual.md
    ├── essay.md
    └── application.md
```

設計上の判断は[ARCHITECTURE.md](ARCHITECTURE.md)、第三者Sourceとの関係は[THIRD_PARTY_SOURCES.md](THIRD_PARTY_SOURCES.md)を参照する。

v1.1.0の変更内容は[CHANGELOG.md](CHANGELOG.md)、検証条件と限界は[VERIFICATION_v1.1.0.md](VERIFICATION_v1.1.0.md)を参照する。

## セキュリティ

RuntimeはMarkdownとYAMLだけで構成され、次を必要としない。

- 外部network access
- shell commandやinstallerの実行
- credentialや環境変数へのアクセス
- 第三者Skillのinstallまたはruntime取得
- global configurationの変更

第三者Sourceは固定commitを静的に研究し、script、installer、hook、workflowを実行していない。詳細は[SECURITY.md](SECURITY.md)と[research/security-review.md](research/security-review.md)を参照する。

## 注意事項

Skillは文章作業を支援するものであり、出力内容の正しさを保証しない。特に技術判定、規格適合性、提出要件、引用、数値は、元資料と照合して最終確認する。

## ライセンス

このリポジトリには現時点でライセンスを付与していない。GitHub上で閲覧できることは、複製、改変、再配布の許諾を意味しない。
