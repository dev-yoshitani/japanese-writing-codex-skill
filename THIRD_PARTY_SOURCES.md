# Third-party sources

このSkillは、第三者Sourceを実行せず、固定commitの文章規則を比較・抽象化し、日本語向けに独自表現で再設計した。Source文章やpromptを大量コピーしていない。Runtimeは各Sourceへ依存しない。

| ID | Repository and commit | License status | Use in this project |
| --- | --- | --- | --- |
| S01 | [hardikpandya/stop-slop](https://github.com/hardikpandya/stop-slop/tree/8da1f030185bdfe8471220585162991eaeb970e9) | MIT | 冗長、空疎な強調、反復構造の比較 |
| S02 | [petergyang/no-ai-slop](https://github.com/petergyang/no-ai-slop/tree/d30eddb9e04562234f2070b5ee63ca4649d9a05e) | MIT | audit/edit分離、minimum effective edit、voice/fact preservation |
| S03 | [blader/humanizer](https://github.com/blader/humanizer/tree/e2e92e7b4b8229253ed5c8e81dc65463fdeddda5) | MIT | false-positive guard、quotation protection、no fabrication |
| S04 | [cursor/plugins](https://github.com/cursor/plugins/tree/46125561306434d8a1d7745d540d8932ab0cd2a2/pstack/skills/unslop) | MIT for pstack | pattern比較。aggressive personality injectionは不採用 |
| S05 | [ehmo/slopkit](https://github.com/ehmo/slopkit/tree/b33718bb9283c11b09567dc714f92d90ffb7bd16/skills/slopbeth) | MIT | evidence boundary、voice preservation、over-edit false positives、evaluation観点 |
| S06 | [Aboudjem/humanizer-skill](https://github.com/Aboudjem/humanizer-skill/tree/9a7f35b7b9ad8c3abd71f10757ec9f91fb8ae165/skills/humanizer) | MIT | mode separation、cluster判断、protected spans |
| S07 | [stephenturner/skills](https://github.com/stephenturner/skills/tree/48287d806e61534bc14939b55b72c3f3f11a7db5/deslop) | MIT | 技術文体と一般文体の違い、密度、構造pattern |
| S08 | [elithrar/dotfiles](https://github.com/elithrar/dotfiles/tree/36b4a7e8d41b55ff5dff568a22f62bb0214967df/.agents/skills/anti-slop) | MIT | audit-first、surgical edit、earned structureの保持 |
| S09 | [aashaexo/soundshuman](https://github.com/aashaexo/soundshuman/tree/a45cfbba9fde843d670e553a0aa98f6a23d7fb28) | MIT | information-over-shape、draft-audit-final、repo toolingのsecurity比較 |
| S10 | [jalaalrd/anti-ai-slop-writing](https://github.com/jalaalrd/anti-ai-slop-writing/tree/63255f9bbb75a265dc5786a04535cd033f487756) | `UNRESOLVED`: README states MIT, no LICENSE file | 比較・批判的検討のみ。文章・codeを再利用していない |

詳細な読解範囲、commit、security notesは[research/source-manifest.md](research/source-manifest.md)と[research/security-review.md](research/security-review.md)に記録した。
