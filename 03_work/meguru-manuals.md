---
title: meguru-manuals — 建築設計業務マニュアル PPTX 生成パイプライン
category: 03_work
tags: [project:meguru-manuals, client:meguru, tech:nodejs, tech:pptxgenjs, tech:react-icons, tech:libreoffice, tech:poppler, stage:active, milestone:5-part-standard-structure-2026-04, topic:demolition, topic:house-survey]
sources: [aa4f1029-a4cd-4adc-8c2c-c83a8c36438f, 8b1f8490-fd1e-4fe0-b971-108e4d2e3f7c, d9595f4e-5269-418c-9099-d7775eb81aa8]
updated: 2026-06-26
---

# meguru-manuals

## Summary

株式会社めぐる向けの建築設計業務マニュアル（PPTX）を Claude Code + pptxgenjs で自動生成するパイプライン。現状の対象マニュアルは **建築測量 / 地盤調査 / 地盤改良 / 自火報 / 解体・家屋調査** の 5 件、`manuals/<分野>/generate.js` 1 ファイル＋ `assets/` 配下の元資料（Excel / PDF / Markdown / PPTX）から PPTX を 1 コマンドで生成し、`scripts/qa.sh` で PDF → JPG 経由の目視 QA を回す。テーマは `themes/ocean.js` / `themes/yellow.js` を 1 行差し替え可能、コアの slide-builders 関数群はテーマ非依存。

## 標準マニュアル構成（2026-04〜、aa4f1029 で確立）

新規マニュアルは原則 **3 部構成**（CLAUDE.md に明文化、`manuals/地盤調査/generate.js` で実装済）:

1. **{対象業務} の目的** — 何のために行うのか（俯瞰＋個別）
2. **業務マニュアル**
   - 2-1 業務フロー（`buildFlowSlide` 全体像）
   - 2-2 資料と成果物（業務フローのどこで登場するかを明示）
   - 2-3 手順（設計 PM が実施する Step 形式）
   - 2-4 ルールと注意事項（判断基準＋落とし穴＋用語チェック）
3. **ケーススタディ** — 実案件ベースのよくある状況と対応

> [!info] 構成要件（QA で機械チェック）
> - 目次番号 と 各スライドの `sectionLabel` が一致（例：目次 `3-1` → スライド `Sec.3-1 ...`）
> - サブセクションを持つ章は TOC で `subs` を使う
> - 各スライドに `subject`（設計 PM / 構造設計者 / 地盤調査会社 / 測量士 …）を指定 → タイトル右下に「主語：○○」バッジで自動表示
> - 業務フロースライドの各ステップは `role` フィールドで明示（`subject` は不要）

## 対象者レベルの使い分け

aa4f1029 で確定したルール:

- **経験者向け**: `buildChecklistSlide` 中心。**抜け漏れ防止のチェックリスト**として機能
- **未経験者向け**: `why` フィールドで「なぜ必要か」を添える。**教育の台本**として機能（💡 なぜ必要？ ボックスで自動表示）
- `why` と `note` は **排他**。両方必要な情報過多スライドは **2 枚に分割**
- 実案件の判断例は Sec. ケーススタディ にまとめる（本間提案→回答→結論の 3 段構造）

## コアアーキテクチャ

```
meguru-manuals/
├── core/
│   ├── slide-builders.js   — 10 種のスライドテンプレート関数（pptxgenjs ラッパ）
│   └── icon-helper.js      — react-icons → PNG 変換
├── themes/
│   ├── ocean.js            — Ocean Blue（ダーク表紙、青アクセント）
│   └── yellow.js           — Yellow/Warning（白表紙、黄色バー）
├── manuals/<分野>/
│   ├── generate.js         — コンテンツ定義＋テーマ指定（1 行で差替）
│   ├── assets/             — 入力（Excel/PDF/PPTX/Markdown）
│   └── output/             — 生成 PPTX
└── scripts/
    ├── build.sh            — 単一マニュアル生成
    └── qa.sh               — PDF 変換 → JPG 化 → 目視 QA
```

`core/slide-builders.js` は **テーマ非依存**。テーマ追加時はファイル 1 枚を `themes/` に置くだけで完結する設計。

### スライドテンプレート選定表

| 用途 | テンプレート関数 |
|------|----------------|
| 表紙 | `buildCoverSlide` |
| 読み方ガイド | `buildGuideSlide` |
| 目次 | `buildTocSlide`（`subs` で階層 TOC） |
| 俯瞰（カードグリッド） | `buildIconGridSlide` |
| 本文（テキスト＋箇条書き、`why` 対応） | `buildContentSlide` |
| 2 カラム比較 | `buildTwoColumnSlide` |
| フローチャート | `buildFlowSlide` |
| 分岐フロー | `buildBranchFlowSlide` |
| 画像＋注釈 | `buildImageSlide` |
| チェックリスト（`why` 対応） | `buildChecklistSlide` |
| 連絡先・まとめ | `buildEndSlide` |

## Claude Design vs Claude Code（aa4f1029 の判断）

- **Claude Design**（Anthropic Labs の別製品、canvas UI ベース、対話的デザイン生成）は **CLI ツールではない** ため、本リポの「プログラマティック／再現可能なマニュアル生成」用途には合わない
- **PPTX 系 MCP**（office-pptx-mcp 等）は既存 `pptxgenjs` と抽象度が重複 → **追加せず**
- **Playwright MCP** は既に Claude Code 環境に同梱済 → 追加インストール不要、UI 比較が必要な場合のみ使用
- 結論: **Claude Code + pptxgenjs の現構成が優位**、外部依存追加は最小化

## 元資料を漏れなく反映する原則（aa4f1029 で痛感）

`assets/` 配下の **全ファイル**に目を通してから `generate.js` を書く。地盤調査マニュアルでは:

- 旧 PPT → 土の種類（ローム/シルト/凝灰質粘土等）、土質試験判断基準、ローム層基礎選定パターン
- 用語集.xlsx → 試験系用語（三軸 UU / 圧密 / LLT / 一軸圧縮 / 細粒分 / 二層地盤）
- 室内試験判断基準メモ.md → **5 件の実案件ケーススタディ**（[[03_work/yahatayama-rokujizo|八幡山六地蔵]] / 世田谷大原 / 中野坂上 / 東長崎 / 東日暮里）
- 報告書 PDF → 業者の正式連絡先（ウチヤマ地質工業 t@uchiyama-geo.com、TEL）

→ コンテンツが旧版比 **23% 増**（1.19 MB pptx）に達した。aa4f1029 では `_backup_20260422.pptx` を作って旧版を保全したうえで上書き再生成。

## 文体ルール

- **語りかけ口調**（「〜してくれます」「〜しましょう」）
- 注意事項は「要注意！」「ここ大事！」「確認！」で呼びかける
- タイトルは動詞で終わる（「〜を確認しよう」「〜をはっきりさせる」）
- `assets/(分野)/OutOfScope` に置いた内容は **スコープ外**として冒頭で明示、本文には含めない
- `assets/(分野)/一般知識` の内容は **用語注釈や基礎知識の補記**として活用

## QA 基準

`bash scripts/qa.sh manuals/<名前>/output/*.pptx` 後、生成された `slide-*.jpg` を目視（or Claude に直接画像を渡す）で:

- テキストの溢れ・重なり
- 全スライドに sectionLabel が付いているか
- **目次番号と各スライドの sectionLabel が一致**（aa4f1029 で QA 項目化）
- **subject バッジが業務フロー以外のすべての業務スライドに表示**（aa4f1029 で追加）
- note / callout がスライド下端に収まっているか
- 画像スライドで画像が正しく表示
- TODO / xxx 等のプレースホルダー残置なし
- **元資料の重要コンテンツが漏れなく反映**（aa4f1029 で明文化）

## 依存関係

- Node.js 18+
- npm: `pptxgenjs` / `react` / `react-dom` / `react-icons` / `sharp`
- LibreOffice (`soffice`) — PDF 変換用（aa4f1029 / 8b1f8490 環境では未インストールで PDF QA 不可だった。**d9595f4e (2026-06-26) で `brew install --cask libreoffice` で 26.2 を導入、PATH に soffice を追加。以後 `scripts/qa.sh` は無加工で動く**）
- poppler-utils (`pdftoppm`) — 画像化用

## よく使うコマンド

```bash
# 単一マニュアル生成
bash scripts/build.sh manuals/建築測量

# QA（PDF → JPG）
bash scripts/qa.sh manuals/建築測量/output/建築測量_業務マニュアル.pptx

# 全マニュアル一括生成
for d in manuals/*/; do bash scripts/build.sh "$d"; done
```

## マニュアル別ステータス

| 分野 | テーマ | スライド数 | 生成 session | 備考 |
|------|--------|-----------|-------------|------|
| 建築測量 | ocean | — | （未確認） | |
| 地盤調査 | ocean | — | aa4f1029（2026-05-19） | 5-part 構成の初実装、用語集 + 5 案件ケーススタディ反映 |
| 地盤改良 | ocean | 42 | 8b1f8490（2026-05-22） | 標準 3 部構成、8 案件ケーススタディ、Excel 4 ファイル + 事例フォルダから抽出 |
| 自火報 | yellow | — | （未確認） | |
| 解体・家屋調査 | ocean | 31 | d9595f4e（2026-06-26） | 標準 3 部構成、解体＋近隣家屋調査の 2 業務、対象範囲 (隣接家屋) 選定基準を 3 か所で重点記載、用語整理 (家屋調査 ≠ 土地家屋調査士業務) |

## 地盤改良マニュアル（8b1f8490、2026-05-22）

ユーザ依頼「地盤改良のマニュアルを作って！」に対し、Claude が `assets/` 配下の Excel 4 ファイル（地盤設計の基本的な考え方 / コンセプトと工法の整理 / 概算見積 / 詳細見積）＋ `事例/` フォルダから情報を抽出し、`manuals/地盤改良/generate.js` を新規作成（544 行）→ 42 スライドの PPTX を生成。

**構成（標準 3 部構成準拠、ocean テーマ）:**

- Sec.1 文書の定義 — 設計 PM 向け位置づけ
- Sec.2 地盤改良の目的 — 5 つの目的 / 3 つのコンセプト（複合地盤・周面摩擦杭・先端支持杭）/ 3 つの選定観点 / 支持層深さ別の仕分け / 既存データ活用
- Sec.3 業務マニュアル
  - 3-1 業務フロー（報告書受領 → 構造ダブルチェック → 概算 → 工法選定 → 詳細＋発注準備）
  - 3-2 資料と成果物（概算・詳細の添付資料 / メールサンプル）
  - 3-3 手順（Step 0〜7 + 最終チェックリスト）
  - 3-4 ルールと注意事項（地盤調査連携 / 水位・残土・近隣 / ラップルコン / 杭の特殊条件 / 工法カタログ 12 種 / 用語）
- Sec.4 ケーススタディ — 実案件 8 件（佃 / 不動前 ×2 / 高円寺大和町 / 田端東尾久 / 下目黒 ×3 / 田端駒込 / 中野区本町 / 西大井 ×6）＋業者連絡先

> [!warning] QA 画像化スキップ
> 本ランの実行環境に `soffice`/`libreoffice` 未インストールで `bash scripts/qa.sh` が動かず、目視 QA は未実施。PPTX 自体は 42 スライドで正常生成・構造は地盤調査マニュアルと同型を確認済。次回 LibreOffice 入った環境で `qa.sh` を回すか、PowerPoint で直接目視チェック必要。**→ 2026-06-26 (d9595f4e) で LibreOffice 26.2 を導入したため、再生成すれば PDF QA 可能。**

## 解体・家屋調査マニュアル（d9595f4e、2026-06-26）

ユーザ依頼「解体・土地家屋調査のマニュアルを作って！土地家屋調査については、どの範囲（隣接する家屋）を対象とするかについても記載すること」に対し、`manuals/解体・家屋調査/generate.js` を新規作成 → **31 スライド** (ocean) を生成。

**重要な用語整理**: ユーザの「土地家屋調査」は **土地家屋調査士の登記業務ではなく**、解体に伴う **近隣家屋の事前事後調査** (振動・沈下クレーム対策) を指す。Sec.1 に「ここでの家屋調査 ≠ 土地家屋調査士の登記業務」スライドを明示追加して取り違え防止。

**構成（標準 3 部構成、ocean テーマ）:**

- Sec.1 文書の定義 — 2 業務 (解体＋近隣家屋調査) の位置づけ + 用語整理スライド
- Sec.2 目的 — 解体／家屋調査それぞれの目的、両者の関係
- Sec.3 業務マニュアル
  - 3-1 業務フロー (解体／家屋調査の 2 本＋接続)
  - 3-2 資料と成果物
  - 3-3 手順 (解体 Step 0〜3 + 家屋調査 Step A〜D)
  - 3-4 ルールと注意事項
- Sec.4 ケーススタディ — 対象選定の迷い／不在対応／内部調査の判断

**「対象範囲（隣接家屋）」要件への対応 (3 か所で重点記載):**
1. Sec.3-3 Step A「家屋調査の対象範囲を決めよう」— 近接家屋・古くて心配な所有者・クレームリスク家屋を抽出、地盤緩い／掘削深い場合は範囲拡大、内部調査の対象判断
2. Sec.3-4 ルールと注意事項 — 範囲判断基準
3. Sec.4 ケーススタディ — 対象選定の実例

**元資料 (2 点) を漏れなく反映:** `家屋調査メモ.txt` (発注先 3 社・見積メール案・添付ファイル・注意事項 4 項目) + Excel `設計PM_作業詳細_202508_解体.xlsx`

**QA で発見・修正した不具合 (再発防止メモ):**
- `buildEndSlide` の **事実上の上限は 5 行**。6 行 (近隣窓口＋社内相談を別行) でも下端からはみ出すことを確認。今回は両者を 1 行に統合して 5 行に収めた。
- 7 行 → 6 行 → 5 行 と 2 回トリムが必要だった。次回 End Slide を組むときは最初から 5 行以内で設計するのが安全。

## Links

- [[02_diary/2026-05-19]] — aa4f1029（5-part 構成の確立 + Claude Design 調査 + slide-builders 拡張 + 地盤調査マニュアル再生成）
- [[02_diary/2026-05-22]] — 8b1f8490（地盤改良マニュアル新規 42 スライド生成）
- [[02_diary/2026-06-26]] — d9595f4e（解体・家屋調査マニュアル新規 31 スライド + LibreOffice 26.2 導入）
- [[03_work/yahatayama-rokujizo]] — 八幡山六地蔵案件、地盤調査マニュアルのケーススタディ 5 件のうち 1 件
- [[03_work/meguru-pm-report]] — めぐる関連、同じ client:meguru タグ
