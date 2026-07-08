---
title: Home
tags: [home]
updated: 2026-07-08
---

# Home

Vault の入口。`/wiki-distill` が維持する（index.md は機械カタログ、こちらは人間向け）。

## いま動いている仕事（03_work）

- [[03_work/meguru-pm-report|MeguruPMReport]] — 週次レポート自動 publish 運用中（直近 2026-07-03 フルセット配信）
- [[03_work/threadsposts|ThreadsPosts]] — 自律投稿ループ稼働（7 日停止インシデント解消済、buzz 補充まで自動化）
- [[03_work/habi-bff|habi-bff]] — dev 環境デプロイ済、PM Chat Tool 実機 URL あり
- [[03_work/todobot|ToDoBot]] — email-only 通知へ移行、cron 固定化済
- [[03_work/meguru-design-portal|Meguru Design Portal]] — 初回要件定義済（設計士向けドキュメント共有 portal）、実装これから

## いま動いている生活・資産（04_life）

- [[04_life/sayama-land-contract|狭山市 土地売買・建築請負]] — 2026-04-28 契約済、建築・決済フェーズ
- [[04_life/saltmoon-llc-operations|合同会社ソルトムーン運営]] — 資産管理法人（決算 8 月末）
- [[04_life/emil-corp-operations|エミル株式会社運営]] — 節税・オペレーティングリースはこちらで実行
- [[04_life/nisa-2026-rebalance|NISA 2026 リバランス]] — 残枠 253 万円の消化計画実行中
- [[04_life/minami-gakudo-fubokai-2026|みなみ学童父母会 2026]] — 割当・集計運用

## 直近の主要決定（~2 週間）

- 2026-07-08: wiki を 2 層アーキテクチャ（capture / knowledge）へ再構築 — ログ収集から「問い合わせに答えられる分身」へ（openspec `wiki-knowledge-refocus`）
- 2026-07-07: Threads 投稿はポエム化せず 68–76 字に凝縮する方針を確立（[[00_self/preferences]]）
- 2026-07-03: MeguruPMReport 週次フルセット publish + Milestone writeback 8 セルを定常運用化

## 自分について（00_self）

- [[00_self/profile|プロフィール]] / [[00_self/skills|スキル]] / [[00_self/values|価値観と判断基準]] / [[00_self/goals|目標]] / [[00_self/preferences|好み・進め方]]

## 使い方

- 質問する: `/wiki-query`（今どうなってる？ / なぜ決めた？ / どうやる？）
- 取り込み: SessionEnd hook が自動 capture → 溜まったら `/wiki-distill` で知識化
- 状態確認: `/wiki-status`
