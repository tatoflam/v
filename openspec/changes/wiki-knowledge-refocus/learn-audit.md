# 05_learn 構造監査（stable headings = topics / 経緯 quarantine）

監査日: 2026-07-08。対象 38 ページ。原則: 見出しはトピックで安定させ、時系列は `## 経緯` / `### 観察ログ` に隔離する。

- **(a) curated**: トピック見出しで安定した構造 — そのままで OK
- **(b) single-session capture**: 単発の gotcha/知見 — そのままで OK（統合候補は note に記載）
- **(c) time-appended silo**: 日付見出し・時系列追記で成長 — 再構成が必要

| page | class | note |
|---|---|---|
| ac-energy-saving-regulation.md | a | 法制度・閾値・提言のトピック構造。「めぐる向けレポート (2026-05-15)」は日付付きだが単一のまとまったレポート節で許容。residential-ventilation と同じ HVAC 領域（弱い統合候補） |
| anthropic-tool-use-max-tokens-empty-input.md | b | 単発シグネチャ知見。トピック見出しで安定 |
| apartment-gomi-stocker-sizing.md | b | 単発調査（狭山物件）。Summary/Details で安定 |
| aws-profile-account-hlab-mfa.md | b | 単発インシデント分析。安定 |
| claude-code-hooks.md | a | hooks 挙動のリファレンス。→ 統合候補グループ 1 の受け皿候補 |
| claude-code-plugin-namespace.md | b | 単発 gotcha。→ claude-code-session-resume と共に claude-code-hooks（または新設 claude-code-tips）へ統合候補 |
| claude-code-session-resume.md | b | 単発リファレンス。→ 同上（統合候補グループ 1） |
| external-planning-docs-observability-framing.md | b | 単発の planning 原則。安定 |
| fy-cycle-mmdd-year-inference.md | b | 単発ロジック知見。→ Google Sheets グループ（グループ 2）と弱い統合候補 |
| gmail-mcp-reauth.md | b | 単発手順。→ gmail-search-threads-message-limit と「Gmail MCP 運用 gotchas」へ統合候補（グループ 3） |
| gmail-search-threads-message-limit.md | b | 単発 API 制約。→ 同上（グループ 3） |
| google-sheets-image-excel-compat.md | b | 単発 gotcha。→ google-sheets-multi-row-header と「Google Sheets gotchas」へ統合候補（グループ 2） |
| google-sheets-multi-row-header.md | b | 単発 API 対応パターン。→ 同上（グループ 2） |
| habi-bff-pmchat-localdev-gap.md | b | 単発の構造ギャップ分析。安定 |
| honeypot-autofill-antipattern.md | b | 単発 anti-pattern。安定 |
| instagram-multi-account-isolation.md | a | 4 軸 boundaries のトピック構造。threads-scrape-tos と fingerprint 論点が重なる（弱い統合候補、相互リンクで足りる） |
| jooto-checklist-items-separate-endpoint.md | b | 単発 API 特異点。安定 |
| local-first-anthropic-ops.md | a | 原則 1〜8 のトピック構造。§8 のみ日付付きだが Details 内で許容 |
| mermaid-dotted-edge-label-syntax.md | b | 単発 syntax gotcha。安定 |
| metsushitsu-touki-kihon.md | a | 制度リファレンス。安定 |
| milestone-yaml-comment-out-behavior.md | b | 単発挙動整理。「2026-06-05 実測」は観察ログ 1 節で許容 |
| openspec-retroactive-flow.md | a | 5 ステップのワークフロー構造。安定 |
| persona-driven-content-rules.md | **c** | **再構成済**。末尾に 2026-05-07 追補 / 05-16 改訂×3 / 07-07 追補が時系列追記され、「うち」採用→撤回の変遷が現行ルールと混在していた → 現行ルールをトピック見出しに集約し変遷を `## 経緯` へ |
| php-local-lint.md | b | 単発手順。安定 |
| rakuten-dashboard-shorturl.md | **c** | **再構成済**（軽度）。`## Links` の後に「⚠️ 旧 RWS API 停止（2026-05-07 追加）」が追記されていた → RWS API 移行のトピック節に統合し Links を末尾へ |
| reins-headlesschrome-ua-block.md | b | 単発 WAF gotcha。honeypot-autofill と同じ bot 判定領域だが対象が別で統合不要 |
| residential-ventilation-negative-pressure.md | b | 単発設計知見。→ ac-energy-saving と HVAC で弱い統合候補 |
| specdrawing-material-presenter.md | **c** | **再構成済**。`## 2026-04-27` 〜 `## 2026-05-03` の日付見出し 6 本（うち 2 本は Links の後）で成長した典型的 silo → 合成パイプライン / スキーマ / dev-trace / デプロイ等のトピック見出しに再編、タイムラインは `## 経緯` へ |
| ssh-agent-shortcuts.md | b | 単発運用メモ。安定 |
| threads-engagement-rotation-pattern.md | b | 単発事例分析（沼子。）。→ persona-driven-content-rules と文体・運用論点が近い（グループ 4） |
| threads-graph-api-setup.md | **c** | **再構成済**。`## 7 (2026-05-03 追加)` / `## 8 (2026-05-07 追加)` が Links の後に追記されていた → ID 対応表・現行 UI 経路・token 運用・env 配置をトピック見出しに再編、UI 変遷は `## 経緯` へ |
| threads-scrape-tos.md | a | 三重判定のトピック構造。安定 |
| todobot-line-mvp.md | **c** | **再構成済**。「メール送信方式の変更 (2026-05-21)」「@mention 解決の修正 (2026-05-21)」「実装進捗 (2026-05-11 時点)」の時系列追記 → メール送信 / 抽出 / 実装スペック / 運用ドキュメントのトピック見出しに再編、進捗は `## 経緯` へ |
| vercel-path-to-regexp-v6.md | a | 落とし穴 1〜6 のトピック構造。安定 |
| vpoint-olive-vs-platinum-preferred.md | b | 単発比較。安定 |
| wiki-automation-pipeline.md | a | curated・現役メンテ中（指示により対象外） |
| woodone-pboard-architecture.md | a | 調査レポート構造。specdrawing-material-presenter の出発点（相互リンク済、統合不要）。frontmatter が他ページと異なる形式（category/updated なし）— 別課題として注記のみ |
| youtube-knowledge-pipeline.md | a | パイプライン設計のトピック構造。安定 |

**集計**: (a) 11 / (b) 22 / (c) 5

## 統合候補

1. **Claude Code 小ネタ群** — `claude-code-plugin-namespace.md` + `claude-code-session-resume.md` → `claude-code-hooks.md` を「Claude Code 運用知見」に拡張して吸収（または新設 `claude-code-tips.md`）。いずれも短い単発 capture で、参照時は「Claude Code の挙動」として一括で探される
2. **Google Sheets gotchas** — `google-sheets-image-excel-compat.md` + `google-sheets-multi-row-header.md`（+ 弱: `fy-cycle-mmdd-year-inference.md` の日付列パース）→ `google-sheets-gotchas.md` に統合。API/互換性の落とし穴として同一トピック
3. **Gmail MCP 運用** — `gmail-mcp-reauth.md` + `gmail-search-threads-message-limit.md` → `gmail-mcp-operations.md` に統合。どちらも MeguruPMReport 週次フローの Gmail MCP 制約
4. **Threads 運用知見（弱）** — `threads-engagement-rotation-pattern.md` ↔ `persona-driven-content-rules.md` は文体・投稿設計で隣接。当面は相互リンク維持で可、増えるようなら「Threads 投稿設計」に統合
5. **HVAC/住宅設計（弱）** — `ac-energy-saving-regulation.md` ↔ `residential-ventilation-negative-pressure.md`。論点が別（法規制 vs 換気設計）なので統合優先度低、タグ整合のみ
