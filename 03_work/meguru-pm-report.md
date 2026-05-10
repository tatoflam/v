---
title: MeguruPMReport
category: 03_work
tags: [meguruit, jooto, weekly-report, python, google-sheets, project:meguru-pm-report, client:meguru, tech:python, tech:google-sheets, stage:active]
sources: [3e07de94-4eea-46b3-892a-e815cd133f4e, 92ea8970-d8f1-4aa3-aaed-66db645434ca, bab023ec-53ee-4301-869d-306222b4a3f8, 002f63f9-be02-4b79-acd5-3f0f1b1ea354, 0e835096-fe82-4b7c-9127-a91d45d19520, a78e0aaa-c07f-4a30-bc50-8bec60ab1b1c, d87e347c-74eb-4770-bb1b-9b8ac0c9e386, 552ceb4f-7b74-492d-b829-616f7d6da38b, 61d82ae6-e969-4ebb-a4d1-d5174c250de1]
updated: 2026-05-11
---

# MeguruPMReport

## Summary

Meguru 案件の **週次アップデート** を Gmail と Jooto から Claude Code 上で生成するワークスペース。仕様の SoT は `openspec/specs/`、スラッシュコマンドは `/weekly-report` と vendored plugin `jooto-grabber/`。

## Details

### リポジトリ
- ローカル: `/Users/tato/repo/github/meguruit/MeguruPMReport`
- リモート: `git@github.com:meguruit/MeguruPMReport.git`（2026-04-24 に初push、main 直 push は初回のみ承認で通した）

### 典型ワークフロー
```
/jooto-backup --all-active       # 差分同期
/jooto-overdue-scan              # 期日超過の深掘り源泉
/weekly-report                   # 週次レポート生成
```

### Python 環境（plugins/jooto-grabber）
- **Python 3.10.11**（`.python-version` で pyenv に指示、`.gitignore` 対象なのでコミットされない）
- **venv**: `plugins/jooto-grabber/.venv`（editable install + dev extras）
- 旧ワークスペース（`tatoflam/...`）から vendor-in した際に venv パスが破損するので、`python -m venv --clear .venv` で作り直す
- pytest 54 件（2026-04-24 時点）

### 運用ルール（CLAUDE.md 抜粋）
- Gmail は **厳格 read-only**：`search_threads` / `get_thread` のみ、送信・下書き・ラベル操作禁止
- Jooto も read-only、コメント/チェックリスト取得は期日超過タスクに限定（コスト抑制）
- 変更は **OpenSpec change 起票が先**（`/opsx:propose`）、コード先行禁止
- 元リポジトリ（Plugins-Bizuayeu/JootoGrabber）と元ワークスペース（ClaudeWork/MeguruPM）は編集禁止

### Git push の前提
- `. ~/sshgl;` を **同一 Bash 呼び出し**で連結してから `git push`（2026-04-26 の `df5ce43` / `075077d` push でこの短縮形が Claude Code Bash でも通ると確認）
- 旧手順 `eval \`ssh-agent\`; ssh-add -k ~/.ssh/id_rsa7; ssh-add -k ~/.ssh/github_rsa` は同等だが冗長。`~/sshgl` を source する短縮形が標準
- 主要ブランチへの直接 push は harness ガードで初回拒否される（permission 承認が必要）。feature ブランチ + PR 運用に切り替えるのが本筋
- 詳細: [[05_learn/ssh-agent-shortcuts]]

### `/jooto-backup` の差分同期が取りこぼす条件
- 既定の差分同期は **board.updated_at** を見て全ボードスキップ判定する。タスクレベルの変更（ステータス遷移・コメント追加・期日更新）では board.updated_at が上がらないことがあり、差分同期だと拾えない
- **回避**: `/jooto-backup --all-active --force` で強制再取得。週次レポート前に board 更新イベントが無くても、タスクは動いている想定で `--force` を当てる運用が安全
- 2026-04-24 の `/weekly-report` 実行で発覚（差分同期が 38 ボード全スキップ → `--force` で再取得して中野坂上 S10_躯体積算の新規 overdue を検知）

### Gmail MCP の再認証
- 週次レポート中に Gmail MCP トークンが失効するとバッチ検索が全件エラーになる
- 再認証手順と、Claude.ai ログインアカウントと MCP 対象 Gmail アカウントの違い: [[05_learn/gmail-mcp-reauth]]

### 週次レポート成果物（リポジトリ内）
- `reports/YYYY-MM-DD_weekly_update.md` に格納。前回比較元は `state/latest_summary.md` と `state/latest_state.json`、バッチ進行は `state/batch_progress.json`
- 2026-04-29 版: 上記 `f818fb1 Add 2026-04-29 weekly update and refresh state snapshots` で `075077d..f818fb1  main -> main` push 済（[[06_output/2026-04]]）。Push 手順は `. ~/sshgl; git push` を**同一 Bash 呼び出し**で連結（[[05_learn/ssh-agent-shortcuts]]）。Claude Code は明示「commitして」「push して」が無いと自動 commit/push しない。粒度は「`/weekly-report` 実行→確認→1 commit にまとめる」が定石
- 2026-04-24 版: **新規 overdue = 中野坂上 S10（CC 漏れ起因）**、板橋氷川町/東長崎4丁目/渋谷区本町5丁目/山王3丁目/中野1丁目/西荻北1丁目で大きな前進、高田馬場・東尾久・江古田江原・西巣鴨は停滞継続
- 2026-04-24 vs 0422 版: `diff_against=2026-04-22` ＋ `run_date=2026-04-24_vs_0422` で `reports/2026-04-24_vs_0422_weekly_update.md` を別ファイル出力（今朝の 2026-04-24 版は温存）。2 日差分の主な動きは東長崎4丁目（構造図 CH 4/23 送付）／幡ヶ谷本町（接地圧＋暫定構造図 CH）／幡ヶ谷不動尊通り（ルート 1 申請可能確定・最上階開口斜め壁質疑）／中野坂上（躯体積算完了・S04-2 私道通行掘削許可確認）／中野1丁目（注文者法人化＆再電子署名）／山王3丁目（構造着手当日の意匠図未着＋地盤報告書案件違い疑義）／世田谷大原（パース見積受領＋JWW 共有）
- `/weekly-report diff_against=YYYY-MM-DD` で前回比較元を指定可能。`run_date=YYYY-MM-DD[_suffix]` と組み合わせれば既存レポートを上書きせず別ファイルに書き出せる（`state/latest_*` は常に上書き点注意）
- 24 案件の per-project セクションは **3 並列 subagent** に FY26_01-08 / 09-16 / 17-24 で分割委譲するのが定石（Gmail 検索＋Jooto overdue 照合＋申し送り差分を並行化）

### 意匠設計担当の負荷ビュー（2026-04-25 改修）
- 統合表の日付は `MM/DD` のみで年情報なし。文字列比較では誤判定が出るため、**FY26 設計サイクル＋基準日 today ベースで YYYY-MM-DD に変換**してから並行案件を集計する（設計開始は「過去側に固定」、以降は月減少で +1 年）。汎用ロジック: [[05_learn/fy-cycle-mmdd-year-inference]]
- **日付未設定の案件も並行案件にカウント**（「(日付未設定)」注記付き）。キックオフ前の案件を振り分けられている担当が実態より軽く見えないようにするため
- 2026-04-25 時点の警告対象: **井上 3 件**（祐天寺＋江古田江原＋山王3丁目）／**鈴木 4 件**（うち FY26_22 駒込待ちでスタンバイ扱い）／**加納** 新規登場（FY26_08 高田馬場＋FY26_11 東尾久、両方とも日付未設定）
- 恒久化の follow-up change 候補: `plugins/pm-master-grabber/scripts/domain/pm_master.py` に MM/DD→YYYY-MM-DD 変換ユーティリティを内製し、`integration.json` の rows に変換済み日付を同梱（現状はレポート生成側でアドホック変換）

### PMMasterGrabber プラグイン（2026-04-24 追加、OpenSpec change `add-pm-master-grabber`）
- 意匠設計担当の **負荷ビュー**（複数案件並走度＋評点）と **申し送り差分** を `/weekly-report` に組み込むための新プラグイン
- 対象スプレッドシート: `進捗管理表_master`（ID `1oY9nd8tc55wLvEhqaFksZq-EMKD8GtfUBQRDUKpyBm8`、アカウント `thomma@meguru-construction.com`）
- 3 シート前提: `統合表`（案件基本情報、行=案件）／`申し送り`（更新履歴）／`案件評価`（評点）
- OAuth: Google Cloud Console で **Desktop app** クライアント作成、スコープは `spreadsheets.readonly` のみ。`plugins/pm-master-grabber/credentials.json` と `token.json` は `.gitignore` 済（書き込みスコープは **絶対禁止**、AST guard `test_readonly_guard.py` で担保）
- コマンド: `/PMMasterGrabber:pm-master-auth` ／ `/PMMasterGrabber:pm-master-list-sheets` ／ `/PMMasterGrabber:pm-master-backup`（名前空間注意・[[05_learn/claude-code-plugin-namespace]]）
- バックアップ先: `data/pm_master/{integration,handover,evaluation}.json`（機微情報を含むため `.gitignore` 済、transcript 非出力）
- 実データで確定したスキーマ（design.md の Q1〜Q6 解消済み）:
  - **ID 列**: `案件番号`（`project_id` ではない、全 3 シート共通、値形式は未確認の Q7 として継続）
  - **統合表マイルストーン（8 列）**: `設計開始` → `基本図承認` → `仮受予定` → `本受予定` → `下付予定` → `契約上の着工` → `実着工予定日` → `引渡日`
  - **評点**: `案件評価+ポイント`（数値合計）
  - **意匠設計担当**: 統合表 `意匠担当` 列を 1 次ソース、空時のみ `config/projects.csv.key_contact` に fallback
  - **ヘッダ構造**: 統合表のみ **2 行ヘッダ**（上=グループ・下=詳細、`/` 区切りで合成）、他 2 シートは 1 行。詳細は [[05_learn/google-sheets-multi-row-header]]
- 進捗（2026-04-24 時点）: **45/50 tasks done**、81 tests pass、`openspec validate --strict` ✓。残: `/weekly-report` の end-to-end 突合（`案件番号 ↔ project_id` の Q7）、PR、archive
- Python venv は `plugins/pm-master-grabber/.venv`（`pip install -e '.[dev]'`、google-api-python-client / google-auth / google-auth-oauthlib）
- 未解決の Open Question:
  - Q7: `案件番号` の値形式（`FY26_01` 形式かどうか）— 次の `/weekly-report` 突合で判明、失敗時は `display_name` fallback を follow-up change で追加
  - Q8: `/pm-master-backup` を `/weekly-report` から自動トリガするか — 別 change

### 週次レポート履歴（2026-05 系統）

- **2026-05-01**（session 61d82ae6、5-7 22:00 JST）: `/jooto-backup --all-active` (39 ボード、1 skip) → `/jooto-overdue-scan` (73 件) → `/pm-master-backup` → `/weekly-report` で `reports/2026-05-01_weekly_update.md` 生成。前回比較元 `state/latest_*` = 2026-04-29 版、2 日差分。期日超過 6 件 → 5 件（解消 2 = 滝野川5丁目 M08/M09、新規 1 = 八幡山六地蔵 M04 4/30 期日通過 5 週間更新停止）。主要マイルストーン: 渋谷区本町5丁目 4/30 着工時金 88,080,000 円入金完了、西荻北1丁目 構造 KO MTG 49 分実施、板橋氷川町 4/30 ♦︎ MM4 本受け移行 Jooto 公式化、祐天寺 4/30 本受予定未達確定（三軸 UU 結果 5/9-10 まで入手なし）。運用課題: 完了済 overdue タスクの Jooto status 未更新が目立つ（笹塚方南 MM6 / 東長崎 MM2 / 中野坂上 S12）→ 構造的ノイズ。レポートはリポ内に未コミットで残置（内部成果物、外部公開なし）
- **2026-05-08**（session 552ceb4f、5-8 07:17 JST、`diff_against=2026-05-01 run_date=2026-05-08`）: `/jooto-backup --all-active` (40 ボード、**新規 `FY26_27 中野区本町5丁目` と `FY26_29 きつね塚通り前`** を検出) → `/jooto-overdue-scan` (1241349「２課」のみ archive で 404、FY26 案件は全件正常完了) → `/pm-master-backup` → 24 案件並列 Gmail 検索 (3 batch × 8-10 件) → `reports/2026-05-08_weekly_update.md`。
  - 主要トピック: **🚨 笹塚方南1丁目** 5/7 中村先生 Jooto で「隣地土地権利問題により PJ 休止中」発覚（引渡 5/17 の 9 日前）／**高円寺南** さくら構造「監理外」→ 大神別途費用交渉、新規 overdue 2 件（案内図・道路使用 / サッシ・UB 見積）／**世田谷大原** 本間の整合チェック 6 項目再督促、中村レス 11 日遅延（本受 5/31 まで 23 日）／**祐天寺** 三軸結果 16-17 日入手なし、5/20 下付達成困難／**中野坂上** 施工マイルストーン詳細確定（各階電気/スリーブ図リミット + 上棟 10/5）／**中野1丁目** 解体 5/18-6/4 延期通知＋ウチヤマ地盤調査／**駒込駅前** さくら構造に長期地耐力検討依頼／**西巣鴨駅前** 4/30 請負契約調印完了後の意匠フェーズ移行／**東長崎4丁目** 確認申請＋条例関連 7 項目督促（5/13 社判押印期日）
  - handover_diff 3 件: FY26_03/04/18 が「未定」→ ２課/１課/２課担当に確定
  - 新規ボード 2 件は projects.csv 未反映のため per-project セクション省略
  - 詳細: [[02_diary/2026-05-08]]

### 横展開できる小ネタ (2026-05 系統 2 ラン経由)

- **新規ボード検出は projects.csv 反映と独立**: `/jooto-backup --all-active` は board.updated_at をシードに新ボードを発見できるが、`projects.csv` (案件マスター) に entry が無ければ per-project セクションは生成されない (5-8 ランで `FY26_27 中野区本町5丁目` と `FY26_29 きつね塚通り前` が typically 検出 → 全体サマリ末尾の 1 行注記のみで本体省略)。新ボードは「検出 → projects.csv 追記 → 翌週 per-project 化」の 3 段で取り込む運用
- **archive ボードの 404 は許容**: `1241349 ２課` のような archive 済ボードは `/jooto-overdue-scan` で 404 を返す。FY26 案件側は `--board <id>` で個別実行が並列で正常完了するので、404 はログに残しつつ batch を止めない方針
- **handover_diff の現場担当変更 (「未定」→ ２課/１課)** は週次レポートで前回差分末尾に `; 申し送り: ...` 形式で吸収される。複数案件で同タイミング (= 期初の振り分け) に発生しがちで、週次レポートの主要トピックには浮上しないが、後続の overdue 検知に影響するので handover_diff だけは別途確認する習慣

## Links

- [[02_diary/2026-04-24]]
- [[02_diary/2026-04-25]]
- [[02_diary/2026-05-08]]
- [[05_learn/ssh-agent-shortcuts]]
- [[05_learn/gmail-mcp-reauth]]
- [[05_learn/google-sheets-multi-row-header]]
- [[05_learn/claude-code-plugin-namespace]]
- [[05_learn/fy-cycle-mmdd-year-inference]]
- [[06_output/2026-04]]
