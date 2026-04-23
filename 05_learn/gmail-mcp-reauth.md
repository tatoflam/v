---
title: Gmail MCP 再認証（VS Code Claude Code 拡張）
category: 05_learn
tags: [mcp, gmail, claude-code, oauth]
sources: [92ea8970-d8f1-4aa3-aaed-66db645434ca]
updated: 2026-04-24
---

# Gmail MCP 再認証（VS Code Claude Code 拡張）

## Summary

Claude Code 組み込みの「claude.ai Gmail」MCP はトークン期限切れで失効する。週次レポート処理などで Gmail 検索が全件エラーになったら再認証が必要。Claude 自身は再認証できないため、ユーザ側で `/mcp` → Reauthenticate を実行する。**OAuth で選ぶ Google アカウントは「読みたい Gmail」（＝仕事用）であって Claude.ai ログイン用アカウントとは別物**、というのが最大のハマりどころ。

## 手順

1. Claude Code パネルで `/mcp` を実行
2. 接続済み MCP サーバー一覧から `claude.ai Gmail` を探す（ステータスが `expired` / `needs auth`）
3. サーバーを選択し **Reauthenticate** / **Reconnect**
4. ブラウザで Google OAuth 同意画面 → **目的の Gmail アカウントを選択**（複数アカウント併用時は誤選択に注意）
5. 許可すると VS Code に戻りトークン更新

### ブラウザが開かない / コールバック失敗時

- ターミナルで `claude mcp list` で状態確認
- `claude mcp` の対話メニューから再接続

### それでも直らない場合

- claude.ai にブラウザでログイン → Settings → **Connectors / Integrations** → Gmail を一度切断 → 再接続
- VS Code を再読み込み（コマンドパレット: `Developer: Reload Window`）

## アカウントの切り分け（重要）

| 役割 | アカウント例 |
|---|---|
| Claude.ai プラットフォーム ログイン | 個人アカウント（例: `tato.flam@gmail.com`） |
| Gmail MCP の OAuth 対象 | **読みたいラベルが入っている Gmail**（週次レポートなら仕事用アカウント） |

- 前回成功時のラベル（`label:案件-01.高円寺南5丁目` など）を再現したければ **そのラベルが存在する Gmail アカウント**で OAuth を通す
- 違うアカウントで認証してしまうと「該当スレッドなし」で静かに失敗する（エラーにならない）→ 症状から再認証が必要と気付きにくい
- 復旧: claude.ai の Settings → Connectors → Gmail を切断してから正しいアカウントで再接続

## MeguruPMReport の週次フローとの関連

- `/weekly-report` の Batch 実行中に Gmail MCP が失効すると **すべての案件で「Gmail 更新なし」扱い**になり、レポートが嘘をつく
- 失効検知: `mcp__claude_ai_Gmail__search_threads` がトークンエラーを返した時点で一旦停止し、ユーザに再認証を依頼するのが安全
- 再開時はユーザが「最新のレポートを作って」を再発話すれば、Jooto 側は最新（当日の `/jooto-backup --force` 結果）のまま Gmail から再取得できる

## Links

- [[03_work/meguru-pm-report]]
- [[05_learn/claude-code-hooks]]
