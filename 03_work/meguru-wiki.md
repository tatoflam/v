---
title: MeguruWiki — Bizuayeu 配下の中央ナレッジ Vault (project / team / vendor / knowledge shards)
category: 03_work
tags: [project:meguru-wiki, client:meguru, tech:claude-code-plugin, tech:python, tech:jooto-api, tech:gmail-api, tech:obsidian, stage:active]
sources: [0d974a46-909d-4bee-83e2-8885c1196a89]
updated: 2026-06-25
---

# MeguruWiki

## Summary

Bizuayeu (= 株式会社めぐる向け Claude Code プラグイン基盤) 配下の **中央ナレッジ Vault** (= `~/repo/github/Bizuayeu/MeguruWiki/`)。case-shard 形式で project / team / vendor / knowledge を独立ファイルとして管理し、JootoGrabber / GmailGrabber からの自動吸収 + LLM 駆動の `/wiki-jooto-absorb` / `/wiki-absorb` skill 群で日次更新する。本ページは 2026-06-16 の大規模 Gmail 統合 + Jooto 再吸収 + MeguruPMReport 側への OpenSpec 引き継ぎを記録する。

## 2026-06-16 大規模 Wiki 最新化 + Gmail 統合 + OpenSpec 引き継ぎ (session 0d974a46、1 日跨ぎ、9 commits)

User 起点「ローカルで wiki を最新化したい」を受け、Jooto 再吸収 → Gmail 認証統合 → メール大量吸収 → 知識シャード反映 → 統合運用 OpenSpec 引き継ぎ、まで一気通貫で完了。最終 `main` は **`origin/main` から 9 commits ahead** (user が手動 push 予定)。

### Phase 1: Jooto 再吸収 (commits `bf55fb5`, `30a8e9c`)

- `JootoGrabber/scripts/interfaces/backup_cli.py --all-active` で **20 ボード更新 / 26 不変** (4/16 以来 ~2 ヶ月分の差分)
- スキル方針「**勝手に新規 project を起こさない**」に従い `_alias_resolver.md` ベースで分類:
  - 既存 project shard 更新: **12 件** (高円寺南5丁目 / 渋谷区本町5丁目 / 中野坂上 / 高田馬場 / 新宿山吹町 / 山王3丁目 / 中野区本町5丁目 / 東尾久4丁目 / 東向島5丁目 / 多摩川1丁目 / 西大井6丁目 / 恵比寿三田1丁目)
  - 既存 team shard 更新: **2 件** (Div1Ka, SekkeiPMTemplate)
  - 新規 team shard 作成: **1 件** (SaiTasks)
  - **5 件 ambiguous** → `inbox/unclassified/` 退避 (.gitignored)
- 副次修正: `Koenjiminami5Chome` の malformed orphan `last_synced:` frontmatter 行除去 + dry-run で空行混入バグ解消
- 残存 1 件 `inbox/unclassified/jooto-1294167.md` (FY26_21 江古田江原) → user 指示で `NakanoEhara3Chome` にマップして commit `30a8e9c`

### Phase 2: GmailGrabber Cloud プロジェクト統合 (option B)

**現状の Cloud project 分散の発見**:

| Cloud プロジェクト | 使用プラグイン | 用途 |
|---|---|---|
| `meguru-pm-master` | milestone-alert / pm-master-grabber / pm-master-writer | Sheets r/w + Gmail send |
| `meguru-pm-report` | drive-publisher | Drive 書き込み |
| `orbital-caldron-455606-d6` | GmailGrabber (5/22 設定) | Gmail 読み取り |

→ MeguruPMReport 側は 3 plugin が `meguru-pm-master` 共有、GmailGrabber だけ完全分離。`gmail.readonly` scope は **どこにもなく** (`gmail.send` ≠ `gmail.readonly`、scope 混同の整理が必要だった)。

選択肢 (A) 現状継続 / (B) `meguru-pm-master` への統合 → user 選択 **(B)**:

1. Cloud Console で `meguru-pm-master` の OAuth 同意画面に `gmail.readonly` scope 追加 (UI 改装で「アプリを編集」ボタン場所が変動、user 側で対応)
2. `meguru-pm-master` の `client_secret.json` を symlink で参照
3. `orbital-caldron-455606-d6` 配下の旧 client は不要化

### Phase 3: Multi-User Gmail 認証 (3 アカウント分の使い分け)

User の 3 アカウント体制を整理 → 方式振り分け:

| アカウント | 正体 | 認証方式 |
|---|---|---|
| `thomma@meguru-construction.com` | user 本人 | **個人 OAuth** (`token_thomma.json` 生成) |
| `togami-log@meguru-construction.com` | GWS グループアドレス (本人参加) | thomma OAuth + `to:togami-log@` Gmail 検索で間接取得 (Groups は Gmail API で直接読めない仕様) |
| `hishida@meguru-construction.com` | 別人 (役員) | **Service Account + DWD** (user は Super Admin、Admin Console で domain-wide-delegation 登録) |

SA key: `~/.config/gmailgrabber/sa-key.json` (600)、Client ID `118121602385730379920` を Admin Console で DWD 登録 → impersonation で本人ノータッチで取得可能。

→ `/gmail-multi-backup` で 1 コマンド全アカウント横断、**RFC5322 Message-ID で自動 dedup** (CC 配信の二重取得防止)。

### Phase 4: メール大量吸収 (commits `bdc2fa5`, `3d84860`, `2fd9f78`, `9de7a02`, `31853e2`, `15ab29d` — 計 6 commits、1,005 emails 吸収)

**Production fetch 結果** (hishida 受信箱 1 ヶ月 + thomma 経由の togami-log 1 ヶ月):

- 取得: 1,643 件
- `_alias_resolver.md` rule_match: 1,147 件 (68%)
- unclassified: **496 件** (= 残 = 32%)

並列 subagent (`/wiki-absorb-shard`) で project / team / vendor / knowledge 系シャードに吸収:

| バッチ | 内訳 | エントリ数 |
|---|---|---|
| Top 5 projects (`bdc2fa5`) | Higashinippori6Chome 97 / SetagayaOhara 102 / NishisugamoEkimae 69 / HachimanyamaRokujizo 64 / HatagayaHoncho 139 | 471 |
| Large projects (`3d84860`) | HatagayaFudosonDori 37 / Takinogawa5Chome 55 / NakanoEhara3Chome 38 / SasazukaHonan1Chome 42 / HigashiNagasaki4Chome 64 / ShinjukuYamabukicho 50 | 286 |
| Medium projects (`2fd9f78`) | SumidaNarihira3Chome 23 / Yutenji 24 / NakanoSakaue 19 / Omorinishi2Chome 19 / Takadanobaba 20 / KomagomeEkimae 30 | 135 |
| Small projects (`9de7a02`) | Senju4Chome 17 / Nakano1Chome 15 / ShibuyaHoncho5Chome 10 / ShinjukuNishiwaseda 11 / Sanno3Chome 15 / NakanoHoncho5Chome 12 (1 stall→retry) | 80 |
| Tiny projects + vendors (`31853e2`) | Koenjiminami5Chome 2 / Nishiogikita1Chome 1 / TakaoyamaProject 2 / HigashiOgu 9 + Iandf vendor 6 / SakuraKozo vendor 5 + EbisuMita 10 | 33 |
| Knowledge shards (`15ab29d`) | DesignStatusUpdate 3 / StructuralDesign 3 / LandAcquisition 5 / DrawingManagement 3 / BuildingCodes 77 (= 3 新規 topic 派生: EnergyStandardSpec / EnergyComplianceMinorChange / GreeningOrdinance) / DailyReport 49 | 140 |

→ 全 `_index.md` で **既存 Jooto セクション保持** + alias_resolver 更新 + frontmatter `last_synced` 更新まで揃った。

### Phase 5: LLM triage on unclassified (550 → 56 signal)

unclassified 550 件に対し `triage_cli` (rule fallback として `claude -p` subprocess、~50–100 分想定の background 起動) を実行 → **56 件で signal 検出**、ただし全て `primary_slug=None` (= 「案件メール」とは判定したが「どの案件か」は未確定):

- projects/None: 25 / vendors/None: 15 / knowledge/None: 13 / clients/None: 3

→ 残 494 件は CG 納品自動通知 / システム配信 / 部署内 / 空本文返信などのノイズ。subagent 合計トークン消費 ~3.3M。

実行は途中で **SessionEnd hook の v vault 側 push 失敗 → ScriptStopper 連鎖** で停止 (= triage 自身は完走、停止は副次フックの問題)。

### Phase 6: PMReport ↔ MeguruWiki 統合運用の OpenSpec 引き継ぎ (commit `a113f3b` on MeguruPMReport)

User 提案「**PMReport の更新と MeguruWiki の更新を一体化した運用を行いたい**」を受け、4 つの統合シナリオ (I 統合せず維持 / II Wiki 側に寄せる / III PMReport 側に寄せる / IV ハイブリッド) のうち **IV 案 (主導 = MeguruPMReport、OpenSpec で 3 phase 設計)** を選択。MeguruPMReport の `openspec/` 配下に **3 つの change を新規追加**:

| Change | パス | 役割 |
|---|---|---|
| **Phase 1** | `openspec/changes/add-triage-routing-enrichment/` | rule_match 後の unclassified を Wiki の `_alias_resolver` に LLM-driven で fold |
| **Phase 2** | `openspec/changes/consolidate-grabber-plugins/` | Jooto/Gmail grabber を MeguruPMReport 側へ統合 (重複実装解消) |
| **Phase 3** | `openspec/changes/add-wiki-absorb-orchestration/` | weekly-report run の延長として Wiki 吸収を orchestration |

全 3 change `openspec validate --strict` ✅、MeguruPMReport の他作業 (uncommitted 残あり) に触れずに 3 change のみ commit。

### 観測

- subagent stall (NakanoHoncho5Chome 12 件で 600s no-progress) は retry で復旧 = 並列 LLM 駆動の典型的なフレーキ
- `inbox/absorbed/` (吸収済みメール raw cache) は agent 副次産物のため `.gitignore` に追加 (`b844a3a`)
- Cloud project 統合 + OAuth scope 整理は **新 plugin 開発時の初手 chcek list として有効** (`gmail.send` ≠ `gmail.readonly` 混同問題は再発しがち)

## Links

- [[03_work/meguru-pm-report]] — OpenSpec 3-change の引き継ぎ先 + 統合運用の主導側
- [[03_work/yahatayama-rokujizo]] — HachimanyamaRokujizo 64 件吸収先 (= 同一案件)
- [[03_work/businesscurator]] — Bizuayeu 配下の姉妹プラグイン (BusinessCurator) との分担
- [[02_diary/2026-06-16]]
- [[memory:project_wiki_system]]
