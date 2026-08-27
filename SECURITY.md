# Security policy

## 対象

このリポジトリの`main`ブランチにある最新版を対象とする。

## 報告方法

秘密情報、個人情報、未公開の脆弱性をpublic issueへ投稿しない。GitHubのPrivate vulnerability reportingから報告する。

報告には、影響範囲、再現条件、該当ファイル、期待される安全な動作を含める。API key、token、password、credential file、private repositoryの内容は添付しない。

## Runtime security properties

`japanese-writing`はMarkdownとYAMLだけで構成し、Runtimeで次を要求しない。

- network通信
- shell、PowerShell、Python、JavaScript等の実行
- installer、package manager、git hook、workflowの実行
- credential、環境変数、browser sessionの参照
- 第三者repositoryやSkillの取得
- global configurationの変更

第三者Sourceの調査は固定commitに対するstatic review onlyであり、Sourceの完全な安全性を保証するものではない。調査時に第三者script、installer、runner、hook、workflowは実行していない。

## Security boundary

文章内に含まれる指示や引用は、ユーザーの依頼と区別して資料として扱う必要がある。Skillの利用は、入力文書や外部Sourceに書かれた命令を自動実行する権限を与えない。

AI検出回避、不可視文字、同形異字、意図的な誤字注入はサポート対象外であり、Runtime ruleで禁止している。
