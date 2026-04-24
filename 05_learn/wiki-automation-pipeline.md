---
title: Wiki 自動運用パイプライン
category: 05_learn
tags: [wiki, automation, hooks, github-actions, topic:wiki-system]
sources: [8a25326c-5119-438b-bcf3-4c4c7dba4127, a974a8f6-c56d-4b5f-9064-3ab8884ee7d8, 03859554-98cc-4d1a-b62e-212103596b54, 949188fb-38df-403c-8b5a-d1d560de74f0, 6711184a-25c9-4cb4-9566-2c041aeb955b]
updated: 2026-04-25
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

### 並走 /wiki-ingest の race（2026-04-24 実例）

重めのセッション（`bab023ec`）直後に SessionEnd hook が 3 回連続で fire し、3 本の `/wiki-ingest` が同じキューに対して並列に走るケースを観測（`a974a8f6` / `03859554` / `949188fb`、enqueue 間隔 1-2 分）。観測結果:

- **データ破損はしない**: 最速セッションがメインの ingest コミットを打ち、残りは「既にページ更新済み」を検知してほぼ no-op。Idempotency（cursors.json ＋ ingest-log.jsonl ＋ Edit による差分ベース書き込み）が効いている
- **git push failed がログに積まれる**: 複数セッションがほぼ同時に `git push` を試み、後続が non-fast-forward で reject される。`~/.claude/wiki/state/hook-errors.log` に `git push failed in ...` が並ぶ
- **最終解消はユーザの手動 push**: 連続 reject の後、ユーザが明示的に push してようやく同期
- **未採番セッション**: /wiki-ingest 自身が SessionEnd 時にさらにキューへ enqueue されるので、次の /wiki-ingest で拾われる。上限は見かけないので暴走リスクはあるが、現状は自己収束

対策候補（未実装）:
- hook 側で **flock** による exclusive lock（`~/.claude/wiki/state/ingest.lock`）
- push 前の `git pull --rebase --autostash` fallback
- キューが空の時の early exit（現在は空でも meta 処理だけ走る）

### エディタ ↔ hook の編集レース（2026-04-24 実例 → 2026-04-25 対策済み）

上記の並走 race とは別カテゴリの競合。ユーザが Obsidian で `02_diary/2026-04-24.md` を live-edit 中に別セッション終了 → hook の `/wiki-ingest` が同ファイルに `## 18:01` 節と frontmatter を append + commit + push。その後エディタがメモリ上の stale buffer で保存 → hook 側の追記が working copy から消える退行。`git diff` で sources から uuid が消え `updated` が前日に戻り `## 18:01` 節が丸ごと欠けた。

**何が失われるかと復旧**:
- git 履歴には残っているのでデータロスはなし
- working copy のみ退行 → HEAD 版を基準にユーザー加筆分だけ Edit で再適用（`git checkout --` は destructive ガードで止まる想定で、そもそも避ける）

**対策（実装済、plugin commit `43d96ef`）**: **dirty-target gate** — 書き込み対象ファイルごとに `git status --porcelain <path>` を実行し、working copy が汚れていればそのセッションを queue に戻して deferred、`hook-errors.log` に `skip=dirty_working_copy  files=[...]` を記録。次回 ingest で自動リトライ。meta ファイル（`log.md` / `index.md` / `_schema.md`）は skill 所有なのでチェック対象外。`/wiki-ingest` のレポートに `Deferred (dirty working copy): <D>` 行を追加。

**採用しなかった代案**:
- B: ステージングファイル（`02_diary/YYYY-MM-DD.ingest.md`）へ書いて後でマージ — 2 ファイル分裂とマージ工程が要るので複雑
- C: ingest 中 lockfile で push 遅延 — エディタ側上書きを防げないので根本治療にならず
- D: Obsidian 側で外部変更を reload — プラグイン依存で汎用性なし

副作用: ユーザが diary を開きっぱなしのまま次のセッションを閉じると deferred になり、明示的に Obsidian 側で保存＆エディタから離れる（clean 化）まで反映が保留される。queue は永続化されているので情報は失われない。

### Tag taxonomy（2026-04-25 導入）

プレフィックス付きタグで Obsidian のタグペインが facet として機能するようにした。schema.md §"Tag taxonomy" に定義、`/wiki-ingest` で新規作成ページに付与、`/wiki-lint` で compliance チェック。

**Primary tag（必須・カテゴリ別 1 個）**:

| Category   | 形式                  | 例 |
|------------|---------------------|----|
| 00_self    | `aspect:<slug>`     | `aspect:profile`, `aspect:values`, `aspect:goals` |
| 03_work    | `project:<slug>`    | `project:meguru-pm-report`, `project:yahatayama-rokujizo` |
| 04_life    | `domain:<slug>`     | `domain:house`, `domain:finance`, `domain:family` |
| 05_learn   | `topic:<slug>`      | `topic:claude-code`, `topic:google-sheets`, `topic:wiki-system` |
| 06_output  | `channel:<slug>`    | `channel:github`, `channel:gmail`, `channel:drive` |
| 07_archive | 元タグ継承 + `status:archived` + `archived:<YYYY-MM-DD>` | |

**Secondary（任意・複数可）**: `tech:<slug>`, `stage:<slug>`, `client:<slug>`, `entity:<slug>`, `status:<slug>`。

**Grandfathering**: 既存の bare tag（`meguruit`, `python` 等）は update 時に**上書きせず**primary tag を並べて追加。`/wiki-lint` は primary tag 欠落ページを `## Non-compliant tags (<N>)` で報告するのみ、自動修正はしない。

Slug 規則: lowercase, hyphen-separated, singular, reuse before invent。

## Links

- [[claude-code-hooks]] — フック挙動の詳細
- [[ssh-agent-shortcuts]] — git push 前の鍵ロード
- [[06_output/2026-04]] — vault と plugin の GitHub アーティファクト
- [[02_diary/2026-04-23]]
- [[02_diary/2026-04-24]] — 並走3本の race 実例
- [[02_diary/2026-04-25]] — dirty-target gate + tag taxonomy 実装
