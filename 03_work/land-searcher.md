---
title: land-searcher — REINS 物件スクレイパー (meguruit)
category: 03_work
tags: [project:land-searcher, client:meguru, entity:meguruit-org, tech:python, tech:selenium, tech:headless-chrome, tech:github-actions, tech:gcp, topic:waf-bypass, topic:user-agent-spoofing, stage:active]
sources: [e702af57-704f-45d2-b1c7-5545a1990670, 8c19b6ca-f61c-41d2-8c1c-0e5643f22140, 58313e2d-a2a5-4691-94ba-7f18df49f62d]
updated: 2026-07-02
---

# land-searcher

## Summary

`meguruit/land-searcher` は REINS (Real Estate Information Network System) を
Selenium ヘッドレス Chrome で巡回し物件データを取得する Python スクレイパー。
GCP プロジェクト `land-searcher-ss` で定期実行する CI/CD 構成。
2026-06-26→27 セッション (`e702af57`) で **REINS WAF が `HeadlessChrome` UA を 503 で
弾く問題**を診断 → User-Agent 差し替えで解消、`origin/main` に push 完了。

## REINS WAF 503 ブロッカーの根治 (2026-06-26→27, session e702af57)

### 症状

GitHub Actions の定期ラン (`land-searcher` workflow) が REINS への HTTP リクエストで
503 を返し続ける状態。ローカルからの curl は通る、CI 側だけ落ちる。

### 診断 — UA マトリクス probe

仮説「WAF が UA で弾いている」を確認するため、複数 UA で REINS 到達性を
matrix 化して probe する一時 commit を投入:

- `b13cca1` test probe REINS reachability via curl + urllib
- `30cc344` test UA matrix probe to REINS

結果: **`HeadlessChrome/...` を含む UA だけ 503**。curl / urllib / 通常 Chrome UA は 200。
WAF はパターンマッチで HeadlessChrome を block している。

### 修正

Selenium WebDriver の起動オプションでユーザーエージェントを通常 Chrome に
オーバーライド (`land_searcher/main/driver.py`):

- `7bdc449` Fix REINS WAF bypass by overriding headless Chrome User-Agent
- 関連 `.github/workflows/actions.yml` のサービスアカウントキーのファイル名を
  整合 (`235b479` Restore CI run with new headless mode, align Service Account
  key filename)
- `c79bf69` Revert temp diagnostic (page-state log + screenshot) — UA matrix
  probe / page-state ログ等の診断コードを片付け

### 学び

- **WAF は IP だけでなく UA パターンで弾く**。"HeadlessChrome" 文字列は典型的な
  ブロック対象 — Headless ブラウザを業務に使う場合は UA 差し替えが必須。詳細は
  [[05_learn/reins-headlesschrome-ua-block]]
- **UA matrix probe** = "curl / urllib / Chrome / HeadlessChrome" の 4 種を並べて
  503/200 の境界を切り分けるのが最短診断。WAF 問題で原因仮説を持つときの reusable
  パターン。

## アーキ概要

- Python + Selenium (Chrome headless)
- 認証: REINS 業者向けログイン
- 実行: GitHub Actions (cron) → GCP `land-searcher-ss` (Service Account key 経由)
- 出力: 物件データを meguruit 側のシステムに供給 (詳細は後続セッションで追記)

## 2026-07-02 close (session 8c19b6ca)

REINS WAF 対応後の並行セッション `8c19b6ca` (2026-06-26 開始、6 日間持続、07-02
15:19 close) が「GitHub Actions 運用で問題なし。Thanks!」で終了。原因追跡の
辿り直し（silent failure = batch.py の例外握り潰し → LINE Notify 終了 → login
Timeout → **IP 説を一度立てて GCP 東京 VM で curl 200 まで確認** → その後
UA matrix probe で真因が `HeadlessChrome` UA と確定 → GCP 移行不要と結論）が
完全に含まれている。既存の H2「REINS WAF 503 ブロッカーの根治」で書いた結論を
プロセス面から補強する記録。cron は **07:05 JST**、run 実行時間の目安は
「2〜3 分 = 成功 / 約 1 分 = 失敗」。通知は当面オフ（Slack/Discord webhook 差し替え
は将来案件）。

単発 QA session `58313e2d` (2026-06-26, 24 秒) は「`land-searcher-ss-cd912322ecb1.json`
service account key はどう取得？」に対する Cloud Console 手順の解説のみ。この
質問の背景で、`8c19b6ca` セッション内で SA 鍵は末尾 `1d2075633b90` の有効鍵へ
差し替え、`.github/workflows/actions.yml` のファイル名整合と Secret
`CREDENTIALS_JSON` 更新まで実施済。

## Links

- [[05_learn/reins-headlesschrome-ua-block]] — 本セッションで根治した WAF UA block の
  汎用 reusable 知識
- [[02_diary/2026-06-27]] — run-107 ingest 着地点
- [[02_diary/2026-07-02]] — 8c19b6ca / 58313e2d close 着地点
- [[06_output/2026-06]] — `meguruit/land-searcher` への commit push 記録
