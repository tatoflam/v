---
title: meguru-diagrams — Meguru CRM 業務フロー Mermaid シーケンスダイアグラム
category: 03_work
tags: [project:meguru-diagrams, client:meguru, tech:mermaid, tech:markdown, channel:github, stage:active]
sources: [0b793fb1-a0be-4fe9-ad7e-79eea87aac43]
updated: 2026-06-12
---

# meguru-diagrams

## Summary

株式会社めぐる向けの業務フロー設計を Mermaid シーケンスダイアグラムで可視化するリポジトリ (`/Users/tato/repo/github/tatoflam/meguru-diagrams`)。営業プロセス見直しの局面で、CRM (`meguru-crm`) が現状カバーする機能と、CRM 外で GWS スプレッドシート管理になっている業務を 3 レイヤで視覚化し、ワークフロー管理追加 (= 提案クロージングまでのステータス管理) の議論基盤に使う。

## 現在の状態

初版 `sales-process-sequence.md` (土地探し → 構造キックオフまでの 14 ステップ営業プロセスを 3 レイヤ構成のシーケンスダイアグラムに落としたもの) を main に push 済 (2026-06-10)。

### 業務フロー (14 ステップ + アクター)

| # | プロセス | アクター |
|---|---|---|
| 01 | 土地探し | 営業 |
| 02 | 目論見作成 | 営業 |
| 03 | 目論見レビュー | 大神 |
| 04 | 建築用情報収集 | 営業 |
| 05 | ボリューム検討 | 計画設計 |
| 06 | 計画レビュー | 大神 |
| 07 | 概算見積作成 | 牛山 |
| 08 | 利益率確認＆案件化判断 | 大神 |
| 09 | 顧客提案 → クロージング | 営業 |
| 10 | 請負契約 | バックオフィス |
| 11 | 基本設計 | 設計監修 |
| 12 | デザインレビュー | 大神 |
| 13 | デザイン監修 (オプション) | 施主 (税込 495 万円追加) |
| 14 | 構造キックオフ → 実施設計開始 | 設計 |

### 3 レイヤ構成

- **アクター層**: 営業 / 大神 / 計画設計 / 牛山 / 設計監修 / 設計 / バックオフィス / 施主
- **🟡 GWS スプレッドシート (共有ドライブ)**: 09 顧客提案以前の CRM 外プロセスの記録先。**シート単位に細分化せず 1 エンティティに集約** (= ユーザー向け資料として煩雑になるのを避ける、user 修正 2 回目で確定)
- **🔵 CRM (`meguru-crm`)**: メイン機能 = a. 志願者 / b. 土地 / c. 目論見 / d. 提案。`proposals.status` (`proposing` → `negotiating` → `contracted` / `lost`) によるワークフロー管理を新規追加対象とする

### 🔁 連携ポイント (GWS → CRM 反映、2 箇所)

1. **08 → 09 案件化反映 (提案登録)**: GWS 上の目論見・概算見積データを起点に、09 顧客提案フェーズで CRM 側に「提案」レコードを登録。**転記の主体は営業**で図中に表現 (= 「手動」テキストは未記載、矢印で示す)
2. **11 以降 設計成果物リンク**: 基本設計以降の成果物リンクを CRM の提案レコードに紐付け

### 公開先 (= channel:github)

- repo: `https://github.com/tatoflam/meguru-diagrams` (= 個人 GitHub org)
- sales-process-sequence.md の main push 2 commit (= 2026-06-10):
  - [`aeaded8`](https://github.com/tatoflam/meguru-diagrams/commit/aeaded8) `update: sales process sequence`
  - [`d5cf0cc`](https://github.com/tatoflam/meguru-diagrams/commit/d5cf0cc) `update: sales process w/GWS`
- GitHub の native Mermaid render で web 上で図確認可能: `https://github.com/tatoflam/meguru-diagrams/blob/main/sales-process-sequence.md`
- 06_output 着地: [[06_output/2026-06#GitHub commits — tatoflam/meguru-diagrams 営業プロセス × GWS × CRM 図新設 (2026-06-10)]]

### 未解決事項・運用メモ

- **目論見の確認済 status テーブル所在は保留**: 03 レビューステータス更新の対象テーブルは現状の db design からは不明 (= UI 上で「確認済」管理されているがバックエンドの該当テーブル要確認)。提案側は `proposals.status` がテーブルに存在することは確認済
- CRM のデータベース設計参照元: `https://github.com/meguruit/meguru-crm/blob/main/docs/designs/database-design.md`
- 本リポジトリの cwd は `tatoflam/meguru-diagrams` (= 個人 GitHub org)、設計成果物として `meguruit/meguru-crm` の検討資料を補完する関係

## 決定事項

- 2026-06-10: **GWS の細分化を解消** — 「土地調査シート」「ボリュームシート」「概算見積シート」「設計管理シート」を個別エンティティ化していた中間版を `GWS スプレッドシート（共有ドライブ）` 1 ロールに統合、ノートと管理先テーブル列も `GWS` に統一 (user 修正 2 回目で最終形)。理由: ユーザー向け資料として煩雑になるのを避ける。
- 2026-06-10: **提案登録は手動想定**だが「手動」テキストは figure に明示しない — 08→09 の 🔁 反映ブロックを残して営業の矢印で表現。
- 2026-06-10: `proposals.status` によるワークフロー管理を CRM への新規追加対象とする。

## 経緯

- 2026-06-10 (session 0b793fb1、JST 10:38→12:47、~2h、4 user turn): `sales-process-sequence.md` 初版を作成。1 回目作成時に socket disconnect 系の API Error で書き込み未完 → user「エラーしたのでリカバリして続けて！」で再適用 (GWS 細分化解消の編集が前回未着地だった分も合わせて反映)。user 確認 2 回 (GWS 細分化解消・提案登録の手動表現) を経て最終形、main へ 2 commit push。

## Links

- [[06_output/2026-06]] — 本リポの GitHub commit カタログ
- [[03_work/meguru-pm-report]] — Meguru PM レポート生成基盤 (= 同じ Meguru ドメインの別系統、CRM とは直接連携しないが案件マスタを介して接続)
- [[03_work/meguru-manuals]] — Meguru 業務マニュアル PPTX 生成 (別アウトプット系統、設計 PM 向けマニュアル)
- [[03_work/yahatayama-rokujizo]] — Meguru 実案件 reference
