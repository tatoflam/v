---
title: MeguruPMReport
category: 03_work
tags: [meguruit, jooto, weekly-report, python, google-sheets, project:meguru-pm-report, client:meguru, tech:python, tech:google-sheets, tech:gmail-mcp, tech:google-drive, tech:firebase-hosting, tech:firebase-functions, tech:launchd, tech:mermaid, stage:active]
sources: [3e07de94-4eea-46b3-892a-e815cd133f4e, 92ea8970-d8f1-4aa3-aaed-66db645434ca, bab023ec-53ee-4301-869d-306222b4a3f8, 002f63f9-be02-4b79-acd5-3f0f1b1ea354, 0e835096-fe82-4b7c-9127-a91d45d19520, a78e0aaa-c07f-4a30-bc50-8bec60ab1b1c, d87e347c-74eb-4770-bb1b-9b8ac0c9e386, 552ceb4f-7b74-492d-b829-616f7d6da38b, 61d82ae6-e969-4ebb-a4d1-d5174c250de1, 50e16870-ca1e-4877-8c90-c87059048d94, 27c4797e-4a8a-45c4-9fe4-7a06118a56af, 75556c24-bc5c-4976-baae-d00fdd820b15, b51914bf-d923-4c9a-8ab5-92f42b82481a, 0a506395-789d-4176-882c-7cce4fb8e07a, b50d3ddb-d9a6-4539-b43b-5a967748e748, 7d4100ea-5e88-4447-a4fd-5102759d4877, eee551a5-1222-433f-afc9-6158234a3b33, 3c659039-30a8-48b4-b825-7b0dc77bbaaf, d13623c3-f842-4c48-b688-8dc149f20c20, 24f10575-318b-41d3-b6c7-4a18bcb5d229, 3f66a79f-6018-47eb-83c7-d963ed362111, 5d8213db-5b81-4f67-a4aa-86c85e83d3af, f3a28fae-f6aa-45c6-94cf-566dcb101b26, fe1f5fac-3230-4199-912e-bdda570463c1, 2e4721dd-2285-4f3d-97ff-7e5e88c37b52, 8c7aa96d-0845-4a70-84e2-dc8bf17ffea7, 821f682c-145f-460a-9214-effb01b8a849, f1336766-5705-4d8b-a7bc-559494e807e1, fbb058f2-6e1d-4ae1-9460-f4e54099fbc0, cdd93242-ab74-40ad-a85e-4635b815f09d, 1fca49c1-8c3b-4a77-b6a4-0c4dcdbc0f81, 66be2df6-aeed-483f-804d-ca033fc1cf6a, 0ef2475c-8995-476b-aebc-f8856a937bed, d56dc1c3-34eb-4a4e-95d6-40cbe8f6da58, 00db3a35-a07a-43bf-913e-97f2d41c1041]
updated: 2026-06-05
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

### PMMasterGrabber プラグイン（2026-04-24 追加、OpenSpec change `add-pm-master-grabber` → 2026-05-29 archive 済）
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
- **2026-05-13**（session 50e16870、5-15 08:45 JST、ユーザー第一声「最新のレポートを作成して！」のみ）: `/jooto-backup --all-active` → `/jooto-overdue-scan` → `/pm-master-backup` → 24 案件 Gmail 並列検索 → `/weekly-report` で `reports/2026-05-13_weekly_update.md` (43 KB) 生成。前回比較元 = 5-08 版（5 日差分、`diff_against` 未指定 → `state/latest_*` 採用）。期日超過 8 → 7 件（解消 1 = 世田谷大原 MM2 / 5-8 本間「完了扱い」運用クローズ）。
  - 主要トピック: **東長崎4丁目** 審査機関質疑伸長で本受 7/10 → 7/20 へ +2 週間後ろ倒し確定／**駒込駅前** 仮受 6/10・本受 8/3・下付 8/27 への工程後倒し提案＋構造梁壁見直し CAD 共有で着手準備／**祐天寺** 軒高さ整合問題が顕在→構造図書差替で解消（5/12 完了、井上「審査機関へ差替手続き」）／**滝野川5丁目・中野1丁目** アスベスト顕出で解体後ずれ＋近隣家屋調査追加（ヤマダイ仕切 10 万円/軒）／**中野坂上** 着工準備一気に整備（躯体施工図／地震火災保険 WEB 完了／NICE 検査 6/11／道路使用 5/13-5/27）／**江古田江原・山王3丁目・幡ヶ谷不動尊通り・大森西2丁目** 長期停滞 4 案件が今週軒並み初動
  - 申し送り 18 件変更（基礎形状「直接基礎 → ベタ基礎」表記統一含む）
  - Jooto API: **板 1241349「２課」のみ HTTP 404** (archived) → projects.csv 対象案件には影響なし、log のみで batch 継続
  - 詳細: [[02_diary/2026-05-15]]
- **2026-05-15**（session 27c4797e、5-15 08:45→09:09 JST、ユーザー第一声「最新のレポートを作成して！」のみ）: `/jooto-backup --all-active --force` (全40ボード再取得) → `/jooto-overdue-scan` (基準日 2026-05-15、FY26 全 23 ボード) → `/pm-master-backup` (handover_diff 7 件) → 24 案件並列 Gmail → `reports/2026-05-15_weekly_update.md` (35 KB) 生成。前回比較元 = 5-13 版。期日超過 7 → 5 件（**解消 3 件**: 中野坂上 S12_質疑回答 done / 世田谷大原 MM2_意匠仮受 done / 駒込駅前 M03_平面レイアウト検証 期日設定解除）。
  - 主要トピック: **東長崎4丁目** 確認申請後ろ倒し +2 → **実質 +4 週間に拡大**（5/14 角田訂正「3/10 時点で 1 回目質疑 6/22→7/20、正しくは +4 週間」、更新版工程表受領、本受 7/10 起点で下付 7/25・着工 10/20 の再整合必要）／**駒込駅前** 構造発注フェーズ突入（5/13 市川 CAD Drive 格納、5/14 鈴木「基本図今週中完成、東京都防災・建築まちづくり防災へ提出」、大神「省エネ計算を構造に先駆け実施で確認完了早まる」提案 → 鈴木「渋谷区本町は同じ進め方で 1 ヶ月短縮実績」、本間「構造仮受 6/30・初回質疑 7/31・下付 8/31 でさくらへ発注」）／**江古田江原** 構造設計の契約調印完了（5/13 さくら経理斉藤送付→芦萱 MoneyForward 電子署名→同日斉藤完了、5/18 月実施設計着手で停滞 27 日終了）／**山王3丁目** 地盤改良見積3社並行依頼（サンワ工業/プラスエヌ/誠信 GLOCAL、RES-P 希望・刃工法ベタ基礎希望、構造質疑 5/19 回答期限と並走）／**幡ヶ谷本町** 地盤改良見積 3 社並行依頼（アルテック/誠信 GLOCAL/プラスエヌ、ベタ基礎+柱状改良 or 礎オメガ、5/20 期限）+ 図面 GL 整合解消（5/14 林「孔口標高+175mm が設計 GL」訂正版送付）／**中野1丁目** 解体完了 6/26 へ再延期（アスベスト除去工事追加）も KSA 品田質疑回答 5/13 提出で設計工期は変更なし／**中野坂上** JCAD が 3 階見上図・4 階見上図・屋根伏図順次納品、新規図面全納品完了／**渋谷区本町5丁目** 地区計画準拠の根拠確認決着（5/14 鈴木「電子申請で副本返却なし、申請書 1 枚目のみ役所持参で押印取得済」）
  - handover_diff 7 件: 滝野川5丁目 (FY26_04) と中野坂上 (FY26_07) で「不要／改良なし／不要」3 項目確定（地盤改良不要案件確定）、幡ヶ谷本町 (FY26_19) は基礎工法が「ベタ基礎＋柱状改良」→「ベタ基礎＋柱状改良 or 礎オメガ」（3 社見積依頼と連動）
  - 意匠負荷ビュー警告: 鈴木 4 件 (FY26_01/05/20/22) / 井上 3 件 (FY26_06/21/23)
  - **HTML サンプル試作 (PoC、定常運用化なし)**: user follow-up「確認しやすい形式で HTML にして同じディレクトリに出力できる？まだ定常運用するわけではないが、サンプルとして確認したい」に応えて `reports/2026-05-15_weekly_update.html` (52 KB、CSS 埋め込み自己完結) を 1 ファイル生成。工夫 5 点を後続定常化候補として控えておく:
    1. **案件インデックス**: 冒頭に全 24 案件のジャンプリンク
    2. **5 項目色分けタグ**: 実績=緑 / 予定=青 / 期日超過の示唆=赤 / 未解決=橙 / 前回差分=紫 の左カラム固定幅タグで横並び可読化
    3. **ステータスバッジ**: 案件見出しごとに「⚠ 期日超過あり」「超過なし」「期限設定なし」「超過データなし」で一覧リスク即判別
    4. **`**強調**` → 黄色マーカーハイライト**変換
    5. **CSS 埋め込み自己完結**: 外部依存なしでブラウザ直開き可
  - 06_output 該当判定: **該当せず**（HTML は PoC、外部公開 evidence なし）
  - 詳細: [[02_diary/2026-05-15]] 09:05 entry

> [!warning] 訂正 (2026-05-19T14:08Z run-22): `27c4797e` の生成物は `reports/2026-05-15_weekly_update.md` + `.html`、**5-13 版ではない**。5-13 版 (`reports/2026-05-13_weekly_update.md`, mtime 5/13 16:11) は `50e16870` 由来で 2026-05-13 履歴に既に集約済み。直前 21st-run (3826916, cron worker 22:59 entry) では 5-13/5-15 を取り違えて「並列セッション + HTML プレビュー」のみ注記となっていたため、本ランで 5-15 履歴セクションを正式に独立追加し、関連 sub-bullet を 2026-05-13 履歴から除去した

- **2026-05-19**（session b51914bf、5-19 22:57→23:17 JST、ユーザー第一声「最新のレポートを作成して！前回の会議後のフィードバックは、`latest_summary.md` にのみ更新済み。フィードバックを踏まえた上で、定常通り、今回のレポートを作成してほしい」）: `/jooto-backup --all-active` (40 ボード) → `/jooto-overdue-scan` → `/pm-master-backup` → 24 案件並列 Gmail (`mcp__claude_ai_Gmail__search_threads` × 24) → `/weekly-report` で `reports/2026-05-19_weekly_update.md` (211 行) 生成。前回比較元 = 5-15 版（前回会議後 user フィードバックは `latest_summary.md` 経由で取り込み）。期日超過 5 件 → **4 件**（解消 1 = 東長崎4丁目 ♦︎ MM2_意匠仮受 4/27 が今回スキャンで Jooto 側 done 化反映、継続 4 件は高円寺南 案内図・道路使用作成 / サッシ・UB 見積、笹塚方南 MM4_本受け / MM6_済証交付）。
  - 主要な動き①: **駒込駅前で構造発注完了**（5/19 Jooto M01 invoice、大神/本間「発注請書 Drive 格納済」）。5/18 鈴木→本間 基本図送付 → 5/18-19 大神⇄鈴木がオフィス棟内部レイアウトを 3 往復で詰め（事務所A の倉庫/主要部 扉分割、A 以外は倉庫→小会議室、応接室小→会議室、A 内部にデスク配置）、5/19 鈴木が 1F 事務所A 内部プラン提出。前週確定した「仮受 6/30・初回質疑 7/31・下付 8/31」目処の発注が早期に着地
  - 主要な動き②: **江古田江原で施主側「仕様設備・外装決定取り進め」要求発生**（5/17 原田→大神 確認申請書類＋更新工程表要求 → 大神 添付・「金融機関向けバッファ内で更新不要」回答、5/18 原田 仕様/外装決定の進め方イメージ依頼 → 5/19 大神 仕上パターン別テイスト資料（ナチュラル/フラット/シャープ）送付）。5/18 実施設計着手と同時期に施主側が動き、停滞 27 日の前進フェーズが本格化
  - 主要な動き③: **八幡山六地蔵で地盤調査報告書受領、構造方針議論本格化**（5/19 本間→大神/枝「ベタ基礎＋刃工法 or 柱状改良で 10m あたり N 値 15 で改良体止め」→ 大神「RES-P か刃が第一希望、枝 OK なら支持層未到達で SST も」→ 本間→枝「SST or RES-P 摩擦杭・改良体 6m 程度止め」→ 大神「RES-P 摩擦支持は無理、SST は締固めで摩擦取れる」→ 枝「GL-6m 先端だと支持力取りづらい」）。**申し送りで基礎工法が「ベタ基礎+刃またはRES-P」に確定**
  - 主要な動き④: **幡ヶ谷本町で地盤改良 3 社見積比較完了**（5/18 誠信GLOCAL 検討書＋見積書送付、5/19 本間→大神「誠信 GLOCAL NET 11.6M（税別）が良さそう」3 社比較レポート、5/19 本間→林/山口「プラスエヌの柱状改良計算書、SST/礎オメガはコスト観点で柱状改良前提」）。**申し送りで基礎工法は「ベタ基礎＋柱状改良 or 礎オメガ」→「ベタ基礎＋柱状改良」、地盤改良業者は空欄→「プラスエヌ」に確定**
    - **3 社技術比較サブブロック** (session `0a506395`、5-19 15:54→17:18 JST、Google Drive `FY26_19/03_地盤資料/02_地盤改良工事計` の検討書＋見積を読み込み比較、`地盤改良工事_3社比較レポート_260518.md` を Drive 保存)
    - 検討依頼書条件（さくら 260514）: 5層 WRC べた基礎／設計GL=KBM-165／杭頭 GL-2,250/-2,375/-3,300 (3 パターン)／杭長 4,325/5,075/5,375mm／杭頭ピン／支持層シルト混じり砂層／先端 **N=15**／設計水平力 2,000 kN／想定形式は **柱状改良検討**
    - **誠信GLOCAL (礎オメガ、大臣認定 TACP-0703)**: φ267.4 軸／翼 Dw=800、本数 **51 本**、杭長 3.725〜4.775m、先端砂 **N=15** (依頼通り GL-7.03m)、長期許容支持力 347 kN/本、施工 **4 日**、残土ほぼ無し、御社 NET **¥11.6M**。唯一の鋼管杭で施工日数最短だが鋼材費 ¥16.3M で総額最高、水平力は本数割算定 = 実水平力での再確認余地
    - **プラスエヌ (柱状改良、Fc=1,200 kN/m²)**: φ800、本数 97 本、コラム長 3.525〜4.575m (掘削 6.825m)、先端 N=12.5 (安全側採用、依頼書 N=15 からやや低め)、改良率 αp=0.396、qa=182.1 kN/m²、施工 6 日、出精値引 ▲525,280 円込み 御社 NET **¥4.54M** (3 社中圧倒的最安)、水平支持力検討も実施済
    - **アルテック (SST、粉体噴射撹拌、Fc=2,300 kN/m²)**: φ500、本数 **144 本**、コラム長 **6.00m** (掘削 8.20m)、先端 **砂礫 N=39** (深部硬質採用、3 社中唯一)、改良率 0.219 (ピッチ 1.14m)、LRa=150 kN/本、施工 **15 日**、山砂 94.5m³ 搬入＋残土 120m³ で工程・物流負荷最大、御社 NET **¥9.9M** (元請経費別途)
    - **価格差**: プラスエヌ vs 誠信GLOCAL で約 2.6 倍、vs アルテックで約 2.2 倍。プラスエヌ選定は価格優位 + 検討依頼書「柱状改良検討」想定への直接合致が決め手
    - **要確認ポイント (本セッション明示)**: 支持層採用が 3 社で乖離 (N=15/12.5/39、深度 GL-7/-6.825/-8.20m) → さくら構造へ「依頼書 N=15・GL-7m 前後を厳守すべきか、より深部硬質層への到達を許容するか」確認推奨。06_output 非該当 (御社 NET 価格を含む社内成果物、外部公開 evidence なし)
    - 詳細: [[02_diary/2026-05-19]] 15:54 entry
  - その他の前進: **江古田江原** さくら経理↔大神↔芦萱 MoneyForward 電子署名で契約調印クローズ（5/13 起点）／**渋谷区本町5丁目** B1階見上図・階段躯体図 CB ループ 1 周完了（5/17 田中→枝/鈴木 → 5/18 枝→田中 → 5/19 鈴木「意匠 OK」）／**東日暮里6丁目** 5/16 藤本→大神 施主仕上げ方針回答「外観・内観フラット仕様、館銘板=目黒美術館前と同様」、5/18 誠信GLOCAL 地盤改良見積到着で 5/19 牛山「ベタ基礎」確定／**中野1丁目** 5/18 さくら神鳥→KSA 品田 確認事項 5/20 午前回答依頼＋クリーンアイランドへアスベスト除去注文書 MoneyForward 承認／**新宿山吹町** 5/19(火)午前 看板設置＋施主株式会社TOKYO 法人所在地変更（晴海5丁目6-7-3706）が蔡→工事1課でクローズドループ／**板橋氷川町** 5/17-18 躯体積算 PDF まとめ受領で Jooto S10 完了コメント／**幡ヶ谷不動尊通り** 5/18 さくら経理 斉藤→大神 契約書送付＋芦萱「完了」/ 5/19 石田→澤口 地盤調査報告書送付「無改良で成り立つか確認」依頼／**山王3丁目** 5/14 大神→3 社（サンワ工業/プラスエヌ/誠信GLOCAL）地盤改良見積依頼＋ゴミ置き場 4m 路地反対側共有案（青木→施主、井上→隣地田中さん承諾要件）／**東長崎4丁目** 5/19 五十川→本間 CG 用 DXF 送付＋PersGPT 制作依頼完了／**西荻北1丁目** 5/15 枝 検討構造図タタキ送付＋廣川 X1 通り W25 壁範囲確認で停滞 7 日以上から議論再開
  - 静観継続: 千住4丁目・東尾久4丁目・大森西2丁目・祐天寺・笹塚方南（祐天寺は 5/20 下付予定が明日に迫るが Gmail 上動きなし、笹塚方南は隣地土地権利問題で PJ 休止継続）
  - handover_diff 5 件: 高円寺南 (FY26_01) と渋谷区本町 (FY26_05) が「発注状況=発注済」確定、八幡山六地蔵 (FY26_14) 基礎工法「ベタ基礎+刃またはRES-P」、幡ヶ谷本町 (FY26_19) 地盤改良業者「プラスエヌ」＋基礎工法「ベタ基礎＋柱状改良」
  - 意匠負荷ビュー警告: **鈴木 4 件**（FY26_01/05/20/22）／**井上 3 件**（FY26_06/21/23）、加納は **2026-05-20 空き見込み**（FY26_08 高田馬場 基本図承認 5/20 通過後）
  - 06_output 該当判定: **該当せず**（reports/2026-05-19_weekly_update.md は MeguruPMReport repo に未コミット、外部公開 evidence なし。state/latest_summary.md / latest_state.json / batch_progress.json も同期更新済）
  - 詳細: [[02_diary/2026-05-19]] 23:29 entry
- **2026-05-22**（session b50d3ddb、5-22 23:xx→5-23 00:01 JST、ユーザー第一声「最新のレポートを作成して！前回の会議後のフィードバックは、`2026-05-19_weekly_update.md` にのみ更新済み。フィードバックの内容を `latest_summary.md` に必要あれば転記した上で、今回のレポートを作成してほしい」）: 会議フィードバック 4 点（八幡山六地蔵=刃工法/RES-P 依頼分担＋大神 island 連絡、板橋氷川町=越境是正の着工後計画変更案、山王3丁目=RES-P 総和返信待ち）を `state/latest_summary.md` 全体サマリ＋per-project セクションへ手動転記 → `/jooto-backup --all-active` → `/jooto-overdue-scan`（**非 FY26 ボードで HTTP 404 で全件一括が停止** → FY26 ボード 24 件を個別 `--board <id>` スキャン）→ `/pm-master-backup` → 24 案件並列 Gmail → `reports/2026-05-22_weekly_update.md` 生成。前回比較元 = 5-19 版（`state/latest_*`）。期日超過 4 件 → **5 件**（新規 1 = 幡ヶ谷本町 MM2_意匠仮受が 5/20 未達で overdue 化）
  - 初版で発生した重大欠落と恒久対策（必読）: ユーザー指摘「幡ヶ谷本町は、仮受当日になって天空率の計算ミスが発覚、プラン見直しとなっており、山口設計士・大神・本間の間で頻繁にメールのやり取りがあるが、拾われていないのはなぜ？」→ assistant 初動「メールボックスに存在しないと推測」誤判定 → ユーザー再指摘「該当ラベルに届いてやり取りしてる、Gmail 検索が動いていないとしか思えない」→ assistant が `get_thread` で「【渋谷区幡ヶ谷本町】質疑」スレッドを直接展開 → **全 47 通中先頭 5 通（5/12 まで）しか `search_threads` が返していなかったことが判明、5/13 以降の 42 通が完全欠落**。`mcp__claude_ai_Gmail__search_threads` のスレッド先頭打ち切り仕様による取りこぼし。canonical: [[05_learn/gmail-search-threads-message-limit]]
  - 仕様恒久反映: `.claude/commands/weekly-report.md` 改訂（`search_threads` 結果だけで要約せず、**各スレッドを `get_thread` で全件展開し対象期間内のメッセージを 1 通も取りこぼさない**ことを完了条件に明記）／`config/workspace_defaults.md` に「期間内メッセージの全件取得（必須）」節を追加（期間外・引用履歴の非展開でコンテキスト節約、期間内の取りこぼしは許容せず）
  - 再点検 3 並列 subagent（全 24 案件の対象スレッドを `get_thread` で全件展開して 5/19→5/22 差分を再構築） → **取りこぼし 3 案件特定**:
    - **幡ヶ谷本町**: 仮受当日 5/20 に **天空率・日影規制の不適合発覚 → 建物形状を伴うプラン見直し** という重大インシデントが完全欠落 → 案件セクションを全面書き直し、全体サマリの「重要な動き①【重大インシデント】」に格上げ、MM2_意匠仮受 overdue の原因も明記。現況: 日影規制適合に平均地盤面〜4F パラペット天端 11.4m / 3F 天端 8.825m が必要、550mm 以上 建物高さを下げ＋埋め戻しで平均 GL 調整 or 小規模空堀で建物全体を下げる案を検討中。構造は着手済のため実費精算・手戻り発生、設備計画も再検討、施主への金利負担・スケジュール影響あり
    - **八幡山六地蔵**: 施主（島田さん）の 3 点確認のうち、②建物右側の自転車置き場が成立するか（配置プラン論点）／③リビングのプロジェクター設置距離 が省略 → 補記
    - **西巣鴨駅前**: 5/22 有間→大神「想定通りの測量図になっています」と修正測量図を承認したメッセージが欠落 → 実績に反映、未解決から「修正測量図の有間確認」を削除
  - 主要トピック（再点検後）: **🚨 幡ヶ谷本町 仮受当日 天空率・日影不適合 → プラン見直し**（上述）／**祐天寺** 確認済証 5/19 発行で下付着地（5/20 下付予定達成）／**滝野川5丁目** 整合性チェック収束（構造図のみ修正）・特寸サッシ製作可能確定・構造質疑のさくら対応始動／**大森西2丁目** 構造設計のさくら契約調印完了（5/21 電子署名）／**江古田江原** さくら構造担当アサイン完了・構造実施設計始動／**西巣鴨駅前** 越境物（トタン屋根・雨どい）敷地除外で測量図修正＋有間承認／**八幡山六地蔵** 会議 FB 通り大神→島田パース確認連絡を実行、施主から違和感なし＋3 点質問（自転車置き場・プロジェクター距離・残 1 点）／**中野1丁目** 申し送り「審査機関=アウェイ」→「アウェイ／国際確認」変更
  - Jooto API 運用課題: **非 FY26 ボードでの HTTP 404 で `/jooto-overdue-scan` 一括実行が止まる**（5-13 / 5-15 ランで観測した 1241349「２課」と同類）→ FY26 案件 24 ボードを個別 `--board <id>` スキャンで運用回避。`workspace_defaults.md` または `/jooto-overdue-scan` 側の 404-tolerant 化が follow-up 候補
  - 06_output 該当判定: **該当せず**（`reports/2026-05-22_weekly_update.md` は MeguruPMReport repo に commit `ff1e628 update: 0522`、origin/main へ push 済だが、内部成果物で外部公開 evidence なしの 5-19 precedent を踏襲。内部 private repo への push は schema §"06_output/ auto-detection" の「外部公開」基準には満たないと解釈）
  - 詳細: [[02_diary/2026-05-23]] run-36 entry（本ファイル更新を実行した /wiki-ingest ラン）

- **2026-05-26**（session eee551a5、5-26→5-27 06:31 JST 跨ぎ、第一声「最新のレポートを作成して！」のみ）: `/jooto-backup --all-active` → `/pm-master-backup` → `/weekly-report` 実行中 NW エラー停止 → user「途中で API エラーで止まった、必要な箇所からリカバリするか、難しければもう一度最初から、最新のレポート作成を実施できる？」→ リカバリ実行で `reports/2026-05-26_weekly_update.md` 生成。前回比較元 = 5-22 版。
  - **13 工程進捗ビューの実 user データ初回適用**: 直前 commit `b75ffb6` で実装した `add-phase-progress-view` (下記「工程軸の進捗ビュー」セクション) が初めて実データで動作。user フィードバック「**工程軸の進捗で、なんで東向島5丁目が「前提整理」になる？マスター表のどこを見てそのように判定しているのだろう。この案件は設計は終了していて、「工事着手」している状況。**」 → 辞書チューニング course-correction の最初の data point を獲得。`phase_evidence` を読み Jooto タスク名辞書または Gmail 件名辞書に「工事着手済」シグナルを 1 件以上追記する follow-up を `workspace_defaults.md` に持ち越し (specs 不変)
  - **板橋氷川町ピンポイント追記運用**: user「Jooto で板橋氷川町の更新あり。そこだけ追記してくれない？差分対象などは比較する必要なし。前回レポート日: 2026-05-22 のママで OK.」 → 全案件再生成のコストを払わずに特定案件のみ部分更新する運用パターンを実証。粒度の柔軟性が確認できた
  - commit `ec8b13e Add 2026-05-26 weekly update and refresh state snapshots` (3 ファイル: `reports/2026-05-26_weekly_update.md` 新規 + `state/latest_state.json` + `state/latest_summary.md`) → origin/main へ push 完了 (`b75ffb6..ec8b13e`)
  - 06_output 該当判定: **該当せず** ([[02_diary/2026-05-23#フェーズ-5-state-同期--commit|run-36 precedent]] 踏襲、`meguruit/MeguruPMReport` は private repo、内部成果物で外部公開 evidence なし)
  - 詳細: [[02_diary/2026-05-27]] run-42 entry

### 工程軸の進捗ビュー (2026-05-26 OpenSpec change `add-phase-progress-view`、commit `b75ffb6`)

週次レポートに「**工程軸の進捗**」セクションを追加し、24 案件がそれぞれ 13 工程のどこまで到達したかを per-phase で並べて可視化する機能。session `7d4100ea` で proposal/design/specs/tasks 4 アーティファクト全起票 → `openspec validate --strict` 通過 → 実装着地。

- **13 工程フォーマット** (`0. 案件準備中 → 1. 前提整理 → 2. 平面検証 → 3. 施主承認 → 4. 躯体形状 → 5. 構造着手 → 6. 設備検討 → 7. 仮受付前 → 8. 整合確認 → 9. 本受付前 → 10. 施工着手 → 11. 確認交付 → 12. 引渡準備 → 13. 工事着工`): user 提示の 11 工程に対し「0. 案件準備中」を追加・「1. 前提整理」へ改名で 13 段に拡張
- **判定ロジック (band-default + 最進工程ルール)**: 各案件について Jooto タスク名辞書 (M01-M11 完了で M フェーズ通過判定、MM1-MM6 でマイルストーン到達判定、S0X workflow 順) と Gmail 件名辞書を突合し、**最進工程 (= 一番先まで到達した工程)** を採用。辞書チューニングは `workspace_defaults.md` のみで完結し、specs (`openspec/specs/`) は不変 という分離が design.md に明文化
- **`phase` / `phase_evidence`**: 工程判定の結果と根拠を `state/latest_state.json` の 24 案件全件に書き込み。`phase_evidence` で「どの Jooto タスク or どのメール件名がその判定を支持したか」が追跡可能 → user 想定 vs 機械判定の乖離 (例: 東向島5丁目 user=工事着手 vs 機械=前提整理、上記 5-26 entry 参照) を `phase_evidence` で診断し、辞書のみで吸収できる設計
- **実装着地ファイル** (commit `b75ffb6 Add 「工程軸の進捗」 section to weekly report (13 phases)`、8 ファイル / +1108 / -51):
  - `openspec/changes/add-phase-progress-view/` (proposal.md / design.md / specs/**/spec.md / tasks.md、19/23 tasks complete)
  - `config/workspace_defaults.md` (12 → 13 工程セクション追加、Jooto + Gmail 辞書定義)
  - `.claude/commands/weekly-report.md` (実行手順 6 として工程判定を追加)
  - `state/latest_state.json` (24 案件全件に `phase` / `phase_evidence` 書き込み)
- **archive 未** (`/opsx:archive` まだ実行せず): 実 user データでの判定精度検証完了後 (= eee551a5 で初回データ取得 → 辞書チューニング 1 件以上反映後) に archive 予定。19/23 tasks の残 4 件は user データ検証 + 辞書補強 + archive 手続きと想定
- 詳細: [[02_diary/2026-05-27]] run-42 entry (7d4100ea 知識 footprint)

### 横展開できる小ネタ (2026-05 系統 2 ラン経由)

- **新規ボード検出は projects.csv 反映と独立**: `/jooto-backup --all-active` は board.updated_at をシードに新ボードを発見できるが、`projects.csv` (案件マスター) に entry が無ければ per-project セクションは生成されない (5-8 ランで `FY26_27 中野区本町5丁目` と `FY26_29 きつね塚通り前` が typically 検出 → 全体サマリ末尾の 1 行注記のみで本体省略)。新ボードは「検出 → projects.csv 追記 → 翌週 per-project 化」の 3 段で取り込む運用
- **archive ボードの 404 は許容**: `1241349 ２課` のような archive 済ボードは `/jooto-overdue-scan` で 404 を返す。FY26 案件側は `--board <id>` で個別実行が並列で正常完了するので、404 はログに残しつつ batch を止めない方針
- **handover_diff の現場担当変更 (「未定」→ ２課/１課)** は週次レポートで前回差分末尾に `; 申し送り: ...` 形式で吸収される。複数案件で同タイミング (= 期初の振り分け) に発生しがちで、週次レポートの主要トピックには浮上しないが、後続の overdue 検知に影響するので handover_diff だけは別途確認する習慣

### sync-published-doc-before-report (2026-05-28 OpenSpec change、31/35 tasks → 2026-05-29 archive 済)

配信済み Google Doc を Drive 上で人手編集された場合に備えて、次回 `/weekly-report` の baseline を Drive から fetch して取り込む仕組み。session `3c659039` (2026-05-28 08:07-08:28 UTC) で proposal/design/specs (3 capability) /tasks 全起票 → `openspec validate --strict` 通過 → 31/35 tasks 実装着地。残 4 task は live Drive/Firebase E2E のため次回自然な `/weekly-report-publish` + `/weekly-report` ランで自動消化予定 (本セッションで 7.3 は `state/latest_state.json` の `published_doc_id` 反映を確認済、commit d27caa7 の state diff)。session `24f10575` (2026-05-29 01:24-01:28 UTC) で deferred 4 tasks を「dogfood で自然消化扱い」として archive 化 (commit `5efbb1c`、`openspec/changes/archive/2026-05-29-sync-published-doc-before-report/` へ移動)。

- **動機**: 前回 `/weekly-report-publish` で配信した Google Doc が宛先側で人手修正されると、次回レポートの差分計算が古い `latest_summary.md` ベースになり、修正が消える形でレポートが上書きされる。Drive を **canonical source** に据え直し、`/weekly-report` 起動時にまず Drive から最新を取り込む
- **核 design (7 個の Decision)**:
  - **Doc 解決キー**: `state/latest_state.json` の `published_doc_id`（前回 `/weekly-report-publish` 成功時に書き込まれる）
  - **Export API**: Drive `files.export(fileId, mimeType='text/markdown')`、UTF-8 + CRLF normalize
  - **マスキング比較**: 配信時のマスキング差分（氏名・社名等）は比較ルール側で無視（specs 不変、`workspace_defaults.md` の辞書層で吸収）
  - **既定挙動**: `/weekly-report` 起動時に自動先行 sync、`--skip-baseline-sync` で opt-out 可、`diff_against=YYYY-MM-DD` 指定時は走らせない
  - **書き込み**: `.bak-{YYYYMMDDTHHMMSSZ}` バックアップ → tmp+fsync+`os.replace` の atomic 上書き
  - **失敗時**: 副作用なしで終了、user に対話的フォールバック提示
  - **Drive 権限**: read-only export、書き込みスコープ追加なし
- **実装着地ファイル** (commit 未確認、本セッション末で `commit, push, openspec archive` を実行する場合は次ラン以降で追跡):
  - `plugins/drive-publisher/scripts/fetch_doc.py` (new) — `DriveClient.export_doc` + `DefaultDriveClient.export_doc`、UTF-8 + CRLF normalize、429/5xx は 1/2/4s backoff の指数バックオフ
  - `plugins/drive-publisher/scripts/sync_baseline.py` (new) — `SyncResult` dataclass + `.bak-{ISO}` バックアップ + atomic tmp+fsync+`os.replace`
  - `plugins/drive-publisher/scripts/test/test_fetch_doc.py` + `test_sync_baseline.py` (new)
  - `.claude/commands/weekly-report-sync-baseline.md` (new) — `/weekly-report-sync-baseline` slash command
  - `.claude/commands/weekly-report.md` (修正) — event 0 として auto-baseline-sync を追加、`--skip-baseline-sync` フラグ実装
  - `config/workspace_defaults.md` (修正) — masking-before-comparison ルール追記（specs 不変、辞書層のみ）
  - `plugins/drive-publisher/scripts/publish.py` (修正) — `_update_latest_state_meta` が全 3 step (HTML deploy + Drive upload + email notify) 成功時のみ `published_doc_id` / `published_doc_url` / `published_html_url` / `published_run_date` を `state/latest_state.json` に upsert（部分成功時は書き込みなし）
  - `plugins/drive-publisher/scripts/test/test_publish.py` (修正) — 新規 4 test (publish-success-writes-meta / partial-failure-no-write / pre-existing-meta-preserved / meta-keys-shape)
  - `.gitignore` (修正) — `state/*.bak-*` / `reports/*.bak-*` 除外
  - `CLAUDE.md` (修正) — 新コマンド + flow + ファイルレイアウト反映
- **検証**: pytest **79 passed** (前回 63 → +16 新規)、`openspec validate --strict` ✓
- **deferred 4 tasks** (7.3-7.6) — live Drive/Firebase E2E:
  - 7.3 `/weekly-report-publish` → `state/latest_state.json` に `published_doc_id` が書き込まれること
  - 7.4 `/weekly-report-sync-baseline` → `.bak-*` 生成 + 内容上書き
  - 7.5 `/weekly-report --skip-baseline-sync` → sync skip 確認
  - 7.6 Drive 上で Doc 編集 → `/weekly-report-sync-baseline` → 編集が local に伝播
- **archive 済** (`24f10575` で 2026-05-29 実行、commit `5efbb1c`): deferred 4 tasks は実装パターンが 5-27 archive 済の `add-weekly-report-distribution` と同型のため dogfood 自然消化扱いで archive 化。7.3 (`published_doc_id` upsert) は本セッションの state diff で実機確認済、残 7.4-7.6 は次回自然な `/weekly-report-publish` + `/weekly-report-sync-baseline` で確認予定
- 詳細: [[02_diary/2026-05-29]] run-51 entry (実装着地) + run-55 entry (archive 実行)

### 2026-05-29 openspec archive ラン (24f10575) — `add-pm-master-grabber` + `sync-published-doc-before-report` を archive 化、3 commit push

session `24f10575-318b-41d3-b6c7-4a18bcb5d229` (5-29 01:24-01:28 UTC = JST 10:24-10:28、user 第一声「openspecでarchiveできるchangeがあれば、archiveしてcommitして。必要な斬タスクを洗い出して」) で `openspec list` 上の 3 active change を棚卸し → 2 件を archive、1 件は soak time 不足で active 据置。

#### archive 判定の根拠

| change | 在席 | 判定 | 根拠 |
|---|---|---|---|
| `add-pm-master-grabber` | 約 5 週間 (4-24 起票) | ✅ archive | 実装機能 (意匠負荷ビュー + 申し送り差分) は 5-01 以降の `/weekly-report` 全レポートで本番稼働中、deferred 8.8 / 9.3 は **follow-up** として認識した上で archive 化 |
| `sync-published-doc-before-report` | 3 日 (5-28 起票 → 5-29 archive) | ✅ archive | 実装 + 79 tests green、deferred 7.3-7.6 は live E2E のみで、同型パターンの先行 archive 化 `add-weekly-report-distribution` (5-27 archive) を踏襲 |
| `add-phase-progress-view` | 3 日 (5-26 起票) | ⏸ 据置 | task 7.2 が「1〜2 週運用での誤判定ログ収集 → 辞書チューニング」を明示要求、現在 3 日経過 → soak time 不足。archive 目安 2026-06-09 以降 |

#### 3 commit の内訳

session 開始時の git status は 12 ファイル未 commit (5-29 の `/weekly-report` 結果 + sync-published-doc-before-report 実装 + state 更新)。論理単位 3 本に分割して `origin/main` push:

- `d613da7 Sync published Drive doc into baseline before weekly-report` — sync-published-doc-before-report の実装本体 (9 ファイル: `fetch_doc.py` / `sync_baseline.py` / `weekly-report-sync-baseline.md` 新規 + `weekly-report.md` / `workspace_defaults.md` / `publish.py` / `.gitignore` / `CLAUDE.md` 修正 + 4 新規 test)。配信物 (`reports/2026-05-29*`) と state は意図的に除外
- `d27caa7 Add 2026-05-29 weekly update and refresh state snapshots` — 5-29 週次レポート + state 更新 (3 ファイル: `reports/2026-05-29_weekly_update.md` 新規 + `state/latest_state.json` + `state/latest_summary.md`)。`state/latest_state.json` の diff で `published_doc_id` 等が反映済なことを確認 = sync-published-doc-before-report task 7.3 の自然消化
- `5efbb1c Archive add-pm-master-grabber and sync-published-doc-before-report` — `openspec archive --yes` 2 回実行 (`openspec/changes/add-pm-master-grabber/` → `openspec/changes/archive/2026-05-29-add-pm-master-grabber/`、同様で sync 側) + 各 archive ディレクトリの specs delta 同期は本リポ未同期運用のためスキップ

push range: `9310599..5efbb1c` → `origin/main`。

#### archive 後の follow-up TODO (specs 不変、運用判定で吸収)

**`add-pm-master-grabber` 残 task (アーカイブ済で本体は close、follow-up のみ持ち越し)**:
- **8.8**: 統合表の `案件番号` 列が `projects.csv.project_id` (`FY26_01` 形式) と厳密一致するか、次回 `/weekly-report` 実行時に検証。不一致なら `display_name` fallback の follow-up change を起票
- **9.3**: `ruff check .` / `mypy scripts` を CI/pre-commit で実行する配管 (プラグイン venv 未インストールのため pipeline 側で)

**`sync-published-doc-before-report` 残 task (deferred 4)**:
- 7.3 ✅ 本セッションの `d27caa7` で state diff 確認済 (`published_doc_id` upsert OK)
- 7.4 `/weekly-report-sync-baseline` 単体実行 → `state/latest_summary.md.bak-*` 1 件生成 + 本体が Drive 内容で上書きされること
- 7.5 `/weekly-report --skip-baseline-sync` → baseline sync スキップ確認
- 7.6 Drive 上で Doc を 1 行手動編集 → `/weekly-report-sync-baseline` → `state/latest_summary.md` に反映される E2E

**`add-phase-progress-view` (active 据置の判定理由 + 次回検証ポイント)**:
- task 6.1 / 6.5 / 6.6: 次回 `/weekly-report run_date=2026-06-XX` 実行時に「`; フェーズ遷移: ...` 行が変化案件に出ること」「アクション項目サブ行 (Jooto unchecked + Gmail 件名) が機能すること」を検証
- task 6.3: 既知の判定乖離 (千住 / 滝野川 / 祐天寺 / 笹塚 / 駒込駅前 / 幡ヶ谷本町 / 東向島5丁目) の運用合意 = user がマニュアル編集 + 辞書フィードバック
- task 7.2: 1〜2 週後、誤判定ログから `config/workspace_defaults.md` の辞書を微調整 (specs 不変)
- task 7.3: 安定確認後に `openspec archive add-phase-progress-view` (目安 2026-06-09 以降)

#### 設計判断: spec sync スキップ運用

本リポは `openspec/specs/` 未同期運用 (過去方針) のため archive 前の spec sync はスキップして archive ディレクトリ移動のみで完了させた。将来 spec sync を有効化する場合は archive 化前に `openspec sync` を挟む手順を追加。

#### see also (24f10575 由来)

- [[02_diary/2026-05-29#21:15  run-55  /wiki-ingest — substantive 1 (24f10575) + meta drain 2 + 1 new defer (e594cbdd dirty 03_work/todobot)]] — 本セッションの ingest entry
- session `24f10575-318b-41d3-b6c7-4a18bcb5d229` (5/29 10:24 JST 起動、archive 2 件 + 3 commit push)

### Jooto 進捗状況 → 工程軸 + Milestone シート同期 (2026-05-29 提案、3f66a79f、`/opsx:propose` 中断で artifact 未起票)

session `3f66a79f-6018-47eb-83c7-d963ed362111` (5-29 22:58-23:02 JST、3 turn の `/opsx:propose` 起動直後に user interrupt) で受領した新規 feature 提案。OpenSpec change としては未起票 (proposal/design/specs/tasks まだなし)、要件文のみがセッションに残った。次に再起動するまで wiki にバックログ保管。

**user 提案要件 3 点**:

1. **Jooto 進捗状況タスクを工程軸の進捗ビューに優先反映**: 各案件の Jooto ボードに「**進捗状況**」というタスクが存在する場合、その中のチェックリスト「**マイルストーン**」の項目ごとのチェック内容を取得し、`/weekly-report` の「**工程軸の進捗**」セクション (`add-phase-progress-view` で実装済の 13 工程ビュー) の判定に**優先**して利用する。「進捗状況」タスクが存在しない案件はこれまで通り Jooto 他タスク + メールスレッド辞書フォールバック
2. **Google Spreadsheet (進捗管理表_master) Milestone シートの実績チェックボックスを更新**: 上記 Jooto「進捗状況」を canonical source として、`進捗管理表_master` の `Milestone` シート (= `pm-master-grabber` と同じスプレッドシートオブジェクト) の **各案件 × 各工程の「実績」チェックボックスを更新**。Milestone シートのレイアウト想定: 案件行 (B4 から 1 行ごと) × 工程列 (M2 から 2 列ごと)、L 列が実績チェックボックス・M 列が期日。**フォーマットは変わり得るのでタイトル行・列やデータ範囲は動的検索で取得する**。本要件は **read-only 厳守の原則例外** (Milestone シートの実績列のみ write 許可) になるため、`pm-master-grabber` の OAuth スコープ拡張 (`spreadsheets.readonly` → `spreadsheets`) または書込み専用の別 grabber 切り出しを設計判断する必要あり
3. **工程名 ↔ Jooto タスク名のマッピング config 化**: 現状の Milestone シート工程タイトル (csv 1 列目) と Jooto「進捗状況」チェックリスト項目 (csv 2 列目)、(2 列目空時の fallback として) Jooto 他タスクの完了状態 (csv 3 列目) の対応関係を `config/` 配下に json または yaml で配置する。3 列目フォールバック使用時は曖昧検索 (Jooto リスト/メール件名のワード拾い) を許容する。マッピングは今後更新予定なので config ファイル化が必須

**user 提示のマッピング表 (現行・改定見込み)**:

| Milestone シート工程名 (1) | Jooto 進捗状況チェック項目 (2) | Jooto 他タスク完了状態 (3) |
|---|---|---|
| 構造梁位置確認 | 梁位置・壁量壁長確認依頼、構造見積依頼、構造着手日・納品日送付（概算） | |
| 平面検証 / 企画承認 | 平面検証 | |
| 施主承認 | 施主承認 | |
| 躯体形状 | 躯体形状 | |
| 設備検討 | 設備検討 | |
| 構造キックオフ | 構造キックオフ | |
| 基本図(平立断) / 天空率 | | |
| 実施（意匠・設備） | 意匠着手 | |
| 実施（構造） | 構造着手 | |
| 仮受（意匠・構造） | 仮受付 | |
| 省エネ申請 | | S08_省エネ申請 |
| 景観条例チェック | | S00_景観条例 |
| 狭隘協議チェック | | S00_狭隘協議 |
| 中高層条例チェック | | S00_中高層申請 |
| 清掃局チェック | | S00_清掃局協議 |
| 緑化・雨水対策チェック | | S00_緑化関連条例 |
| パース承認 | | ♦︎ SM1_パース・仕上げ・館銘確定 |
| 誤記・整合性確認 | 図面整合性確認 | |
| 反映・修正図受領 | | S06_図面誤記・整合性確認 |
| 本受（意匠・構造） | 本受付 | |
| 施工図作成依頼 | 施工着手 | |
| 躯体積算依頼 | | S10_躯体積算 |
| 下付 | 済証交付 | |
| 着工 | 工事着手 | |

**設計上の論点 (artifact 起票時に解消する想定)**:

- **既存 `add-phase-progress-view` (13 工程ビュー、`b75ffb6` で実装着地) との整合**: 13 工程は内製分類で「Jooto タスク名辞書 + Gmail 件名辞書」を `workspace_defaults.md` に持つ。本提案は Milestone シートの 24 工程 (上表行数) が canonical で、「進捗状況」タスクの**チェックリスト項目**が直接シグナル。13 工程ビューを廃止して 24 工程に揃えるか、両立 (13 = サマリ、24 = 詳細) するかが第 1 の論点
- **Spreadsheet 書込み権限**: 現 `pm-master-grabber` は `spreadsheets.readonly` で AST guard (`test_readonly_guard.py`) により書込み API 呼出しは禁止。本提案を満たすには (a) write 権限を持つ別 grabber 新設 (b) `pm-master-grabber` を `spreadsheets` スコープに昇格 (c) 別 OAuth client / service account のいずれか。CLAUDE.md の「Google Spreadsheet は厳格 read-only」原則の例外運用設計が必要
- **「進捗状況」タスクの存在前提**: Jooto 全案件ボードに「進捗状況」タスクが揃っている前提だが、現在は未整備の可能性大。整備の前提条件 (テンプレート化 / 初期化 grabber) も別 change で必要

**次のアクション** (本セッションは中断のみで何も起票していない):

- user 側で `/opsx:propose <change-name>` を再起動する想定 (例: `add-jooto-milestone-progress-sync`)。再起動時、本セッションで失われた CSV マッピング全文は本セクションから transcribe 可能
- もしくは Phase 1 (Jooto 進捗状況 → 工程軸ビューへの優先反映、read-only のみ) と Phase 2 (Milestone シート書込み、write 権限が要る) で 2 change 分割が安全

### 2026-05-29 add-milestone-sync 実装着地 + ライブ書き戻し成功 (5d8213db、~8h、Phase 1 + Phase 2 統合)

session `5d8213db-5b81-4f67-a4aa-86c85e83d3af` (5-29 23:11→5-30 07:31 JST、576 turn) で 3f66a79f 提案を `/opsx:propose add-milestone-sync` として起票 → 63/74 task 実装 → 実 Spreadsheet への 57 セル書き戻し成功 → 設計 v2 ピボットで user pause まで一気通貫。Phase 1 / Phase 2 分割案は採らず、`pm-master-writer` 独立プラグイン + `pm-master-grabber/scripts/shared/` 再利用パターンで両方を 1 change に統合。

**OpenSpec 起票 (v1)**:

- `add-phase-progress-view` を archive 化 → 13 工程要件が baseline specs (`openspec/specs/weekly-report/spec.md`) に確定 (前提条件解消)
- `add-milestone-sync` proposal / design / specs / tasks 全 4 artifact 起票、74 task
- **Decision 1**: `pm-master-writer` 独立プラグイン (write 権限を grabber 側に逆流させない、token.json 分離で scope 物理分離)。ただし Sheets / OAuth / マッピング / Milestone レイアウト検出は **`pm-master-grabber/scripts/shared/` 集約 → writer から import 再利用** (重複コードゼロ)
- **Decision 8 (反転後)**: 双方向同期 — `progress_checklist.prev.json` ↔ `progress_checklist.json` の差分で `false→true` を TRUE 化 / `true→false` を FALSE 巻き戻し。**Jooto 側で変化のないセルは絶対触らない** → Milestone 側の手動 TRUE 化は完全保護。初回 (prev 無し) は TRUE 化方向のみ
- **Decision 4**: 進捗状況タスク未設定の案件は **工程軸グリッド / Milestone サブ行から除外**、案件セクション末尾 `- Milestone: 進捗状況タスク未設定` の 1 行 + 工程軸セクション末尾 `### 進捗状況未設定の案件` H3 ブロックに案件名 + 担当者を列挙 (誤推定温床を物理排除)

**実装着地**:

- `plugins/pm-master-grabber/scripts/application/fetch_milestone.py` + 4 test、`run_backup` 組込
- `plugins/jooto-grabber/scripts/application/progress_checklist.py` + 17 test、`backup_board` 組込 + `progress_checklist.prev.json` 1 世代 rotation
- `plugins/pm-master-writer/` 新規プラグイン (~200 行コア、shared 流用で diff 最小):
  - `application/diff_progress_checklist.py` — Jooto snapshot diff (`FALSE_to_TRUE` / `TRUE_to_FALSE` / `UNCHANGED`)
  - `application/writeback_milestone.py` — Decision 8 双方向同期 planner
  - `infrastructure/range_guard.py` — 動的検出 allow-list 以外を `ForbiddenRangeError` で物理拒絶
  - `infrastructure/sheets_writer.py` — `values.update` guard wrapper
- `.claude/commands/weekly-report.md` — 第 0 ソース = Jooto 進捗状況 最優先 + 既存ロジック (PM マスタ統合表 / Jooto 他タスク / Gmail) フォールバック、`--writeback-milestone` オプション + step 9 post-execution writeback、未設定 H3 block、Milestone 連動サブ行 (`遅延` / `直近予定`)、read-only 制約改訂
- `CLAUDE.md` — Google Spreadsheet 節を read-only path (grabber) + write path (writer) で再構成、5 層 safety、writer コマンド表追記、shared module note、`milestone_mapping.yaml` layout 表追加
- `config/workspace_defaults.md` — 工程軸の進捗節を「判定対象 = 進捗状況タスクあり案件のみ」前提に書き換え、第 0 ソース追加、サンプル出力を 9 ボード分布で再構成
- **テスト**: pm-master-grabber 105 + jooto-grabber 69 + pm-master-writer 29 = **203 全 pass**、`openspec validate --strict add-milestone-sync` pass

**ライブ検証で発掘した 3 件のバグ / マッピングギャップ**:

1. 🐛 **Jooto API スキーマミス (重大)**: `/v1/tasks/{id}/checklists` は **ヘッダのみ返し、items は別 API `/v1/checklists/{id}/items` 経由必須**。自分の `progress_checklist` 実装 + 既存 `/jooto-overdue-scan` が同じバグ → **過去 43 件の `overdue.json` がすべて `unchecked_checklists` 空** (PM は週次レポートで未チェック項目を一度も見られていなかった、約 4 ヶ月の silent bug)。修正: 新規 `application/checklists.py` に `fetch_task_checklist_headers` / `fetch_checklist_items` / `fetch_task_checklists_with_items` を共通化、overdue + progress_checklist 双方を経由。詳細: [[05_learn/jooto-checklist-items-separate-endpoint]]
2. 🔧 **アイテム表示フィールドは `content`** (`name` / `title` ではない、Jooto API ドキュメント未明記) → `_normalize_item` 修正
3. 🔧 **マッピング config 不整合** (実 Jooto テンプレ ↔ user 提示 CSV のズレ):
   - `前提整理` ラベル (9/10 ボードで checked) が config 未登録 → 追加
   - `構造梁位置確認` の Jooto 実ラベルは **「梁位置・壁量壁長確認依頼、構造見積依頼、構造着手日・納品日送付（概算）」(3 項目を `、` 連結した 1 チェックリスト項目)**、`構造キックオフ` も「構造キックオフ、構造設計発注（Limit）、MS（FIX）」の連結形式 → 実ラベルに合わせて修正
   - 結果: **15 distinct labels すべてマッピング一致 (15/15)**、未マッピング 0、未使用 config 0

**format 統一 (途中追加)**: `config/pm_master_mapping.json` → `config/pm_master_mapping.yaml` 化 (理由: `milestone_mapping.yaml` 新規追加で混在になり、PM 編集者の認知負荷を排除しつつ YAML コメントで運用注釈を残せるようにする)。`shared/mapping_loader.py` を `yaml.safe_load` 化 (PyYAML は既に依存)、test で `test_invalid_yaml_raises` + `test_non_mapping_root_raises` 追加、CLAUDE.md / README / weekly-report.md / 3 grabber コマンド / writer プラグイン doc 全 sweep

**OAuth 構成発見**: `credentials.json` は **共通で OK** (client_id + client_secret は **アプリ識別**)、scope (read-only / read-write) は **token.json 側で物理分離**される。当初 spec で「credentials.json も別ファイル」と書いたが過剰だった → grabber 側を symlink 共有 (`plugins/pm-master-writer/credentials.json → ../pm-master-grabber/credentials.json`)、writer 専用は token.json のみ。spec / README 緩和

**ライブ書き戻し成功 (実 Spreadsheet への 57 セル write)**:

- `/pm-master-backup` → Milestone 動的検出 24/24 ヘッダ一致、案件名 23/24 一致 (1 件は projects.csv と Milestone シートで表記差あり)
- `/jooto-backup --all-active` → 41 ボード処理、10 ボードに `progress_checklist.json` 生成 (実 9 + テンプレ 1)
- `/pm-master-writer-auth` → OAuth 同意完了、`pm-master-writer/token.json` 生成 (`scope: spreadsheets`)。`grabber/.venv/bin/python` を `PYTHONPATH=scripts` で writer から流用 (writer 専用 venv は作らない、依存共通)
- `/pm-master-milestone-writeback 2026-05-30 --dry-run` → 57 セル計画 (全 `FALSE_to_TRUE`、巻き戻し 0、unmapped 0、unknown_project 0)、他シート SHA256 preserved、A1 検査で全部 achieved 列 (期日列への書き込み無し)
- **本書き戻し → 57/57 セル全件成功、書き込み後再 fetch 検証で実 Spreadsheet で TRUE 化を確認 (mismatch 0)**
- スキップ 2 ボード (高円寺南5丁目 / 渋谷区本町5丁目) は Jooto 15/15 + Milestone 既 23/24・24/24 TRUE = 完成間近で既に手動同期済、想定通り writer が触らない挙動
- **副次成果**: `/jooto-overdue-scan` の `unchecked_checklists` 空バグも同セッション内で自動解消

**`/weekly-report 2026-05-30` フル実行 (new ロジック動作確認)**:

- 出力: [reports/2026-05-30_weekly_update.md] (24 案件全件、27,763 文字) + `state/latest_state.json` (進捗状況あり 9 案件のみ `phase` + `phase_evidence.source: jooto_progress_checklist` + `phase_evidence.checked_milestone`、未設定 15 案件は phase フィールド削除) + `state/latest_summary.md`
- 検証 7 項目すべて期待通り (13 工程グリッドに 9 案件、H3 ブロックに 15 案件、Milestone 遅延 / 直近予定サブ行、`phase_evidence.source` 必須化、フェーズ遷移追記)
- 主要動向 (5-28〜5-29 新規): 中野坂上 着工時金 9,200 万円入金 + 返金 1,200 万円、笹塚方南1丁目 PersGPT パース完成、大森西2丁目 構造キックオフ MTG (5-29 14:00)、駒込駅前 さくら構造担当アサイン + 測量越境物除外修正依頼、中野1丁目 事前申請用構造図書一式送付 + 同日電子申請完了、八幡山六地蔵 地盤改良見積 + 緑化条例樹種確定

**設計 v2 ピボット (5-30 07:17 JST 〜 07:30 JST、user 指摘で受領)**:

- 新前提: **`phase_buckets` = 15 (= Jooto checklist label そのもの)**、`milestone_mapping.yaml` の `milestones` 各エントリは `process_name` (Milestone シート列) と `phase_bucket` (= Jooto label) の **1:1 対応** だけ持つ。`jooto_checklist_label` フィールドは `phase_bucket` と同義になるので統合 (重複排除)。Milestone 列に Jooto signal がないもの (条例チェック / 省エネ申請 / パース承認等) は `phase_bucket: null` で Milestone 期日のみ追跡。**工程軸の進捗グリッドは 13 → 15 行**
- v2 `milestone_mapping.yaml` (`phase_buckets` 15 ラベル) を assistant が起草し、user が「OK、進めて」確認 → 直後 `[Request interrupted by user]` `あ、ちとまって。` で撤回 (5-30 07:23 JST)
- 5-30 07:29 JST user 追加要件: `jooto_task_prefixes` と `fuzzy_search_terms` 復活してほしい (`元々入っていた`)。意味を再定義:
  - `phase_bucket` (15 のうち 1 つ、null 可) = **判定の主軸** (フェーズ = チェック済み末尾の phase_bucket)
  - `jooto_task_prefixes` = カラム関連 Jooto **タスク名** prefix、**判定には使わず残作業ハイライト用補助メタデータ**
  - `fuzzy_search_terms` = 将来用、現状ロジック未使用
- assistant `jooto_task_prefixes` + `fuzzy_search_terms` 復活作業 (yaml のみ、ローダ / writer / テスト / ドキュメントのリファクタは未着手) → user OK 待ちで session 終話

**残タスク (5-30 add-milestone-sync 再開時)**:

- v2 (`phase_buckets` = 15 ベース、補助 3 フィールド復活) で:
  1. `milestones[].phase_bucket` 対応見直し (実 Jooto data から確定済み)
  2. ローダ / writer / テスト / ドキュメントを 15 ベース + 補助 3 フィールド構造でリファクタ
  3. 203 → 同数程度の test 再走 + `openspec validate --strict`
  4. archive (`/opsx:archive add-milestone-sync`) で **13 工程 baseline → 15 工程 baseline へ置換** (`add-phase-progress-view` で 5-29 に確定させた 13 工程要件は今回の archive で上書きされる予定)
- 残 11 tasks (12.5-12.8 ライブ検証 + 12.9 weekly-report + 13.1-13.4 archive) のうち **12.5-12.9 はすでに本セッションで実態 PASS**、archive のみ未消化

- 詳細: [[02_diary/2026-05-30]]
- 関連: [[05_learn/jooto-checklist-items-separate-endpoint]]

### 2026-05-30 add-milestone-sync v2 完成 + Milestone 中間 SoT 統一 + Report v2 構造 (5d8213db 続き、5-30 07:31→14:16 JST、~7h)

session `5d8213db` の後半 (run-57 commit `49e6d1c` で記録した「v2 ピボット pause」以降の 5-30 朝〜昼)。v2 schema を確定させて dual-path writeback 実装 → ライブで 64 セル追加書き戻し成功 → 3 経路目 (PATH 1 fallback) 発見 → **Milestone シートを中間 SoT として writer / reporter を統一**、最後に 5/30 レポートを v2 構造で再生成。

**v2 schema 確定 (`config/milestone_mapping.yaml`)**:

- `phase_buckets` = 15 (Jooto checklist label そのもの)、`jooto_checklist_label` フィールド削除 (`phase_bucket` と統合)
- 補助 3 フィールド復活: `phase_bucket` (判定主軸、null 可) / `jooto_task_prefixes` (Jooto **タスク名** prefix、判定にも使う方針に転換) / `fuzzy_search_terms` (将来用、現状未使用)
- 5-30 07:39 JST user 指摘で **task_prefixes も判定に使う** に方針再設定: phase_bucket が null のセルは task_prefix で補完判定 (それまで「判定には使わない補助メタデータ」と私が誤解していた)

**dual-path writeback 実装 (5-30 07:39→07:48 JST)**:

| Milestone カラム | phase_bucket | 判定ソース | 方向 |
|---|---|---|---|
| 工程系 (例: 仮受、本受、構造着手) | 非 null | `progress_checklist.json` の checklist label | **双方向**（PATH 1 primary、巻き戻しあり） |
| 補助系 (例: 省エネ申請、各種条例チェック、パース承認、基本図初版) | null | `tasks.json` のタスク完了状態 (`startswith(prefix)` × status ∈ `{done,completed,archived}`) | **片方向**（PATH 2、FALSE→TRUE のみ、巻き戻し無し） |

- `application/collect_task_completions.py` 新設、`writeback_milestone.py` に `_path2_entries` 追加、`writeback_cli.py` で両入力を `plan_writeback` に渡す
- 222 tests pass (108 grabber + 74 jooto + 40 writer) + `openspec validate --strict` pass

**🔧 NFKC 正規化 fix (全角 / 半角ミスマッチ)**: Jooto board slug は `FY26_03_千住４丁目`（全角 ４）、projects.csv / Milestone シートは `千住4丁目`（半角 4）→ substring 検索失敗で `skipped_unknown_projects` 行きだった。`unicodedata.normalize("NFKC", ...)` を `_resolve_project_for_board` に追加で **千住 / 滝野川5丁目 / 大森西2丁目** など 10 件相当が正しく拾えるように。dry-run 計画が 54 → **64 セル**に増加

**ライブ書き戻し追加 64 セル成功 (5-30 07:56 JST)**:

- 全件 `FALSE_to_TRUE` / `source_kind: "task_prefix"`、巻き戻し 0、整合性保持
- 進捗状況タスク未設定の 10 案件 (祐天寺 / 高田馬場 / 中野坂上 / 新宿山吹町 / 板橋氷川町 / 山王3丁目 / 江古田江原 / 西巣鴨駅前 / 西荻北1丁目 / 幡ヶ谷不動尊通り) も task_prefix path で書き戻し対象に
- **累計 121 セル TRUE 化** (5-29 の path 1 = 57 セル + 5-30 の path 2 = 64 セル)
- スキップ board: 内部運用テンプレ (バックオフィス / 1課 / 2課 / 牛山への依頼 / 蔡_タスクリスト) + FY25 終了案件 + projects.csv 未登録 (FY26_29 きつね塚通り前) + Milestone シート行と表記差 (中野1丁目) — 全て **正常な不一致**

**🔁 PATH 1 fallback 発見 + Milestone 中間 SoT として writer/reporter 統一 (5-30 09:24 JST、user 追求で発覚)**:

5/30 レポート v2 を生成した時点で **task_prefix で TRUE 化されたセルが工程軸の進捗ビューに反映されていない**事象を user が発見。原因: writer は Milestone を更新するが、reporter は Milestone を見ず `progress_checklist` を直接読んでいた → アーキテクチャの不整合。私の正直な説明 (transcript 引用):

> 「**書き戻し（dual-path）は実装したのに、レポートの工程軸の進捗は別ロジックで progress_checklist を直接見ていて、Milestone 経由を介していない。設計の整合性が取れていません**」

**統一モデルへの修正**:

```
Jooto (progress_checklist + tasks)
    ↓ writer の 3 経路
Milestone シート (実績=TRUE の集合)  ← 中間 SoT
    ↓ reporter
工程軸の進捗 / 進捗状況未設定 (Milestone TRUE 0 件の案件)
```

writer の 3 経路 (v2 完成形):

1. **PATH 1 primary**: phase_bucket != null × checklist label = checked → TRUE (双方向)
2. **PATH 1 fallback** (新規): phase_bucket != null × checklist label = unchecked × task_prefix 完了 → FALSE→TRUE (片方向)
3. **PATH 2**: phase_bucket == null × task_prefix 完了 → FALSE→TRUE (片方向)

- `_path1_fallback_entries()` + `currently_checked_labels` 引数を `plan_writeback` に追加、`source_kind = "task_prefix_fallback"` 新設
- writer 4 tests 追加 → 全 44 test pass

**Report v2 構造変更 (user 指示 5-30 08:27 JST)**:

セクション順序を以下に固定:

```
全体サマリ → 工程軸の進捗 → 進捗状況未設定の案件 → (各案件) → 意匠設計担当の負荷ビュー
```

- 各案件に `- 重要な動き:` を 6 項目めとして冒頭追加 (24 案件全件出力、内容無しは「特になし」明記)
- 旧 `重要な動き ①〜⑧` 連番節を廃止、案件単位に分散
- **全体サマリの責務変更**: 案件単位の業務内容 → ロジック変更点・横串集計 (overdue 件数、Milestone 書き戻し概要、取得状況) のみ
- 進捗状況未設定の案件: H3 サブセクション → 独立 H2 に格上げ
- 条例集約: `- 遅延: 条例 N 件（中高層/景観/清掃局/狭隘/緑化、期日 YYYY-MM-DD）` 形式で 1 行化
- 差分元: `state/latest_*` 既定 → **`reports/2026-05-26_weekly_update.md`** (4 日ウィンドウ)
- 仕様反映先: `config/workspace_defaults.md` / `.claude/commands/weekly-report.md` / `openspec/changes/add-milestone-sync/specs/weekly-report/spec.md`

**🐛 意匠設計担当の負荷ビュー — 機能落ち修正 (5-30 08:13 JST、user 指摘)**:

- 旧 (誤): projects.csv の `key_contact` (本間 / 石田 / 大神 / 蔡 / 比江島 = **社内設計 PM**) を担当扱い
- 新 (正): PM Master Grabber **統合表の `意匠担当` 列** (鈴木 / 中村 / 井上 / 品田 / 小川 / 加納 / 八田 / 中辻 / 功能 / 角田 / 山口 / 坂口 / 森田 / 廣川 = **外部意匠設計士**) を担当扱い、15 担当別の並行案件表示
- ⚠️ 井上: 並行 3 件 (祐天寺 / 江古田江原 / 山王3丁目)、鈴木 / 中村 / 品田 / 小川 / 加納 / 八田: 並行 2 件

**🐛 `/jooto-overdue-scan` 実行漏れ修正 (同上 user 指摘)**:

24 FY26 ボード全件 scan、per-board 実行で 404 回避。FY26 期日超過 5 件:

- 高円寺南5丁目 2 件 (案内図・道路使用 4/30、サッシ・UB 見積 4/24)
- 笹塚方南1丁目 2 件 (♦︎ MM4_本受け 3/31、♦︎ MM6_済証交付 4/27、隣地土地権利関係で PJ 休止中)
- 東日暮里6丁目 1 件 (♦︎ MM2_意匠仮受 5/12、住所表記齟齬で青木氏確認中)

**5/30 レポート v2 構造で再生成 (5-30 14:16 JST、vs 2026-05-26 ベースライン)**:

- 308 行、5 H2 セクション、24 案件全件 `- 重要な動き:` 出力 (28 H2 = 全体サマリ 1 + 工程軸 1 + 未設定 1 + 案件 24 + 意匠 1)
- Milestone-based 工程軸結果: 施主承認 1 / 構造着手 2 / 仮受付 3 / 本受付 1 / 工事着手 2、進捗状況未設定 15 案件
- 期日超過 5/26 比同数 5 件 (継続 4 + 新規 1 東日暮里 + 解消 1 幡ヶ谷本町)
- API Error (socket closed / rate limit) で 2 度中断、再開して着地
- 出力: [reports/2026-05-30_weekly_update.md](reports/2026-05-30_weekly_update.md) (308 行) + `state/latest_*` 反映

**残課題 (次セッション)**:

- `/opsx:archive add-milestone-sync` で 15 工程 baseline 確定 (5-30 朝の archive は v1 ピボット前で停止)
- `workspace_defaults.md` の旧フォールバックロジック (PM master 帯確定 / Jooto タスク名 / Gmail 件名) 説明残存 → 未到達コードなので機能影響無いが将来削除可能
- 「中野1丁目」が Milestone シート行と display_name 不一致でスキップ続行 → PM 確認推奨
- `state/latest_state.json` の旧 13-bucket 名 `phase` フィールド (例: `工事着工`→新 `工事着手`) — 次回 /weekly-report で正される想定

- 詳細: [[02_diary/2026-05-30]]
- 関連: [[05_learn/jooto-checklist-items-separate-endpoint]]

### README システム構成図 (2026-05-28 commit `9310599`)

`/weekly-report` 実行時の各コンポーネント (スラッシュコマンド、プラグイン、外部サービス) とエンティティ (入力 config / データキャッシュ / state / 出力レポート) を Mermaid 図で README.md に追加し、後発の参加者がワークフロー全体を 1 画面で把握できるようにした。session `d13623c3` (5-28 17:40→5-29 07:20 JST、4 turn) で着地。

- **追加先**: `README.md` の「週次実行」と「ディレクトリ構成」の間 (現 `README.md:47` 付近、`## システム構成図（/weekly-report 実行時）`)
- **含めた要素**:
  - スラッシュコマンド: `/jooto-backup` / `/jooto-overdue-scan` / `/pm-master-backup` (事前)、`/weekly-report` (メイン)、`/weekly-report-sync-baseline` (自動先行)
  - ローカルプラグイン: `jooto-grabber` / `pm-master-grabber` / `drive-publisher`
  - 外部サービス: MCP Gmail (read-only) / Jooto API / Google Spreadsheet (案件マスタ) / Google Drive (published Doc)
  - 入力 config: `projects.csv` / `workspace_defaults.md` / `pm_master_mapping.json`
  - データキャッシュ: `data/jooto/` / `data/pm_master/{integration,handover,handover_diff,evaluation}.json`
  - 状態: `state/{latest_summary.md,latest_state.json,batch_progress.json}`
  - 出力: `reports/{run_date}_weekly_update.md`
- **スコープ外として凡例に明記**: `/weekly-report-publish` (HTML + Firebase + Drive 配信) は別 capability のため除外
- **Mermaid subgraph の `()` ラベル問題**: 当初 `subgraph DataCaches[データキャッシュ (.gitignore)]` のように括弧入りラベルをそのまま書いたところ VS Code Markdown プレビュー (mermaid 拡張) が parse error。**`subgraph ID["Label"]` のダブルクォート化が必須** (`(),:` などが衝突する)。全 7 subgraph を統一してクォート版に修正。ノード側 `Name["..."]` は既にクォート済みで無変更
- **VS Code プレビュー**: 標準 Markdown プレビューは Mermaid 非対応。`code --install-extension bierner.markdown-mermaid` を入れて `Cmd+Shift+V` で描画 (`Markdown All in One` 等と共存可)。GitHub 上の README ページは Mermaid をネイティブレンダリングするので push 後にリポジトリページで「実物」確認するのが最終確認手段
- **push**: README.md のみコミット (`9310599 Add system diagram for /weekly-report to README`、`536dddc..9310599 main -> main`)。同セッションの他作業中ファイル (sync-published-doc-before-report 系の `state/*`, `plugins/drive-publisher/scripts/*`) は意図的に含めず
- **06_output 該当判定**: **該当せず** (`meguruit/MeguruPMReport` 内部 private repo precedent 踏襲、README ドキュメント追加は外部公開 evidence なし)
- 詳細: [[02_diary/2026-05-28#17:40  README mermaid システム構成図 (d13623c3, 5-28 17:40→5-29 07:20 JST)]]

### 2026-06-02 22:38 JST: 日次パイプラインがプラグイン短縮形コマンドで「Unknown command」連発 (fe1f5fac / 2e4721dd / 8c7aa96d)

`scripts/daily_pipeline.sh` を 22:38 JST 起動した際、最初の 3 ステップ (`/jooto-backup --all-active` / `/jooto-overdue-scan` / `/pm-master-backup`) が **すべて `Unknown command:` で失敗** し、続けて SessionEnd hook (`/Users/tato/.claude/wiki/hooks/auto-ingest-push.sh`) も `Hook cancelled` で連続失敗。`~/Library/Logs/MeguruPM/2026-06-02.log` の `claude -p '/jooto-backup --all-active'` 行直後に `Unknown command: /jooto-backup` を確認 (`daily_pipeline.sh:113-119`)。

- **原因の有力候補**: 短縮形 (`/jooto-backup` 等) を `claude -p` ヘッドレスで叩いている。対話モードでは短縮形がプラグイン解決される一方、`claude -p` 起動では plugin が hot-load されず namespace 付きでないと解決されない可能性。**2026-04-24 の `2157bb7 Rename plugin to JootoGrabber` リネーム時に観測した症状** ([[05_learn/claude-code-plugin-namespace]]) と同一カテゴリの failure mode
- **本リポの現状** (`scripts/daily_pipeline.sh:113-119`): `claude_p "/jooto-backup --all-active"` 等を **短縮形のまま** 直叩き。`.claude-plugin/marketplace.json` の plugin name は PascalCase (`JootoGrabber` / `PMMasterGrabber` / `PMMasterWriter` / `DrivePublisher` / `MilestoneAlert`) で、namespace 付きなら `/JootoGrabber:jooto-backup` 等
- **観測結果**: 22:38 起動の 3 セッション (`fe1f5fac` / `2e4721dd` / `8c7aa96d`) は **いずれも 1.6-2.1 KB の空転 transcript** (queue-operation 2 件 + local-command-caveat + `Unknown command:` ユーザログ + system message のみ、assistant 応答ゼロ、tool 呼び出しゼロ)。後段の `/weekly-report run_date=2026-06-02` も同パイプラインで起動された (ログ末尾 `→ claude -p "/weekly-report run_date=2026-06-02"`)、本ラン処理時点で session 完了済みかは未確認
- **推奨復旧手順** (本ランでは実施せず、user 判断):
  1. `scripts/daily_pipeline.sh` の 3 行 (`L113-119`) を namespace 付きに置換 — `/JootoGrabber:jooto-backup --all-active` / `/JootoGrabber:jooto-overdue-scan` / `/PMMasterGrabber:pm-master-backup`
  2. 同じく `L125-126` の `/weekly-report` / `/weekly-report-publish` は **プロジェクト固有 slash command** (`.claude/commands/*.md`) なので namespace 不要、現状維持で OK
  3. `claude -p '/JootoGrabber:jooto-backup --all-active'` を手動で 1 回実行して短縮 vs namespace の挙動差を再確認 ([[05_learn/claude-code-plugin-namespace]] に頭書き追加候補)
  4. `~/Library/Logs/MeguruPM/2026-06-02.log` の `weekly-report` 起動行以降を確認して、4-5 ステップ目 (報告書生成 + Milestone alert) が走れたか検証
- **02-06-02 22:38 が定刻起動ではない件**: 当初の LaunchAgent は 9:00 JST 起動の想定だが今回は 22:38。**user が手動で `daily_pipeline.sh` を叩いたか、`com.meguru.pm.daily` の StartCalendarInterval が再設定されたか**は本ラン時点で未確認 (LaunchAgent plist を git 管理外のため、`launchctl print user/$(id -u)/com.meguru.pm.daily` で確認推奨)

> [!warning] auto-ingest-push.sh も連続失敗
> SessionEnd hook も 3 ステップすべてで `Hook cancelled` を吐いている (`Hook cancelled` は hook 内部の `set -e` の早期 abort か、claude 本体側の hook 実行抑止)。`/wiki-ingest` の queue enqueue は別の hook (`~/.claude/plugins-tatoflam/.../enqueue-session.sh`) が担当しているため今回 3 セッションは queue に入った (本ランで処理) が、`auto-ingest-push.sh` 側の連続失敗は別途確認すべき

#### 4-5 ステップ目 (`/weekly-report` + `/weekly-report-publish`) はパーミッション拒否で停止 (821f682c / f1336766)

3 ステップの plugin command 失敗の後、daily_pipeline は **プロジェクト固有 slash command** (`/weekly-report` / `/weekly-report-publish`、`.claude/commands/*.md` で定義のため plugin namespace 不要) で続けたが、別の理由で停止:

- **`821f682c`** (252 KB、31+56 turn、6-02T13:38:46→13:42:57Z): `/weekly-report run_date=2026-06-02` をヘッドレス起動。assistant が backup_cli 系の Bash 呼び出し (`cd plugins/jooto-grabber && PYTHONPATH=scripts python -m interfaces.backup_cli --all-active --force` 等) を試みるが **複数バリエーションが Bash 承認拒否**。途中で「2026-06-02 のレポートは既に 18:25 に生成済み + Milestone writeback 済み + publish 済み (`b1d3925`/`a434093`/`39252eb`)、再実行スコープを 1/2/3 で確認」と user に `AskUserQuestion` し、ヘッドレスで答が無いまま session 終話
- **`f1336766`** (89 KB、21+31 turn、6-02T13:42:57→13:44:48Z): `/weekly-report-publish` をヘッドレス起動。`cd plugins/drive-publisher && PYTHONPATH=scripts .venv/bin/python -m publish --run-date 2026-06-02` を 15 通り近いバリエーション (`source .venv/bin/activate` / `env PYTHONPATH=` / `sh -c '...'` / 絶対パス / `import sys; sys.path.insert(0, ...)` 等) で迂回試行するも **全て Bash 承認で拒否**。「publish コマンドの承認が必要です」で user に approval 要求して session 終話
- **本日の重要観察**: **2026-06-02 のレポート + writeback + publish はすでに今日 18:17-18:25 JST に完了済み** (commit `b1d3925` Add 2026-06-02 weekly update + Milestone writeback 109 cells / `a434093` Refresh 2026-06-02 report after user fixes + writer catch-up / `39252eb` Implement add-writer-catchup-sync)。22:38 起動の daily_pipeline は **冪等性チェック無しで 1〜5 ステップを再実行** しようとして失敗 — 「すでに今日実行済みなら no-op で抜ける」ガードが daily_pipeline.sh または各 slash command 側で必要
- **headless `claude -p` の Bash 承認問題**: `.claude/settings.json` の permission allow-list に存在しない Bash パターンは、headless モードでも user prompt が出るが TTY が無いため即拒否扱いとなる。`cd plugins/drive-publisher && ...` のような複合コマンドは普段 user が対話で承認するパターンなので allow-list 未登録の可能性が高い。修復候補: `.claude/settings.json` の `permissions.allow` に `Bash(cd plugins/drive-publisher:*)` 系を追加する or daily_pipeline.sh 側で `--dangerously-skip-permissions` 付きの `claude` 呼び出しに統一する (現状 22:38 のは標準モード)

- 詳細: [[02_diary/2026-06-02#run-60]]、[[02_diary/2026-06-02#22:55  run-61]]
- 関連: [[05_learn/claude-code-plugin-namespace]]、[[05_learn/wiki-automation-pipeline]]

### 2026-06-02→03 add-daily-milestone-alert + Firebase Functions HTML viewer + LaunchAgent + README diagram split (fbb058f2、~16h)

`/opsx:propose` → `/opsx:apply` で `add-daily-milestone-alert` OpenSpec change を起票・実装し、Milestone シート期日列の日次背景色塗布 + 各案件サマリの Gmail 通知を新規プラグイン `plugins/milestone-alert/` として導入。同セッションで Firebase Functions の HTML viewer 復旧、`daily_pipeline.sh` の 5 ステップ化、LaunchAgent 登録、README システム構成図の縦 2 枚化までを一気通貫で完了 (commit 系列 `5072473` → `39252eb` → `ffab08d` → `47883b5` → `0d373d9` → `cbb967d`、約 16h 散発)。

- **add-daily-milestone-alert** (commit `ffab08d`):
  - `plugins/milestone-alert/` を新規追加 (`pyproject.toml` + Clean Architecture 4 層: domain / application / infrastructure / interfaces)
  - 期日列背景色: 朱 (期日超過) / 橙 (近日中 = `near_threshold_days` 以内) / 白 (正常)。`spreadsheets.batchUpdate` で `updateCells` を発行できるのは milestone-alert のみ、`fields` は `userEnteredFormat.backgroundColor` 単独に限定、`range_guard.py` で `userEnteredValue` 拒絶 (期日テキスト・実績チェックボックス・他シート・ヘッダ行・案件名列は物理的に触らない)
  - Gmail 送信: OAuth User (デフォルト) または DWD (Workspace Service Account 経由) で `users.messages.send`。`/milestone-alert` 以外から `users.messages.send` を呼ぶことは CLAUDE.md で禁則化、MCP Gmail は read-only `search_threads` / `get_thread` のみ
  - 設定: `config/milestone_alert.yaml` (実体は git 管理外、`.example` のみ追跡) で送信元・受信者・閾値・URL テンプレートを定義
  - 監査: `state/milestone_alert_{run_date}.json` に全 Milestone セルの status / before-after color / メール metadata + body 本文 (dry-run 時) / SHA256 (通常実行時) を保存
  - shared 再利用: Sheets/OAuth/マッピング/レイアウト検出は `plugins/pm-master-grabber/scripts/shared/` から import (copy 禁止、`Simplify shared modules` フィードバック踏襲)
- **daily_pipeline.sh の 5 ステップ化** (commit `47883b5`):
  - `1. /jooto-backup --all-active` → `2. /jooto-overdue-scan` → `3. /pm-master-backup` → `4. (条件付き) /weekly-report + /weekly-report-publish` → `5. python -m interfaces.alert_cli --run-date YYYY-MM-DD` (期日色塗り + Gmail 通知)
  - `weekly_report_frequency` を `config/daily_pipeline.yaml` で `daily` / `tuesday_only` / `weekdays_only` / `manual` の 4 モードに切替可能化。コスト最適化したくなったら設定変更のみでコード不要
  - 排他制御は `flock` または macOS フォールバックの `mkdir`-lock。死活監視は Healthchecks.io URL (`healthcheck_urls.base`) で `start` / 成功 / `/fail` の 3 種 ping
- **LaunchAgent** (`com.meguru.pm.daily`):
  - `scripts/install_launchagent.sh` で `~/Library/LaunchAgents/com.meguru.pm.daily.plist` を実体パス展開して登録、`launchctl bootstrap` 経由
  - 起動時刻は当初 user 指示で 8:00 JST、その後 README システム構成図に反映する時に 9:00 JST に変更 (cbb967d 図内に明記)
  - AC 接続のクラムシェル Mac で毎朝発火想定。ログは `~/Library/Logs/MeguruPM/{run_date}.log` に 30 日 rotate (`log_retention_days` で上書き可)
  - テンプレートは `scripts/launchagent.plist.example` のみ追跡 (実体は machine 依存パス展開)
- **Firebase Functions HTML viewer の Internal Server Error 復旧**:
  - `https://meguru-pm-report.web.app/r/2026-06-02` の初回アクセスで 500 → 認証フォールバック (`__session` Cookie + email-domain) と CSS path を修正してデプロイ ([[memory:firebase_auth_pattern]] / [[memory:firebase_first_deploy_iam]] の前提踏襲)
  - 1st Gen Functions の初回デプロイ IAM 3 点はすでに前段で解決済 (memory 参照)、本セッションは Functions コード側の auth path 修正
  - Google Document リンクは初回から正常配信、配信物は `plugins/drive-publisher/scripts/sanitize.py` で契約金額・個人メールアドレスをマスキング済
- **alert メールフォーマット iteration**:
  - 初回出力はフルテーブル → user 要望で **テキストベース + 太字/色/絵文字で要所のみ強調**、スマホ閲覧前提に空白・インデント抑制、文字サイズ・行間は据え置き
  - 条例 5 種 (景観条例チェック / 狭隘協議チェック / 中高層条例チェック / 清掃局チェック / 緑化・雨水対策チェック) を **1 行** に圧縮、`条例チェック(景観/狭隘/中高層/清掃局/緑化・雨水)` 形式、該当のみカッコ内に列挙
  - alert メール末尾に **PM master Sheet URL + 各案件の Jooto board URL** を追記 (commit `0d373d9`)
- **README システム構成図の縦 2 枚化** (commit `cbb967d`):
  - 旧 `flowchart LR` 横長 1 枚 → 新 `flowchart TB` 縦 2 枚 (日次 / 週次に分割) で可読性向上
  - 新コンポーネント (milestone-alert / pm-master-writer / LaunchAgent / Healthchecks.io) を反映、stale な `add-milestone-sync` を `add-daily-milestone-alert` に差し替え
  - 凡例: 「**fbb058f2 (手動)**」: 事前バックアップは日次が朝に済ませる前提で省略可と明記
  - mermaid-cli `v11.15.0` で両図 SVG レンダリング成功確認
- **Gmail API enable の経路ハマり**:
  - 当初 `meguru-pm-report` GCP プロジェクトで Gmail API enable → 403、**`meguru-pm-master` プロジェクト側**で enable し直して通った
  - `/milestone-alert-auth` は milestone-alert 専用の OAuth 同意フロー (spreadsheets + gmail.send の 2 スコープ)、送信元として認証したい user でログイン
- **既知の未解決**: フルセット実行時、Jooto 進捗状況の **「前提整理」** チェックリストが checked なのに Milestone 列にチェックが付かない
  - 当該マイルストーンは `config/milestone_mapping.yaml` で `phase_bucket=null` + `jooto_task_prefixes` 補完経路 (task_prefix path、片方向 FALSE→TRUE のみ) を想定
  - 本セッションでは深掘り未完了、次回フルセット実行時に再現確認 + `state/milestone_writeback_*.json` の dry-run スナップショットで `intended_writes` の有無を見るのが最短
- **06_output 該当判定**: **該当する** (`https://meguru-pm-report.web.app/r/2026-06-02` が GWS ドメイン制限ありの **外部公開 URL** として配信、ただし社外公開ではないため `06_output/2026-06.md` にリンクのみ catalog)
- 詳細: [[02_diary/2026-06-03#12:21  run-64]]、[[06_output/2026-06]]

### 2026-06-02 add-milestone-sync archive + add-writer-catchup-sync 実装 + 2026-06-02 週次 publish (1fca49c1、~3h)

> 時系列メモ: 本セッション (1fca49c1、6-02 15:57→19:00 JST) は **fbb058f2 (6-02 19:03→6-03 11:28 JST) の直前**。順序は 1fca49c1 → fbb058f2 → 66be2df6 で、上記 fbb058f2 entry の冒頭で言及される `b1d3925` / `a434093` / `39252eb` 系列が本セッション由来。

「最新の実装状況を確認して報告して。各種ドキュメントに追いついていなかったら、その旨を報告して、ドキュメントをアップデートして」のドキュメント追従指示で起動し、`add-phase-progress-view` archive 完了 → `add-milestone-sync` archive 化 → 2026-06-02 週次レポートのフルセット実行 → publish 着地 → 「工程軸の進捗」が反映されない件のユーザフィードバックから writer の catch-up logic 不在を顕在化 → 新 OpenSpec change `add-writer-catchup-sync` を起票 + 実装着地まで一気通貫で完了 (commit 系列 `fb643f1` → `ae1fa14` → `887eaf2` → `ccac106` → `45f239f` → `b1d3925` → `a434093` → `5072473` → `39252eb`、約 3h)。

- **archive run 1** (`fb643f1 Finalize archive of add-phase-progress-view`):
  - 既存 archive 状態のファイナライズ。フェーズ遷移 / `phase_evidence` の **MODIFIED Requirements** を `openspec/specs/weekly-report/spec.md` に fold (ADDED Requirements は前ラン `5efbb1c` で merge 済、本ランは MODIFIED の取りこぼし分)
  - change folder を `openspec/changes/add-phase-progress-view` → `openspec/changes/archive/2026-05-29-add-phase-progress-view/` に rename
- **add-milestone-sync 本着地 + archive** (`ae1fa14` 78 files、続けて `ccac106` archive):
  - `ae1fa14 Add add-milestone-sync: Milestone shared layer + progress_checklist + writer plugin` — bulk commit。新規 `pm-master-writer` plugin (Milestone 実績列のみ書き戻し、spreadsheets スコープ、grabber と OAuth トークン分離)、shared layer (`pm-master-grabber/scripts/shared/` の Sheets/OAuth/mapping/Milestone layout 検出)、`config/milestone_mapping.yaml` 24 マイルストーン × phase_bucket / Jooto 信号源
  - `ccac106 Archive add-milestone-sync` — 4 added + 6 modified weekly-report Requirements、3 changed pm-master-grabber Requirements、新 specs `milestone-mapping` (4 reqs) + `pm-master-writer` (合計 12 reqs)。`openspec/changes/add-milestone-sync` → `openspec/changes/archive/2026-06-02-add-milestone-sync/`
  - 本セッション開始時点で実装と spec.md は 5-29/5-30 ランで概ね揃っており、本ランは「最後の archive 化と spec sync」を完遂した
- **2026-05-30 weekly + 状態 補修** (`887eaf2 Add 2026-05-30 weekly update and refresh state snapshots`):
  - `reports/2026-05-30_weekly_update.md` 新規追加 + `state/latest_state.json` / `state/latest_summary.md` を 2026-05-30 に揃え
  - `config/projects.csv` から `FY26_01 高円寺南5丁目` と `FY26_05 渋谷区本町5丁目` を drop (案件終了)
- **設定の現実合わせ** (`45f239f Fill 前提整理 milestone gap and rename FY26_29 to 滝野川きつね塚通り前`):
  - `config/milestone_mapping.yaml` に **「前提整理」** マイルストーン追加 (`phase_bucket = 前提整理`)。これにより Jooto 進捗状況チェックリストのラベル「前提整理」が writer の未マッピング warning を吐かなくなる
  - `config/projects.csv` の `FY26_29` を **「滝野川きつね塚通り前」** にリネーム (Milestone シート側の案件名とのマッチ確保のため)
- **フルセット実行 + 2026-06-02 publish 着地** (`b1d3925 Add 2026-06-02 weekly update + Milestone writeback (109 cells)`):
  - 実行系列: `/jooto-backup --force` → `/jooto-overdue-scan` → `/pm-master-backup` → `/weekly-report run_date=2026-06-02` → `/weekly-report-publish run_date=2026-06-02`
  - 配信物: **Firebase Hosting** `https://meguru-pm-report.web.app/r/2026-06-02/` + **Drive Doc** `https://docs.google.com/document/d/1DwpQTuc1dhvqJcCk8gpbk3_aAEp-yQhIXx4Tw7L4IOM/edit?usp=drivesdk`。両者とも `sanitize.py` で契約金額・個人メールアドレスをマスキング済
  - Milestone writeback **109 セル** (Jooto 進捗状況 → Milestone シート実績列の双方向同期、`a434093` で catch-up 修正前のラウンド)
  - 初回 publish 時点で run-64 の fbb058f2 が後段に SSR Internal Server Error を修正する経緯あり (`[[02_diary/2026-06-03#12:21  run-64]]` 参照)
- **ユーザフィードバック — 「工程軸の進捗」が仕様通り更新されない**:
  - user 発言: 「Jooto の各案件の『進捗状況』タスクのチェックリストのチェック状況を拾う → 工程軸の進捗をレポート上にサマリ + 進捗管理表_master の Milestone シートの各タスクの実績のチェックを書き戻す。Milestone シートのチェックは人手で更新されている場合があるのでチェック済みであればチェックは外さない。としたいんだけど、工程軸の進捗も Milestone シートも更新されていない。なぜ？」
  - 原因究明: writer の PATH 1 は `progress_checklist.json` (curr) と `progress_checklist.prev.json` (prev) の **差分のみを書き戻し** する設計。**前回 backup が無い案件 + 既に Jooto 側でチェック済みの案件は curr=TRUE / prev (空) = 差分なし → 書き戻し対象から漏れる**。これは catch-up logic 不在による仕様バグ
- **「進捗状況未設定の案件」の謎**:
  - user 発言: 「以下は Jooto に進捗状況を追加したつもりだが取得できない: 中野1丁目 / 西巣鴨駅前 / 西荻北1丁目 / 中野区本町5丁目 / 滝野川きつね塚通り前」
  - 原因: (a) `projects.csv` の `滝野川きつね塚通り前` vs `きつね塚通り前` の **case mismatch** (Milestone シート側は「きつね塚通り前」)、(b) Milestone シート側で **「前提整理」列が無い** (user が後段で追加し 25 列化、`a434093` で対応)
- **ユーザ修正後の再実行** (`a434093 Refresh 2026-06-02 report after user fixes + writer catch-up`):
  - user 側の修正: 「前提整理」列を Milestone シートに追加 (24→25 列)、案件名を `きつね塚通り前` に統一
  - report 側: `projects.csv` の名前を `きつね塚通り前` に揃え、`/weekly-report` 再実行で 2026-06-02 report を再生成、writer の catch-up を一旦 PATH 1 で寄せた緊急対応 (後段の `add-writer-catchup-sync` 本実装の前段)
- **新 OpenSpec change 起票** (`5072473 Propose add-writer-catchup-sync`):
  - 提案: writer の PATH 1 を「prev→curr 差分のみ」から「**Milestone 状態 × Jooto curr 状態の状態ジョイン**」に書き換え
  - 書き戻しルール: Milestone FALSE && Jooto curr TRUE のセルを **常に catch-up で TRUE 化**、Milestone TRUE && Jooto curr FALSE は **手動 TRUE 化セル保護** (Jooto 側が curr で意図的に FALSE に戻していない限り巻き戻さない、prev→curr で TRUE→FALSE 遷移したセルのみ FALSE 巻き戻し)
  - PATH 2 (`task_prefix` 経由、`phase_bucket: null` の Milestone カラム) は片方向 FALSE→TRUE のみで不変
- **実装着地** (`39252eb Implement add-writer-catchup-sync: PATH 1 state-join with catch-up`):
  - `plugins/pm-master-writer/scripts/application/writeback_milestone.py` を状態ジョインに書き換え
  - test 追加: `test_writeback_milestone.py` で catch-up + 手動 TRUE 保護 + prev→curr 遷移 TRUE→FALSE 巻き戻しの 3 シナリオを網羅
  - 本 change は本ラン内で propose → apply → 実装 → push の最短ループで決着 (5072473 → 39252eb 直結)
- **MEMORY 追加** (`feedback_weekly_report_full_set.md`、本 wiki vault ではなく `~/.claude/projects/.../memory/`):
  - user 発言: 「今度から、デフォルトでレポート作成して、って言ったら、フルセットで実施するようにしてほしい」
  - 「レポート作成して」のデフォルトを 1〜9 全ステップ (事前 backup / writeback / 再 publish 含む) に変更
  - `MEMORY.md` への索引追加もこのラン内
- **commit 系列**: `fb643f1` (archive 1) → `ae1fa14` (78 files bulk) → `887eaf2` (2026-05-30 + projects drop 2) → `ccac106` (archive 2) → `45f239f` (前提整理 + きつね塚通り前) → `b1d3925` (2026-06-02 weekly + 109 cells writeback) → `a434093` (refresh after user fixes) → `5072473` (propose) → `39252eb` (implement catch-up)、計 **9 commit + 2 push** (`ccac106..45f239f`、`5072473..39252eb`)
- **06_output 該当判定**: **該当する** — 2026-06-02 週次レポートが初回 publish された session。Firebase URL は後段 `fbb058f2` で SSR 修正されたが、**publish 元は本 session (1fca49c1)**。詳細: [[06_output/2026-06]]
- 詳細: [[02_diary/2026-06-04#00:03  run-65]]

### 2026-06-03 PM Report 提案書 HTML 作成 (66be2df6、~50min)

> 時系列メモ: 本セッション (66be2df6、6-03 12:26→13:14 JST) は **fbb058f2 (6-02 19:03→6-03 11:28 JST) の直後**。順序は 1fca49c1 → fbb058f2 → 66be2df6 で、fbb058f2 の commit `cbb967d` で再構築された README システム構成図 (`flowchart TB` 縦 2 枚) を本セッションが提案書 HTML 内に流用。

「Meguru PM Report システムについて、ここまでの構築の内容を初期構築として、提案書を HTML で作成して。ToDoBot システム提案書の目次構成を参考に」で起動。**3 user turn / ~50 min** の短期セッションで初期構築フェーズの提案書を HTML + PDF で生成。

- **出力物 (リポジトリ内、本ラン記述時点では未コミット `?? docs/`)**:
  - `docs/proposal/meguru-pm-report-proposal.html` (43 KB)
  - `docs/proposal/meguru-pm-report-proposal.pdf` (7.5 MB、HTML を Playwright 経由で印刷化)
  - `docs/proposal/img/` (mermaid SVG 同梱、`flowchart TB` 縦 2 枚 = 日次 / 週次パイプライン)
- **構成 (目次、ToDoBot 提案書の骨格を踏襲)**:
  1. エグゼクティブサマリ
  2. 目次
  3. 背景と課題 — なぜ案件情報は分散するのか
  4. ソリューション概要 — Meguru PM Report ができること (システムダイアグラム 2 枚を埋め込み)
  5. 主要機能・要件 — 週次レポート / 期日アラート / Milestone 双方向同期 / 配信 (Firebase + Drive)
  6. システム仕様 — アーキテクチャと技術スタック (Python 3.10 / Claude Code plugin / OAuth / Firebase Functions 1st Gen / LaunchAgent / Healthchecks.io)
  7. セキュリティ・プライバシー — Gmail read-only / Spreadsheet 読み書き分離 (grabber readonly + writer Milestone 実績列のみ) / 配信物のマスキング / GWS ドメイン制限
  8. 開発工数見積 — 時間単位の明細 (本セッション内で **1.2 倍に increase**)
  9. 運用コスト試算 — Claude Code (Opus 1M) + Firebase + GCP (Sheets/Drive/Gmail API)
  10. 想定スケジュールと前提条件
  11. リスクと対策／次のステップ
- **iteration 3 段**:
  1. 初稿生成 (HTML 単体 + PDF)
  2. user 要望「初期構築の開発工数を 1.2 倍程度に明細から増やせる？」→ 明細レベルで全項目の工数係数を再計算
  3. user 要望「README.md のシステムダイアグラムを提案書のソリューション概要あたりに、テーブルのレコード内改行が文字重なるので要修正」→ `flowchart TB` 縦 2 枚 mermaid を HTML 内に埋め込み、`<td>` 内 `<br>` の line-height / padding を増やして重なり解消
- **06_output 該当判定**: **該当しない** — `docs/proposal/` は **未コミット状態** (`?? docs/`、ローカル成果物)、外部 URL 配信なし。コミット + 配信 (社内 PDF メール送信 or Drive 共有) が行われたら [[06_output/2026-06]] への catalog 追加候補
- 詳細: [[02_diary/2026-06-04#00:03  run-65]]

### 2026-06-04 milestone-alert 起動時刻 8:00→9:00 JST + 受信者 4 名 + 本番デプロイ (d56dc1c3、~2min)

> 時系列メモ: 本セッション (d56dc1c3、6-04 23:56→23:58 JST) は **fbb058f2 / 66be2df6 系列の後**。fbb058f2 entry で「起動時刻は当初 user 指示で 8:00 JST、その後 README システム構成図に反映する時に 9:00 JST に変更 (cbb967d 図内に明記)」とあるが、実体は **本セッション (d56dc1c3) で改めて user 明示指示** → コード 5 ファイル + LaunchAgent 実体を 9:00 にデプロイ、という流れ。cbb967d は 6-03 11:28 JST のコミットで diagram 内の表記だけが先行 9:00 化していて、LaunchAgent 実体は本セッションまで 8:00 のままだった。

user 1 turn のみ: 「メール通知の時間を8:00から9:00にしてほしい。あと、メールの宛先をyamlファイルに追加したので、本番デプロイしてもらっていい？」で起動。**2 つの要求を 1 セッションで完結**:

- **要求 1**: 起動時刻 8:00 → 9:00 JST (`milestone-alert` の Gmail 通知時刻 = `daily_pipeline.sh` 全体の発火時刻)
- **要求 2**: `config/milestone_alert.yaml` 受信者追加 → 本番デプロイ

#### 反映 5 ファイル (8:00 → 9:00)

| ファイル | 行 | 変更 |
|---|---|---|
| [scripts/launchagent.plist.example](scripts/launchagent.plist.example) | 32-37 | `<key>Hour</key><integer>9</integer>` |
| [scripts/daily_pipeline.sh](scripts/daily_pipeline.sh) | 2 | ヘッダコメント |
| [scripts/install_launchagent.sh](scripts/install_launchagent.sh) | 55 | 完了メッセージ |
| [scripts/test/test_launchagent_template.sh](scripts/test/test_launchagent_template.sh) | 67-72 | `Hour == 9` アサーション |
| [README.md](README.md) | 5 箇所 | 概要 / セットアップ / 自動実行 / 構成図 / ファイル一覧 |

`git diff --stat HEAD` (本ラン書き込み時点で **未コミット**):
```
README.md                                 |  12 ++--
config/milestone_mapping.yaml             | 106 +++++++++++++-----------------  (別件)
scripts/daily_pipeline.sh                 |   2 +-
scripts/install_launchagent.sh            |   2 +-
scripts/launchagent.plist.example         |   4 +-
scripts/test/test_launchagent_template.sh |   8 +--
```

#### デプロイ手順 (本セッションで実行済)

1. `scripts/test/test_launchagent_template.sh` → **11/11 pass** (`Hour == 9` 新アサーション 1 件含む)
2. `scripts/install_launchagent.sh` で `~/Library/LaunchAgents/com.meguru.pm.daily.plist` を再 render (Hour=9 で展開) + `launchctl bootout/bootstrap` で再ロード
3. `launchctl print gui/$(id -u)/com.meguru.pm.daily` で `"Hour" => 9 / state = not running` (次回発火待ち) を確認

#### `config/milestone_alert.yaml` 受信者追加 (gitignored、デプロイ不要)

- ファイル実体は **git 管理外** (`.example` のみ追跡)、`interfaces/alert_cli` が起動毎に再読込する設計のため **別途デプロイ不要**
- スキーマ検証 (本セッション内で実行) — `plugins/milestone-alert/.venv` の pydantic loader を直接 invoke:
  - `email_from` = developer1 (= ログイン中の OAuth ユーザ)
  - **受信者 4 名**: togami-log / design / tkasuya / mashikaya
  - `max_recipients=10` 以下 (4 ≤ 10)、`gmail_oauth_mode=oauth`

#### 次回発火と挙動確認

- **明日 2026-06-05 09:00 JST** に LaunchAgent 自動発火 → `daily_pipeline.sh` 5 ステップ → step 5 で `interfaces.alert_cli` が 4 名へ Gmail 送信
- **即時挙動確認**: `launchctl kickstart -k gui/$(id -u)/com.meguru.pm.daily`

#### 未コミットの 5 ファイル (追跡)

本セッション末尾時点で、user 明示の `commit/push` 指示がないため commit は走らせていない。`scripts/launchagent.plist.example` / `scripts/daily_pipeline.sh` / `scripts/install_launchagent.sh` / `scripts/test/test_launchagent_template.sh` / `README.md` の 5 ファイルが **本番ファイルは 9:00 化済だが git は 8:00 のまま**。次の commit (`feat: switch LaunchAgent schedule 8:00→9:00 JST` 相当) で reconcile される想定。`docs/proposal/` (66be2df6 由来) も同じく未コミット状態のまま。

#### `06_output` 該当判定

**該当しない** — 起動時刻変更は内部 LaunchAgent 設定の変更で、外部 URL 配信なし。社内 Gmail 送信は明日 9:00 の発火結果待ちで、メール送信が実際に走ったら [[06_output/2026-06]] に catalog 追加候補

#### 関連 memory フィードバック

- 本セッションは 1 turn の短いタスクで [[memory:feedback_long_running_commands]] (フル `/weekly-report` は次回の自然な実行で検証) には抵触しない、`launchctl kickstart` で即時テスト可能
- 詳細: [[02_diary/2026-06-04#23:58  run-66]]

### 2026-06-05 milestone_mapping yaml cleanup 整合性検証 + daily_pipeline.sh data dir bug 修正 + LaunchAgent 8→9 / yaml cleanup の 2 commit push (00db3a35、~30min)

> 直前の d56dc1c3 (run-66 entry) では LaunchAgent 8→9 反映 5 ファイルが **未コミット** で残っていた。本セッション末尾で **`b7f5097` LaunchAgent: bump daily fire time from 08:00 to 09:00 JST** として 1 commit に切り出し + push。実体は run-66 で配置済 / 本セッションで git 反映、の 2 段構え。

user 起動: 「milestone_mapping.yaml について、スプシに列は残っているけど、一部の process をコメントアウトした。このようにしても、backup, 実績チェック付、遅延/期日近いチェック、工程軸の進捗状況レポート、メールレポート、それぞれ整合性をとって動く・・？」

#### Phase A: yaml comment-out 整合性の机上回答

5 サブシステム (backup / writeback / alert / weekly-report / メール) について、`detect_layout()` の完全一致スキャンを起点に「コメントアウト列は素通り、エラーにはならない」と回答。**唯一手動クリーンアップ必須なのは alert の背景色** — alert が触らなくなるので、コメントアウト時点で朱/橙のセルは永久に塗り替わらない → 一度白に戻す必要あり。詳細は [[05_learn/milestone-yaml-comment-out-behavior]]。

`仮受（意匠・構造）` → `仮受（意匠）` のリネームは別問題で、スプシ側のヘッダ文字列もリネーム後に揃える作業が必須 (`detect_layout()` 完全一致のため)。

#### Phase B: クリーンアップ後フルセット 1 周 (メール除く)

user「クリーンアップは実施したので、メール通知を除くフルセットを一度回してテストしてみて」

実行: `/jooto-backup --all-active --force` → `/pm-master-backup` → writeback dry-run → alert (`--skip-email`)

検証 OK:
- layout detection: 15 process columns 検出、`仮受（意匠）` も検出
- commented-out リーク: writeback / alert snapshot ともゼロ
- writeback PATH 1: `cells_planned: 0` (prev==curr 同期済)
- writeback PATH 2: コメントアウトで該当エントリ消滅 → 元から no-work
- alert color: 360 セル走査 / 360 更新 / `hash_drift: []` / 20 overdue + 9 upcoming
- 色分布: done 195 / future 72 / not_applicable 64 / overdue 20 / upcoming 9

#### Phase C: テスト中に **`daily_pipeline.sh` data dir bug** 発見

実行途中で「データの出力先がズレている」ことに気付き、リカバリ実行。

**root cause** ([scripts/daily_pipeline.sh:122-125](scripts/daily_pipeline.sh#L122-L125)):
Step 1 (`/jooto-backup`) が `cd plugins/jooto-grabber` 後に `--output` 未指定で `backup_cli` を呼んでいたため、デフォルト相対パス `data/jooto` が **`plugins/jooto-grabber/data/jooto/`** に解決。一方 downstream (`pm-master-writer` / `milestone-alert`) は `shared/repo_paths.py` 経由で `$REPO_ROOT/data/jooto/` を読む → **書き込み先と読み込み先が食い違い**。

影響:
- repo root の `data/jooto/` 最終更新が **2026-05-30** で固定 (LaunchAgent は 06-02/03/04 と 9:00 に正常起動していたが、書き込み先は plugin 内ディレクトリだった)
- 本セッションでは `--output data/jooto` 明示指定で再実行してリカバリ

修正 ([scripts/daily_pipeline.sh:121-152](scripts/daily_pipeline.sh#L121-L152)):
```bash
# Step 1: jooto-backup
PYTHONPATH=scripts .venv/bin/python -m interfaces.backup_cli \
  --all-active --force --output "$REPO_ROOT/data/jooto"

# Step 2: overdue_cli per-board ループ
... --output "$REPO_ROOT/data/jooto"
```

検証:
- `bash -n` syntax OK
- `scripts/test/test_daily_pipeline_dry.sh` 20/20 pass (既存 substring match は `--all-active --force` / `--board <id>` を残したので壊れない)
- 実 LaunchAgent の回帰確認は、**2026-06-05 09:00 JST** の自動実行翌朝に `data/jooto/{board}/progress_checklist.json` の `fetched_at` が当日分かで確認

メール送信込みのフル実行は `--skip-email` フラグが daily_pipeline.sh に無いため避けた (LaunchAgent 待ち)。

#### Phase D: 2 commit に分割して push

user「OK. ここまでの変更を commit, push しておいて」 → 2 つの論理コミットに分割:

- **`b7f5097`** `LaunchAgent: bump daily fire time from 08:00 to 09:00 JST` (run-66 で配置した 5 ファイル分の git 反映)
- **`5b07ca6`** `milestone_mapping: prune unused processes; daily_pipeline: pin --output to repo-root data/jooto` (yaml cleanup + data dir fix)

`docs/` untracked (66be2df6 由来の proposal PDF/HTML + img) はセッション範囲外として除外。

#### MEMORY 追加

- `project_daily_pipeline_data_dir_bug.md` — 本バグの memory 化 (MEMORY.md の `- [daily_pipeline data dir bug]` 行に対応)

#### `06_output` 該当判定

**該当しない** — GitHub push (2 commits) は内部リポジトリへの反映で、本ファイルが追跡している「外部 URL 配信」(Firebase Hosting + Google Drive Doc) には該当しない。次回 9:00 発火で alert メール送信が成功すれば [[06_output/2026-06]] catalog 追加候補。

## Links

- [[02_diary/2026-04-24]]
- [[02_diary/2026-04-25]]
- [[02_diary/2026-05-08]]
- [[02_diary/2026-05-15]]
- [[02_diary/2026-05-19]]
- [[02_diary/2026-05-23]]
- [[02_diary/2026-05-27]]
- [[02_diary/2026-05-28]]
- [[02_diary/2026-05-29]]
- [[02_diary/2026-05-30]]
- [[02_diary/2026-06-02]]
- [[02_diary/2026-06-03]]
- [[02_diary/2026-06-04]]
- [[02_diary/2026-06-05]]
- [[05_learn/jooto-checklist-items-separate-endpoint]]
- [[05_learn/milestone-yaml-comment-out-behavior]]
- [[05_learn/ssh-agent-shortcuts]]
- [[05_learn/gmail-mcp-reauth]]
- [[05_learn/gmail-search-threads-message-limit]]
- [[05_learn/google-sheets-multi-row-header]]
- [[05_learn/claude-code-plugin-namespace]]
- [[05_learn/fy-cycle-mmdd-year-inference]]
- [[06_output/2026-04]]
- [[06_output/2026-06]]
