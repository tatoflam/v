---
title: BusinessCurator — Bizuayeu 内サブプラグイン (ビジネスメール分類 + Jooto 連携)
category: 03_work
tags: [project:businesscurator, client:meguru, tech:claude-code-plugin, tech:claude-haiku, tech:jooto-api, stage:active]
sources: [058e8848-56aa-4282-a2bb-bd0d0b5dc7d2, ca3a5ff9-dd61-4cbe-b4ab-b36d6386bc7a, a82cc1b4-b04e-40ea-9eec-5526be8c0427, 58f9d0af-6091-4b1c-b4ec-d1f2c8300d55, 74fc50a0-62eb-40e0-9f3f-554c6f7f8925, 4e8bad14-1db8-409c-9698-deea96288d16, d4906d57-fd4c-4e33-abbb-1124556194f6, 37bb2fd3-3936-4e72-9976-3b93fdcaf998, c08eb6b9-9091-48d0-a77e-fa8b2693ef87, bbf488b5-2ce3-40ed-b80e-e1cbabd1f8f8, 72c4e690-0e3b-402e-8341-c92fbc0b66d8, 65586b9e-09a5-4518-b3d6-2fa43c542b34, 6e93de69-9d16-4d8c-8e6f-3759e7750972, 880c3f39-714e-47c7-988a-9cf79ee66087, 974373ab-840d-41cb-b3cb-9ae4d5ea5d8e, fd984dc7-6563-457a-8981-6df4cef1f115, 06e3b108, ea84cf74, b364b8d8, 5eae1ddb, dd27bc9b, 40974924, 39d1cb69, 011bc332]
updated: 2026-06-16
---

# BusinessCurator

## Summary

Bizuayeu 配下のサブプラグイン (= `Plugins-Bizuayeu/BusinessCurator`)。
めぐる組業務メールを自動分類して
Jooto ボード等のワークフロー基盤に流す業務エージェント群を提供する。
2026-06 時点ではブランチ `jooto-integration` で **JootoGrabber**
(Jooto API 経由のボード読み取り/差分同期) + **jooto-absorb** スキル +
**/wiki-jooto-absorb** コマンド が育成中。

## Details

### 構造

- **リポジトリ**: `~/repo/github/Bizuayeu/Plugins-Bizuayeu/BusinessCurator` (現在 `jooto-integration` ブランチ)
- **親プラグイン bundle**: `Plugins-Bizuayeu`
- **サブモジュール群** (本リポ内):
  - **GmailGrabber** — Gmail OAuth + 検索クエリ + .eml/.mbox バックアップ + Service Account + DWD で Workspace 複数ユーザー一括 (see [[05_learn/gmail-mcp-reauth]])
  - **JootoGrabber** — Jooto API でボード一覧/バックアップ/差分同期 (Stage 1-3)
  - **jooto-absorb** スキル — Jooto から取り込んだ JSON を解析しめぐる組フロー側に取り込む
  - **PMMasterGrabber** — PM マスタスプレッドシート (統合表/申し送り/案件評価) を JSON で吸い上げる

### ビジネスメール分類エージェント (= LLM サブエージェント 1ターン分類)

BusinessCurator は受信メールを 4 カテゴリへ Claude サブエージェントで分類する:

| カテゴリ | 用途 |
|----|----|
| `projects` | 案件特定 (具体的な現場・成果物に紐付くメール) |
| `clients` | 顧客 / 営業コミュニケーション |
| `vendors` | 仕入先 / 下請 (購買・協力会社) |
| `knowledge` | 一般知識 / 規制 / 標準 |

呼び出しパターン: 1 メールにつき 1 サブセッション = 「Classify the following business email
into ONE of these categories: ... Return ONLY the category name (one word, lowercase). No
explanation.」 をプロンプトに添付、回答は 1 語 (= モデル: 短文応答に向く小型クラス、cwd は
`Plugins-Bizuayeu/BusinessCurator`)。各サブセッションは Claude Code SessionEnd フック経由で
`~/.claude/wiki/state/queue.jsonl` に enqueue されるため、`/wiki-ingest` で観測される。

### 2026-06-16 に分類された 4 メール (= run-89 で観測)

- 山口特許事務所宛「特許出願希望 (Vaccinium属花芽を原料とする立体的物理処理による茶外茶製造方法)」
  発信 (大神→山口) → **knowledge** (ブルーベリー花芽の茶外茶製造方法、知的財産系)
- 山口特許事務所からの受領返信 → **knowledge**
- 山口特許事務所からの内容コメント返信 (圧延処理量 A × 毫鍼貫入処理量 B の組合せの根拠文献を問う技術論) → **vendors**
- めぐる組お問い合わせフォーム経由の新規見積依頼 (石本様、建物見積) に対する大神様返信 (イラン情勢
  リスクで新規受注見合わせ + 自己資金条件提示) → **clients**

= **分類器の通常運用 4 件 (1 セッション = 1 メール、各 2 ターン)**。
業務的にはブルーベリー花芽の茶外茶製造方法特許出願ワークフロー + 新規見積お断り
ワークフローが今日走った、という業務イベント観測。

### 2026-06-16 追加バッチ (= run-90/91 合算で 20 件処理、累積本日 24+ 件)

run-89 直後 (UTC 06:46-06:52 = JST 15:46-15:52) に Claude Code SessionEnd
フックがほぼ秒単位連続で大量 enqueue (90+ 件)。これを 2 run で消化:

- **run-90 (auto-worker 起動、15:55 JST)** — 5 件 finalize (run-89 の partial write
  の queue/cursors 確定) + 7 件 classifier-drain。詳細表 = [[02_diary/2026-06-16#15:55 JST  run-90]] の H2
- **run-91 (user 手動起動、15:48-15:54 JST、本ラン)** — run-90 と並走、追加で 13 件
  classifier-drain (うち 1 件 974373ab は wiki-ingest-meta noop)

| 分類 | 件数 (合算) | 主なテーマ |
|----|----|----|
| `knowledge` | 8 | 請負契約書雛形更新 (5)、メール通知系 (2)、Vaccinium特許コメント (1) |
| `vendors` | 5 | Vaccinium 特許 (2)、Proforma Invoice / YG381 Projectors (1)、設計業務アンケート (1) |
| `projects` | 4 | 板橋氷川町建築測量 (2)、滝野川5同意書、Proforma Invoice (誤分類?) |
| `clients` | 2 | 設計業務アンケート (1)、めぐる組お問い合わせフォーム経由石本様 (1) |
| `wiki-ingest-meta` | 1 | 974373ab (early /wiki-ingest noop、"Both queue and inbox are empty") |

本日アクティブなメール系統:
- **板橋氷川町建築測量依頼** (新案件、`projects` 分類で 2 セッション)
- **Vaccinium 属花芽 (ブルーベリー花芽) 茶外茶製造方法特許** (run-89 から継続、4 セッション、`vendors`/`knowledge` を行き来 = 山口特許事務所とのやり取り)
- **請負契約書雛形更新** (社内/外部の標準化、5 セッション、すべて `knowledge`)
- **YG381 Projectors Proforma Invoice** (海外ベンダ調達、3 セッション)
- **滝野川5 同意書 (蜷川様)** (`projects`、住民交渉関係)
- **設計業務標準化アンケート** (業界調査、2 セッション)
- **石本様お問い合わせフォーム** (run-89 のお断りフローへ向けた `clients`)

= **本日累計 24+ 分類イベント / 89+ enqueued (run-90 終了時 90 unprocessed)**。
1 セッション = 1 メール = 2 ターンの noop パターンが queue を支配。
分類精度は概ね妥当だが「Proforma Invoice」が `projects` に分類された 1 件は
本来 `vendors` が適切と思われる軽微な揺らぎ。

> [!note] 個別メールの subject だけ載せる方針
> 各 enqueue session の本文 (差出人・本文・添付) は wiki に転記しない。
> 1 メール = 1 業務イベントだが、長期 PKM の観点では「テーマ × 頻度」が
> あれば十分。詳細 audit は `~/.claude/wiki/state/ingest-log.jsonl` を参照。

### 関連スキル / 連携

- `/wiki-jooto-absorb` (Plugin-Bizuayeu 側で公開) — Jooto から吸い上げた JSON を BusinessCurator の
  スキーマに正規化して wiki 側に展開する経路 (= [[03_work/meguru-pm-report]] と
  [[03_work/yahatayama-rokujizo]] の補助線)
- [[03_work/meguru-pm-report]] — Jooto 26 ボード本番、本プラグインは「読み取り」専担
- [[05_learn/jooto-checklist-items-separate-endpoint]] — Jooto API のチェックリスト要素は別エンドポイントの gotcha

## Links

- [[03_work/meguru-pm-report]] — 親業務 (Jooto 上の 26 ボード = めぐる組 PM 業務本体)
- [[05_learn/jooto-checklist-items-separate-endpoint]]
- [[05_learn/gmail-search-threads-message-limit]]
- [[05_learn/gmail-mcp-reauth]]
- [[02_diary/2026-06-16]]
