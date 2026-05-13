---
title: Wiki 自動運用パイプライン
category: 05_learn
tags: [wiki, automation, hooks, github-actions, topic:wiki-system]
sources: [8a25326c-5119-438b-bcf3-4c4c7dba4127, a974a8f6-c56d-4b5f-9064-3ab8884ee7d8, 03859554-98cc-4d1a-b62e-212103596b54, 949188fb-38df-403c-8b5a-d1d560de74f0, 6711184a-25c9-4cb4-9566-2c041aeb955b, 5a969394-b6e8-4550-aa00-4ea7dbd77df8, 023f317a-a958-4f56-ad10-efcf22773aba, 536fc370-29c5-41fc-9eb0-69219ed653ad, 663d418d-e50e-4fab-9865-243d8963e0aa, dc9a7e40-43ae-4e27-a21f-645777ba320c, 6f7fbba7-fca3-49cc-b8e4-061a3aaf9959, ffb55997-2783-45e8-a8ca-0538e3667bf2]
updated: 2026-05-13
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

## 病理学 — auto-worker zombie ＋ duplicate-write race ＋ 18 サイクル defer の 3 系統（2026-05-02 → 05-03 観察）

5-2 朝〜5-3 朝の 9 連続 yield と最終 drain（commit `d6c64ad` ＋ 事後 cleanup `efd00e2`）で観察した、並走 ingest の病理を 3 系統に分けて整理。

### 病理 1 — auto-worker zombie が remote diverge で stuck retry

**症状**: 18 並行 auto-worker（PIDs 28514/28551/30116/30118/30120/31857 系、etime 9-12 分）が `git push` 失敗で stuck retry ループ。HEAD は `8538d57` から動かないのに queue は 27 → 30 と増加し続ける。`cursors.json` / `ingest-log.jsonl` も May 1 07:08 で更新止まり。SessionEnd hook が新 worker を spawn し続けるので worker pile up が止まらない。

**復旧手順**:

```bash
# 1. worker 全滅
pkill -f 'auto-ingest-push.sh'
pkill -f 'claude.*wiki-ingest'

# 2. remote と同期
cd ~/repo/github/tatoflam/v
git pull --rebase

# 3. duplicate ファイル手動統合（病理 2 参照）

# 4. 長期 WIP は commit/discard を強制（病理 3 参照）

# 5. 再 ingest で cursors/queue を自動 reconcile
claude --dangerously-skip-permissions -p "/claude-wiki:wiki-ingest"
```

**根本治療候補（未実装）**: `auto-ingest-push.sh` 側で `git push` 失敗時の **fail-fast + ロックファイル即時開放** を入れて、後続 worker が retry を肩代わりしないようにする。`ingest.lock` の `flock` で 1 worker / 5 分の上限を強制するのも効く。

### 病理 2 — 同セッションを別ファイル名で生成する duplicate-write race

**症状**: 同 `da24ce6d` セッションから 2 worker が **`apartment-garbage-stocker-shortlist.md` と `apartment-gomi-stocker-sizing.md` の 2 ファイル**を別名で並行生成。同様に `vercel-path-to-regexp.md` (auto-worker A 版) と `vercel-path-to-regexp-v6.md` (auto-worker B 版) の near-duplicate も発生（後者が Team scope + repo transfer まで含む superior 内容で canonical 採用）。

**事後 cleanup の定型**（commit `efd00e2` を参考）:

```bash
# 1. duplicate 検出（/wiki-lint で near-duplicate slug を検出）
/wiki-lint

# 2. canonical 判定（より thorough な内容のものを採用）

# 3. git rm 重複 + sed -i '' でリンク全置換
git rm 05_learn/vercel-path-to-regexp.md
sed -i '' 's|\[\[vercel-path-to-regexp\]\]|[[vercel-path-to-regexp-v6]]|g' \
  02_diary/2026-05-01.md \
  05_learn/specdrawing-material-presenter.md \
  06_output/2026-05.md \
  index.md

# 4. hallucinated narrative 検出 + 訂正
#    （auto-worker が推測で書いた内容を正しい narrative に置換）

# 5. index.md の重複 entry も dedupe
```

**予防策（未実装）**: ingest 開始時に **session_id をキー**として「このセッションが既に touch したファイル」を `~/.claude/wiki/state/in-flight.json` に記録、別 worker が同 session を扱おうとしたら yield。

### 病理 3 — user の Obsidian live-edit による 18 サイクル defer

**症状**: 同じ 6 sessions（84dd308c → woodone, 832016a3 / c08d4720 / f75e4e61 / 385eff5c → sayama, d030ba7d → sayama + saltmoon）が **18 営業日連続**で deferred のまま。原因は user が Obsidian 上でこれら 3 ファイル（`04_life/sayama-land-contract.md` M, `04_life/saltmoon-llc-operations.md` ??, `05_learn/woodone-pboard-architecture.md` ??）を live-edit したまま commit しないこと。dirty-target gate が機能しているので破壊は起きないが、関連 session の取り込みが永続的にブロックされる。

**user 側の解消手順**:

1. Obsidian で当該 3 ファイルの編集を一段落させる
2. ターミナルで commit:
   ```bash
   cd ~/repo/github/tatoflam/v
   git add 04_life/sayama-land-contract.md 04_life/saltmoon-llc-operations.md 05_learn/woodone-pboard-architecture.md
   git commit -m "wip: snapshot sayama / saltmoon / woodone live-edits"
   ```
3. 次回 `/wiki-ingest` で 6 sessions が drain される

**自動化の限界**: skill 側からは「user がエディタを開いている」かは検知できない（mtime と git status だけが手がかり）。**ingest レポートに `Deferred (dirty working copy): N` を必ず表示**し、user に「commit してください」を継続的にリマインドするのが現状の最善。

### 5-3 race cleanup commit 構造（参考）

```
d6c64ad ingest: 9 sessions + 0 inbox, 11 pages touched (drained 18-session backlog; defer-gate 18th)
↓ 並走 manual run + auto-worker が同時収束
efd00e2 ingest cleanup: dedupe vercel-path-to-regexp + fix hallucinated 0a7a9e22 narrative
```

`d6c64ad` で書込みが成立し、`efd00e2` で重複 page と hallucination を後始末する 2 段階が、並走時の典型パターン。

### 病理 4 — cron / launchd 環境での `claude` 認証切れ（2026-05-12 観察）

**症状**: 5-12 14:31 / 14:35 / 14:38 JST に 7 cwd 横断で `~/.claude/wiki/hooks/auto-ingest-push.sh` 起動。全 7 sessions の assistant 第 1 ターンが **`Not logged in · Please run /login` 固定文字列のみ**で終了、tool call ゼロ・vault 書き込みゼロ。session ファイルは 20KB 級の「プロンプト受信 + 拒否応答」だけが残る。

**原因推定**:

- macOS launchd / cron 経由で `claude` バイナリを叩くと、ユーザー対話シェルとは異なる環境変数 / keychain アクセス権で起動する
- anthropic CLI の認証トークンは keychain 保管。launchd context では keychain unlock 状態でないため、認証ロードに失敗 → 「Not logged in」固定応答
- 手動 invoke (`claude -p /claude-wiki:wiki-ingest`) では問題なし — keychain unlocked な対話セッションで起動するため

**queue への影響**: 7 sessions が `processed=false` で滞留 → 翌日の手動 drain で「cursor 0 → EOF flip、no-op clear」する必要が生じる。コンテンツ書き込みはゼロなので破壊は起きないが、queue ノイズが蓄積する。

**予防策（未実装）**:

- `auto-ingest-push.sh` 冒頭で `claude --version` 系の軽量コマンドで login 状態を pre-check
- 失敗時は queue に enqueue 自体をスキップ（hook-errors.log に `skip=auth_missing` で記録）
- もしくは launchd plist に `keychain unlock` フックを仕込む（user パスワード平文保存になるので非推奨）

**検出方法**: 同日内に 5+ cwd 横断で同一秒台の `Not logged in` session が発生していたら本病理。`grep -l "Not logged in" ~/.claude/projects/**/*.jsonl | xargs ls -la` で日付クラスタを目視。

### 病理 5 — auto-worker dead residue（untracked diary file、2026-05-13 観察）

**症状**: auto-worker が `02_diary/YYYY-MM-DD.md` を新規作成して書き込み始めたが、cursor / queue 更新前に死亡 → vault working copy に **frontmatter 欠落の untracked diary file** が残る。後続 ingest run の dirty-target gate が「user 編集か dead residue か」判定できずに defer 連鎖を起こすリスク。

**判定基準**（手作業）:

- frontmatter (`---` ブロック) 欠落 → dead residue 確度高
- 該当 session の transcript file が `~/.claude/projects/` から消えている → dead 確定
- 文面が `/wiki-ingest` の典型 output パターン（`session: <id>  cwd: <leaf>`、`queue contained N` 等）→ residue
- 上記が揃えば手動 invoke で上書き finalize して良い

**5-13 ケース**: `d4c85561` (habi-bff cwd) が 15:56:34 JST 起動 → 02_diary/2026-05-13.md を frontmatter 抜きで書いた直後に死亡（transcript missing）→ 同日 16:xx JST の手動 drain で上書き完成 + git add で tracked 化。
