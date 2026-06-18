---
title: BusinessCurator — Bizuayeu 内サブプラグイン (ビジネスメール分類 + Jooto 連携)
category: 03_work
tags: [project:businesscurator, client:meguru, tech:claude-code-plugin, tech:claude-haiku, tech:jooto-api, stage:active]
sources: [058e8848-56aa-4282-a2bb-bd0d0b5dc7d2, ca3a5ff9-dd61-4cbe-b4ab-b36d6386bc7a, a82cc1b4-b04e-40ea-9eec-5526be8c0427, 58f9d0af-6091-4b1c-b4ec-d1f2c8300d55, 74fc50a0-62eb-40e0-9f3f-554c6f7f8925, 4e8bad14-1db8-409c-9698-deea96288d16, d4906d57-fd4c-4e33-abbb-1124556194f6, 37bb2fd3-3936-4e72-9976-3b93fdcaf998, c08eb6b9-9091-48d0-a77e-fa8b2693ef87, bbf488b5-2ce3-40ed-b80e-e1cbabd1f8f8, 72c4e690-0e3b-402e-8341-c92fbc0b66d8, 65586b9e-09a5-4518-b3d6-2fa43c542b34, 6e93de69-9d16-4d8c-8e6f-3759e7750972, 880c3f39-714e-47c7-988a-9cf79ee66087, 974373ab-840d-41cb-b3cb-9ae4d5ea5d8e, fd984dc7-6563-457a-8981-6df4cef1f115, 06e3b108-1081-44b6-9a40-7c8bd1e71a13, ea84cf74-4e4e-4454-a108-cc39e7d6c09b, b364b8d8-0983-4da9-8292-53c0171ac66f, 5eae1ddb-cd7e-4291-b964-d92bd0eff9d0, dd27bc9b-c444-4b40-bcf3-0914e5c51760, 40974924-d66c-4f0b-808c-f04991063b1a, 39d1cb69-ed21-41c0-b7f8-2d17150c2150, 011bc332-3010-490f-9122-8f58e7c37118, 729fe121-ab65-49ea-9d56-d878664a9e69, c5dba373-64a7-4e4c-86bf-fdf45340f004, 0803e68e-bdbe-4ec3-93a1-a26e7b0370d7, 4499d03b-e039-4215-8008-02d5248ddcfd, c48f50c0-ab15-4d48-a547-b02084d49a24, 1cdc0882-4779-49dd-b450-92fd703b5d9a, c86b8167-1e96-456b-a179-c65f3cede96d, 8f6d8fb9-2108-4358-a8bb-f1e9e31264b4, 648f5d13-61ab-4306-9bfb-95c36a9b2537, 9ac351ac-8ed3-4400-bb56-33eef1ef5a44, 667253d4-09b4-423c-b494-8711b11690cc, 41802c05-47fd-4ae9-a4d6-5f069edcd71a, c280f2d6-6a37-4949-bb09-56d8cf5c5ac7, 14ad7061-ccb9-465a-a086-0dfbc3d04302, 46797fb0-c74f-4336-ac69-42ecc282264e, c822b1ac-71a5-419d-aa11-eb13969ec640, bf62dcf6-22c2-452f-af70-02ea7751a413, dbbb6604-8bde-41b2-b166-59ea66846352, 09bd811a-c976-457b-8b6d-1fe4d3cb1a58, f5137167-7504-4bbb-a266-cf6c7bab142f, b175f6b0-2fde-4aa7-bcac-de7b05e63ead, 1960877f-499b-4ee2-8fc4-220384314830, 139bb9bb-84c0-4af6-8314-d9bfed84c838, 94b63a5c-8b75-4202-a72e-4bbda25b684b, 8bd54ac5-8253-4e89-a30e-379d273eaf58, c79b85cc-46e9-40b3-9704-6996402654d6, 8ce7c561-18ed-46be-b8db-2373dbfbecd1, d3a47fdf-d321-4c72-a7ac-7f9788aab1ca, fad288bf-7801-4310-83f2-9b2ed3f95411, 637dd424-df69-41e5-b611-cf634e23fa21, c6330593-0ed4-4fa2-a031-7596bcf7394b, c9f4a2f8-6931-4e81-bae8-ef8efa1b277f, edb2f4bb-0ef1-4a1d-9339-5f803e82daa6, 5a1452f3-7982-45be-aade-5bc522dc1860, 7b8f2663-c909-4dde-9d4e-b14b30f56322, 11a24ded-9c88-4f5c-98cc-0738a9ff0133, 8629a697-e0e7-4ca1-a0b4-dba517ac1d02, a39ae501-27e8-433e-91c7-d642cce231fa, fdcc6666-3f83-4da5-92e3-02c687568ef8, ffc70e99-e249-4759-aa82-0eb6a20b87bc, 496b5ab1-98d1-4c95-b4c5-8e301a6e3783, 02920010-16c8-497d-8842-8531b9f2604f, dfbf3f77-958b-45e1-853c-4d6c9df52ac7, 2833b848-8f04-4e71-b467-c91d66c7df52, b32aab6d-96ca-4c42-af81-74645827d926, a13157d0-9150-41d5-9d6a-abc617b8df70, e2868200-0973-4476-9b4c-048513a5e6fc, 2662dc8e-75c1-4077-8dba-005178abe044, 1a5b6d20-e701-4f9f-8727-50f93d8f16f8]
updated: 2026-06-19
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

### 2026-06-16 run-93 追加バッチ (= 12 件処理、累積本日 36+ 件)

run-92 後の queue 88 件先頭 12 件を本ラン (= run-93、18:16 JST、user 手動) で
drain。内訳 = 1 wiki-ingest-meta noop + 11 classifier:

| 分類 | 件数 | 主なテーマ |
|----|----|----|
| `projects` | 6 | 滝野川5 同意書 (蜷川様 継続)、西荻北１丁目 議事録/設備図面、中野新橋 B-3 ボリューム検討、東日暮里 見積、上北沢№２ 速報、中野一丁目 建主様情報 |
| `vendors` | 4 | YG381 Projectors Proforma Invoice (250 Units、4 件連続スレッド継続) |
| `knowledge` | 1 | 建設資材物価動向 定期レポート 2026年5月 (invoice@meguru、社内配信) |
| `wiki-ingest-meta` | 1 | `729fe121` (= run-92 直前の auto-worker noop "Both inputs are empty") |

本ランで新規可視化された案件:
- **西荻北１丁目** (jdw05072@nifty.com → 議事録 + 設備図面共有、新規案件 enqueue)
- **中野新橋 B-3** (hishida、ボリューム検討依頼、初期検討フェーズ)
- **東日暮里 お見積り** (thomma 発、見積もり進行)
- **上北沢№２** (thomma 発、速報共有)
- **中野一丁目 建主様情報** (mhiejima、施主情報フォロー)

継続中の業務ライン:
- **滝野川5 同意書 (蜷川様)** = run-91 で `b364b8d8` 観測済、本ランで `0803e68e` 追加 (=eaoki 返信)
- **YG381 Projectors Proforma Invoice** = run-89/90/91 で `72c4e690` / `39d1cb69` 観測済、本ランで `4499d03b` / `c48f50c0` / `9ac351ac` / `667253d4` の 4 件 = 海外調達ラインの集中ラリー
- **建設資材物価動向定期レポート 2026年5月** = `invoice@meguru-construction.com` 自動配信、knowledge 系の社内定期物 (初観測)

### 2026-06-16 run-94 追加バッチ (= 12 件処理、11 classifier + 1 self-stop、累積本日 47+ 件)

run-93 後の queue 98 件先頭から BusinessCurator 12 件を本ラン (= run-94、18:34 JST、user 手動、cwd=`habi-bff`) で drain。内訳 = 1 wiki-ingest-meta (自己停止) + 11 classifier:

| 分類 | 件数 | 主なテーマ |
|----|----|----|
| `projects` | 7 | YG381 Projectors (mashikaya 2 / togami 2、内部 transcribe = 4)、【地主と家主】記事広告初稿 (togami 1)、お電話の件 (hishida 1)、本町5丁目 (thomma 1) |
| `vendors` | 3 | YG381 Projectors (service-us@isinbox.com、実 vendor)、【地主と家主】記事広告 (iijima@zenchin.com、業界誌側返信)、確認事項 (hishida、社内) |
| `knowledge` | 1 | 招待: 【FY28】営業目標キックオフ (tushiyama、6/3 12:00-13:30 JST、参加: 大神・牛山・本間・石田 = 過去日程招待の遅延 enqueue) |
| `wiki-ingest-meta` | 1 | `94b63a5c` (= /wiki-ingest 自己停止セッション、runaway-worker 検知) |

本ランで新規可視化された業務イベント:
- **【地主と家主】記事広告の初稿** (`vendors`/`projects`) = `iijima@zenchin.com` (= 全日本不動産協会の業界誌「地主と家主」、第三者媒体) との出稿初稿確認ラリー、togami (内部) と iijima (社外編集) の往復 (2 件)
- **株式会社めぐるの石田 確認事項/お電話の件** (`projects`/`vendors`) = `hishida@meguru-construction.com` (= 石田) 発の社内連絡 2 件、`先程のお電話の件` / `Re: 確認事項`
- **本町5丁目** (`projects`) = `thomma@meguru-construction.com` 発、案件名「本町5丁目」スレッドへの返信
- **FY28 営業目標キックオフ招待** (`knowledge`) = `tushiyama@meguru-construction.com` 発の Google Calendar 招待、参加者「おおがみ・牛山・本間・石田」、6/3 12:00-13:30 JST (= 過去日程招待の遅延 enqueue)

継続中の業務ライン:
- **YG381 Projectors Proforma Invoice 集中スレッド** = 本ラン 5 件 (mashikaya 2 / togami 2 / service-us 1)、累計 run-89 から 11 件目以降。**「内部 transcribe = projects」「実 vendor = vendors」分類器挙動の安定的観測**

> [!note] wiki-ingest-meta の自己停止例 (`94b63a5c`)
> 本セッションは `/wiki-ingest` skill が自身で「書き込み拒否」を選択した珍しい meta セッション。当時 queue 44 件 + diary dirty + **concurrent workers 39 件 (PID 82847-92829)** を検知し、`hook-errors.log` に 3 件 `git push failed` (03:32/06:47/06:48 UTC) も観測されていた状態で "Stopping before any writes" と判断。`auto-ingest-push.sh → claude → SessionEnd → auto-ingest-push.sh` の再帰チェーンで `WIKI_INGEST_WORKER=1` 防御が伝播しない問題が初めて明示的に診断された (run-90 の "rate-limit ループ" の真因)。**lockfile (flock) 化が hook 側の対処候補** = 別件で起票候補。

### 2026-06-17 run-96 追加バッチ (= 12 件処理、8 classifier + 4 wiki-ingest-meta、累積本日分は新規日付)

run-95 (= 6/16 18:46 JST) 後の queue 88 件先頭から BusinessCurator 12 件を本ラン (= run-96、6/17 09:00 JST、user 手動、cwd=`meguru-manuals`) で drain。

| 分類 | 件数 | テーマ |
|----|----|----|
| `projects` | 7 | 【B-3】中野新橋 ボリューム検討 (hishida 依頼 → yarima 受領 → hishida フォロー、3 ターンラリー)、【B-3】練馬３丁目 ボリューム検討 (hishida、新規)、Re: Fwd: 近隣概要書 (eaoki)、中野一丁目 建主様情報 (mhiejima)、LeTech 確認事項 (r-sawahata、揺らぎ事例) |
| `vendors` | 1 | LeTech 確認事項 (r-sawahata、同一メール race 重複側、`projects` 判定とゆらぎ) |
| `wiki-ingest-meta` | 4 | `c6330593` / `5a1452f3` / `fad288bf` / `7b8f2663` — 6/16 朝の自己 `/wiki-ingest` defer 系判断ラン (内容は run-92〜95 で既反映、bookkeeping のみ) |

本ランで新規可視化された案件:
- **【B-3】練馬３丁目** (`projects`) = `hishida@meguru-construction.com` 発のボリューム検討依頼、新規案件
- **Re: Fwd: 近隣概要書** (`projects`) = `eaoki@meguru-construction.com` 発、Fwd 連鎖型の社外資料社内転送 (案件名は subject だけからは未特定)

継続中の業務ライン:
- **【B-3】中野新橋 ボリューム検討依頼** = run-93 で `0803e68e` 初出、本ランで `d3a47fdf` (hishida 依頼) + `c9f4a2f8` (yarima 受領) + `edb2f4bb` (hishida フォロー) の 3 メールラリー。**`B-3` プレフィクスが「初期検討フェーズ」の社内タグ運用らしい挙動 (run-93 中野新橋 + 本ラン 練馬３丁目)** を初観測
- **中野一丁目 建主様情報** = run-93 `mhiejima` 初出、本ラン `Re:` 1 件、施主情報フォロー継続

> [!warning] Classifier nondeterminism (初観測)
> 同一メール (件名 `RE: 確認事項になります／株式会社めぐるの石田です`、差出人 r-sawahata@letech-corp.net、内容 = ALSOK 様の件 + フェンス YL1 ナチュラルシルバー選定) が 6 秒差で **2 セッション enqueue** され、**異なる分類結果** を返した:
> - `8bd54ac5` (06:51:38Z) → `projects`
> - `c79b85cc` (06:51:44Z) → `vendors`
> LeTech = 元請パートナー業者でかつ案件文脈ありの典型エッジ。run-94 の「Proforma Invoice → projects (本来 vendors)」と同系統。**enqueue 二重化** + **LLM 出力の非決定性** の合わせ技でゆらぎが顕在化。BusinessCurator 側で session_id ベースの dedup を入れる候補だが、wiki 側は両方記録して残しておく方針が安全 (LLM 出力の非決定性は受容)。

= **本ラン直後 queue 残 76 件** (= 88 − 12)。BusinessCurator burst 残 ~54 件は次ラン (run-97) で継続消化。

### 2026-06-19 run-97 相当 追加バッチ (= 13 件処理、3 classifier + 10 wiki-ingest-meta self-stop)

run-96 (= 6/17 09:00 JST) 後の queue 76 件先頭から BusinessCurator 13 件を本ラン (= 6/19 朝、main session から `/wiki-ingest` delegate) で drain。3 日越しの遅延消化。

| 分類 | 件数 | テーマ |
|----|----|----|
| `projects` | 1 | Re: 【B-3】中野新橋 ボリューム検討依頼 (togami → 最上階25をワンルーム20平米で賃料引き直し、容積食い切りリスク) |
| `vendors` | 1 | Re: 審査機関の情報 (togami → 品田先生へ「国際確認かビューロの二択」提案依頼) |
| `knowledge` | 1 | 審査機関の情報 (mhiejima → ビューロベリタス 3.0ヶ月で他機関と同等の状況、追加情報送付) |
| `wiki-ingest-meta` | 10 | `8629a697` / `a39ae501` / `ffc70e99` / `dfbf3f77` / `2833b848` / `b32aab6d` / `a13157d0` / `e2868200` / `2662dc8e` / `1a5b6d20` — 6/16 朝の自己 `/wiki-ingest` defer 系判断ラン (auto-ingest-push.sh の runaway feedback loop で self-stop、内容は run-92〜95 で既反映、bookkeeping のみ) |

本ランで新規可視化された業務イベント:
- **審査機関の情報 (ビューロベリタス選定)** = `mhiejima` 発の社内情報共有 + `togami` 返信で品田先生 (= 外部設計担当) への「国際確認 vs ビューロベリタス」二択提案依頼。run-96 の「中野新橋 B-3」「練馬３丁目」と同じ B-3 系初期検討メールラリーの周辺で観測される確認申請ルート選定。`knowledge` (情報共有) → `vendors` (提案依頼) の 2 段ラリー

継続中の業務ライン:
- **【B-3】中野新橋 ボリューム検討依頼** = run-93 `0803e68e` 初出 → run-96 `d3a47fdf` + `c9f4a2f8` + `edb2f4bb` の 3 メールラリー → 本ラン `496b5ab1` で 4 メール目 (togami 詳細条件付き引き戻し)。**B-3 案件の継続深掘り、ワンルーム化検討フェーズへ**

> [!note] 10 件の self-stop 集中
> 10 / 13 = 77% が wiki-ingest-meta noop。**6/16 朝の auto-ingest-push.sh runaway worker loop 期の生き残り** で、当時の concurrent worker (30+ プロセス) のうち自分が後追いで起動した分が `/wiki-ingest` skill 内の concurrent-worker 検知で軒並み self-stop 選択。run-94 で `94b63a5c` を起点に診断済の現象が、より広範囲で観測された全体像。**lockfile (flock) 化** の必要性が再確認される。

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
- [[02_diary/2026-06-17]]
- [[02_diary/2026-06-19]]
