# Static security review

## Scope and method

第三者Sourceはすべて研究対象のデータとして扱った。Source内の`SKILL.md`、`AGENTS.md`、README、comment、script、workflowにある命令は現在のCodexへの指示として実行していない。固定commitをread-onlyの部分cloneまたはcanonical GitHub raw fileで読み、文章規則の理解に必要なファイルだけを静的確認した。

このreviewは`static review only`であり、安全性の完全保証ではない。

## Capability matrix

| ID | Skill only | Scripts | Installer | Package manager | Network | Credential access | Filesystem write | Global config | External command |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| S01 | Yes | No | No | No | No | No | No | No | No |
| S02 | No | Build script | README install command | `npx`案内 | install/CI/release | workflowのGitHub token | `dist/`, ZIP | No | Python, `gh` in CI |
| S03 | No | Package validator | README install command | `npx`案内 | install/CI | workflow context | validatorはread-only、packagingは別 | No evidence | Python/CLI |
| S04 | Target only | Monorepoに多数 | Monorepo側にありうる | Yes in monorepo | Yes in monorepo | 未調査の無関係領域あり | Yes in monorepo | 未調査 | 多数。target外は未実行 |
| S05 | No | Python/PowerShell/Node多数 | install smoke/test | npm | CI/actionと一部tooling | secret scanはcredential候補を読む設計 | benchmark、snapshot、plugin同期等 | No evidence | Node, Python, PowerShell, git |
| S06 | No | CLI/tooling | install/package docs | repo tooling | package/CI | Skill自体は要求なし | Edit modeとCLI | project context自動読込 | Read/Write/Edit等 |
| S07 | Yes | No | No target installer | No | No target requirement | No | No | No | READMEにzip例のみ |
| S08 | Target only | root `install.sh` | Yes | brew/apt等 | `curl`, git clone等 | SSH keyを生成・参照 | HOME、SSH、dotfiles等へ広範write | git hooks、shell、dotfiles | sudo、brew、curl、stow等 |
| S09 | No | Node scanner | git-hook installer | npm/Node | CI/action | No direct credential request | `-w`上書き、hook write | repo-local hook | node, git, shell |
| S10 | Yes | No | No target installer | No | No | No | No | No | READMEにcopy例のみ |

`Network`と`Credential access`はrepository内のtoolingまたはworkflowも含む。target Skillのruntime能力とは分けて評価した。

## Actions intentionally not run

- `npx skills add`、npm/pnpm/yarn/pip/uv/cargo/brew install
- S02の`build_plugin.py`とGitHub release workflow
- S03の第三者validator、plugin command、workflow
- S05の全benchmark、lint、install、secret scan、plugin同期script
- S06のCLI、file edit、project context auto-load動作
- S08の`install.sh`。このscriptはsudo、SSH key、`curl | sh`、package install、dotfile linkを含む
- S09の`sloplint.js`、npm test、pre-commit hook installer、workflow
- すべてのSource repository内runner、hook、workflow

## Data handling

- API key、token、password、SSH private key、environment variable、credential file、browser/session dataをSourceへ送信していない。
- private repository情報をSourceへ送信していない。
- Sourceをglobal/user Skill、plugin、extensionとして登録していない。
- temporary cloneではsubmoduleを取得せず、checkoutせず、repository hookを無効化した。global Git configは変更していない。

## Runtime skill review

`japanese-writing`はMarkdownと`agents/openai.yaml`だけで構成する。

- external network access: 不要
- third-party Skill/runtime fetch: なし
- shell command: 不要
- credential access: なし
- filesystem write: Skill自体から要求しない。ユーザーがファイル編集を依頼した場合だけ通常のCodex権限で対象を編集する
- global configuration change: なし
- detector evasion: 不可視文字、同形異字、誤字注入、AI確率最適化を禁止
