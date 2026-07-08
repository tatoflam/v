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

## 現在の状態

- WAF 503 問題は根治済。GitHub Actions の cron 運用で問題なし (2026-07-02、user「GitHub Actions 運用で問題なし。Thanks!」で close)。
- cron は **07:05 JST**。run 実行時間の目安は「2〜3 分 = 成功 / 約 1 分 = 失敗」。
- 通知は当面オフ（LINE Notify 終了のため。Slack/Discord webhook 差し替えは将来案件）。
- Service Account 鍵は末尾 `1d2075633b90` の有効鍵に差し替え済。`.github/workflows/actions.yml` のファイル名整合と Secret `CREDENTIALS_JSON` 更新も実施済。

### アーキ概要

- Python + Selenium (Chrome headless)
- 認証: REINS 業者向けログイン
- 実行: GitHub Actions (cron) → GCP `land-searcher-ss` (Service Account key 経由)
- 出力: 物件データを meguruit 側のシステムに供給 (詳細は後続セッションで追記)

## 決定事項

- 2026-06-27: WAF 503 対策は **User-Agent 差し替え**で根治、GCP 移行は不要と結論 — WAF は IP ではなく `HeadlessChrome` UA パターンで弾いていた（GCP 東京 VM からの curl は 200 で IP 説は棄却）。
- 2026-06-26〜27 (session 8c19b6ca 内): SA 鍵を末尾 `1d2075633b90` の有効鍵へ差し替え — あわせて workflow のファイル名整合と Secret `CREDENTIALS_JSON` を更新。
- 2026-07-02: 通知は当面オフ — LINE Notify 終了のため。Slack/Discord webhook 差し替えは将来案件。

## 手順・Runbook

- **WAF 503 診断 = UA matrix probe**: 「curl / urllib / 通常 Chrome UA / HeadlessChrome UA」の 4 種を並べて 503/200 の境界を切り分けるのが最短診断。WAF 問題で原因仮説を持つときの reusable パターン。詳細は [[05_learn/reins-headlesschrome-ua-block]]。
- **運用ヘルスチェック**: run 実行時間で成否判定 — 2〜3 分 = 成功 / 約 1 分 = 失敗。
- **学び**: WAF は IP だけでなく UA パターンで弾く。"HeadlessChrome" 文字列は典型的なブロック対象 — Headless ブラウザを業務に使う場合は UA 差し替えが必須。

## 経緯

- 2026-06-26→27 (session `e702af57`): GitHub Actions の定期ラン (`land-searcher` workflow) が REINS への HTTP リクエストで 503 を返し続ける（ローカルからの curl は通る、CI 側だけ落ちる）。仮説「WAF が UA で弾いている」を UA matrix probe の一時 commit で検証 — `b13cca1` (test probe REINS reachability via curl + urllib) / `30cc344` (test UA matrix probe to REINS)。結果: **`HeadlessChrome/...` を含む UA だけ 503**、curl / urllib / 通常 Chrome UA は 200 → WAF はパターンマッチで HeadlessChrome を block と確定。修正: `land_searcher/main/driver.py` で Selenium WebDriver 起動オプションの UA を通常 Chrome にオーバーライド — `7bdc449` (Fix REINS WAF bypass by overriding headless Chrome User-Agent) / `235b479` (Restore CI run with new headless mode, align Service Account key filename) / `c79bf69` (Revert temp diagnostic — UA matrix probe / page-state ログ等の診断コード片付け)。
- 2026-06-26 (session `58313e2d`, 24 秒): 単発 QA —「`land-searcher-ss-cd912322ecb1.json` service account key はどう取得？」に Cloud Console 手順を解説のみ。
- 2026-06-26〜07-02 15:19 (session `8c19b6ca`, 6 日間持続): 原因追跡の辿り直しを完全に含む並行セッション — silent failure = batch.py の例外握り潰し → LINE Notify 終了 → login Timeout → **IP 説を一度立てて GCP 東京 VM で curl 200 まで確認** → UA matrix probe で真因が `HeadlessChrome` UA と確定 → GCP 移行不要と結論。「GitHub Actions 運用で問題なし。Thanks!」で終了。SA 鍵差し替えもこのセッション内で実施。

## Links

- [[05_learn/reins-headlesschrome-ua-block]] — 本セッションで根治した WAF UA block の
  汎用 reusable 知識
- [[02_diary/2026-06-27]] — run-107 ingest 着地点
- [[02_diary/2026-07-02]] — 8c19b6ca / 58313e2d close 着地点
- [[06_output/2026-06]] — `meguruit/land-searcher` への commit push 記録
