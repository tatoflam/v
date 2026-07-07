---
title: Meguru Design Portal
category: 03_work
tags: [project:meguru-design-portal, client:meguru, tech:firebase, tech:google-drive, stage:planning]
sources: [2550f3e9-ebc6-494f-8489-3f542868206c]
updated: 2026-07-08
---

# Meguru Design Portal

## Summary

株式会社めぐる (client:meguru) の外部設計士向けドキュメント共有 portal の新規案件。めぐる側の設計標準資料・標準収まり図を外部の意匠/構造設計士へ**一方向共有**する web portal。2026-07-07 深夜の session `2550f3e9` で初回要件プロンプトを受領 (session は 10 秒で中断、実装は後続 session)。

## Details

### 事業コンテキスト

- めぐるは施主の WRC 投資物件について企画/設計/建築/管理をワンストップで請ける**元請け** (general contractor)。
- 意匠設計・構造設計は外部の設計士へ外注し、確認申請・監理をディレクション。設計標準ドキュメントと標準収まり図をめぐる側が保有・提供する。
- この「元請けが標準を握り外部設計士へ配る」構図が、portal の一方向共有 + 管理者承認制登録という設計を規定している。

### 要件 (2550f3e9 プロンプトより)

- **認証**: 外部設計士のセルフ登録 + ログイン。めぐる社内管理者の承認ゲート付き。認証ユーザーのみ閲覧可。
- **コンテンツ**: 専用 content DB を**持たない**。実体はめぐるの Google Workspace 共有ドライブ (めぐる社員がフォルダ整理)、portal はリンクのみ登録。
- **DB**: ログイン履歴 + 通知管理のみの最小構成。無料枠または Google Sheets 志向。
- **Hosting**: Firebase など安価で GitHub 連携しやすいサービス。
- **機能**: 変更履歴の登録 + 一括メール通知 (設計士をチェックボックス選択、本文記入、送信者を To/CC)。
- **成果物要求**: 前提/制約/必要リソース込みの HTML 提案書、要件定義〜運用移行の人間工数見積 (単価 10,000 円/h)、初期構築費 + ランニングコスト。
- **プロセス要求**: openspec ドキュメントを Fable で作成し、Opus で継続するための思考体系・引き継ぎ事項を文書化。private repo `meguruit/MeguruDesignPortal` として git-init + push。

### ステータス

> [!question] 後続 session 未取り込み
> 本ページの内容は「要件プロンプトの記述」であり実装結果ではない。cwd `~/repo/github/meguruit/MeguruDesignPortal` には `openspec/` が既に存在するが repo は未 git-init (2026-07-08 時点の観測)。実際の提案書・openspec 作成を行った後続 session が enqueue され次第、本ページを更新する。

## Links

- [[03_work/meguru-pm-report]] — 同 client:meguru の既存案件
- [[03_work/meguru-wiki]]
- [[02_diary/2026-07-08]] — run-123 で取り込み
