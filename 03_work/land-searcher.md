---
title: land-searcher — REINS 物件スクレイパー (meguruit)
category: 03_work
tags: [project:land-searcher, client:meguru, entity:meguruit-org, tech:python, tech:selenium, tech:headless-chrome, tech:github-actions, tech:gcp, topic:waf-bypass, topic:user-agent-spoofing, stage:active]
sources: [e702af57-704f-45d2-b1c7-5545a1990670]
updated: 2026-06-27
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

## Links

- [[05_learn/reins-headlesschrome-ua-block]] — 本セッションで根治した WAF UA block の
  汎用 reusable 知識
- [[02_diary/2026-06-27]] — run-107 ingest 着地点
- [[06_output/2026-06]] — `meguruit/land-searcher` への commit push 記録
