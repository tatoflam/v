---
title: Gmail MCP `search_threads` のスレッド先頭打ち切り（取りこぼし要因）
category: 05_learn
tags: [topic:gmail-mcp, tech:gmail-api, tech:claude-code, project:meguru-pm-report, stage:active]
sources: [b50d3ddb-d9a6-4539-b43b-5a967748e748]
updated: 2026-05-23
---

# Gmail MCP `search_threads` のスレッド先頭打ち切り（取りこぼし要因）

## Summary

Claude Code 組み込み MCP の `mcp__claude_ai_Gmail__search_threads` は **1 スレッドあたり先頭の数通（実測 ~5 通）しか返さない**。長期間続くスレッド（質疑応答・進捗報告等）では、検索ヒットしたスレッドの **最新メッセージが丸ごと欠落** する。`search_threads` の結果だけで要約する運用は、長スレッドのある業務では **取りこぼし前提** で考えるべき。

## 詳細

### 観測ケース（2026-05-22, MeguruPMReport `/weekly-report`）

- 案件「幡ヶ谷本町」の **「【渋谷区幡ヶ谷本町】質疑」スレッドは全 47 通**（5/11 開始、5/21 まで継続中、スレッドサイズ 2.9 MB）
- `search_threads` は **先頭 5 通（5/12 まで）しか返さず**、5/13 以降の 42 通が `/weekly-report` の集計から完全欠落
- 結果: 5/20 仮受当日に発覚した **「天空率・日影規制の不適合 → 建物形状を伴うプラン見直し」** という重大インシデントが初版レポートで未検出
- 山口設計士（k.yamaguchi@that-tokyo.com）からの直近メールは `search_threads` 視点では「5/11 で停止」と見えるが、実際にはスレッド内に最新メッセージが存在

### 根本原因

`search_threads` の API がスレッドのメッセージ全件を展開せず、ヒット判定に必要な先頭部分のみを返す仕様（MCP 側または上流の Gmail API の挙動）。長スレッドでは新着が末尾に追加されるため、**新しいやり取りほど取りこぼしやすい**。

### 回避策（必須運用）

各スレッドを `mcp__claude_ai_Gmail__get_thread` で **全件展開** し、対象期間内のメッセージを 1 通も取りこぼさないことを完了条件とする。コンテキスト節約は

- **期間外メッセージの非展開**
- **引用履歴（`> ...` 行）の非展開**

で行い、**期間内の取りこぼしは許容しない**。

### 検出方法（運用上の sanity check）

- 案件ラベル内で `search_threads` 結果のスレッド数 vs. 各スレッドの実メッセージ数を突合
- 「あるはずのメール」が出てこない指摘（user feedback）があったら、まず該当スレッドを `get_thread` で全件展開して再確認
- 長スレッド（10 通超）は **必ず全件展開** を既定にする

### `/weekly-report` への恒久反映（2026-05-22 適用）

- `.claude/commands/weekly-report.md` — Gmail 検索手順を改訂、`get_thread` 全件展開を完了条件に明記
- `config/workspace_defaults.md` — 「期間内メッセージの全件取得（必須）」節を追加、期間外・引用履歴の非展開でコンテキストを節約する規約を明示

### 横展開の射程

`/weekly-report` 以外でも、Gmail MCP を使うあらゆる定常運用（週次・月次の集計、進捗追跡）で同じハマり方が再現する。**「search_threads の結果だけで要約しない」** は MCP Gmail 全般のベースラインに昇格させるべき。

## Links

- [[03_work/meguru-pm-report]] — 2026-05-22 ラン（本症状の発見ラン）
- [[05_learn/gmail-mcp-reauth]] — Gmail MCP の認証側のハマり所
