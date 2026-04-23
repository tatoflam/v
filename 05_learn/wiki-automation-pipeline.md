---
title: Wiki 自動運用パイプライン
category: 05_learn
tags: [wiki, automation, hooks, github-actions]
sources: [8a25326c-5119-438b-bcf3-4c4c7dba4127]
updated: 2026-04-23
---

# Wiki 自動運用パイプライン

## Summary

Claude Code セッション終了 → wiki への取り込み → GitHub への push までを「日常は何もしない」で回すための構成。LLM 推論が必要な処理（分類）と決定論的な処理（lint）を分け、前者はローカル LLM hook、後者は GH Actions に切り分けた。

## Details

### 構成図

```
セッション終了
  ├─ plugin SessionEnd hook   →  queue.jsonl に enqueue
  └─ user SessionEnd hook     →  claude -p /wiki-ingest → git push
                                 （Claude が分類・diary 追記・コミット）

毎日 09:00 JST
  └─ GitHub Actions           →  Python 純実装の lint
                                 → log.md 追記 → push back
                                 異常時は job fail → メール通知

知りたいとき
  └─ /wiki-query
```

### LLM が必要 / 不要の切り分け

| 処理 | LLM 必要 | 実行場所 |
|---|---|---|
| enqueue | 不要（ただの追記） | plugin の shell hook |
| `/wiki-ingest`（分類・要約・ページマージ） | **必要** | ユーザ側 hook 内で `claude -p` |
| `/wiki-lint`（健康診断） | 不要（正規表現・frontmatter パース・リンク解決のみ） | GH Actions 上の Python |
| `/wiki-query` | 必要かつユーザ起点 | 手動 |

`/wiki-lint` を CI に切り出した最大の理由は **Anthropic API キーすら不要** な決定論処理だから。これによりローカル resource を消費せず、cron も GitHub 側に任せられる。

### ユーザ側 hook の実装ポイント

`~/.claude/wiki/hooks/auto-ingest-push.sh`：
- `WIKI_INGEST_WORKER=1` で再帰防止（[[claude-code-hooks]] 参照）
- `claude --dangerously-skip-permissions -p "/claude-wiki:wiki-ingest"` でヘッドレス実行
- 完了後 `git -C $VAULT push`
- バックグラウンド化（`( ... ) &; disown`）してフックは即 return

### CI の実装ポイント

`.github/workflows/wiki-lint.yml` + `.github/scripts/wiki-lint.py`：
- `cron: '0 0 * * *'` UTC = 毎日 09:00 JST
- contradictions / broken-links 検出時は exit 非 0 → GitHub からメール通知
- `log.md` 追記後の自動 commit は `[skip ci]` で push、self-trigger ループを防ぐ
- 並列実行衝突対策：concurrency group + push 前 pull --rebase fallback

### 残る手動オペレーション

- `~/.claude/settings.json` への hook 登録 と `chmod +x` は、Claude 自身からは permission ガードで止められやすいので、ユーザ側で 1 回叩く

## Links

- [[claude-code-hooks]] — フック挙動の詳細
- [[ssh-agent-shortcuts]] — git push 前の鍵ロード
- [[06_output/2026-04]] — vault と plugin の GitHub アーティファクト
- [[02_diary/2026-04-23]]
