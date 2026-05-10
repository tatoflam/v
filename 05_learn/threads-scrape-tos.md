---
title: Threads スクレイピング不可の三重判定 — robots.txt × Graph API × Local-First fingerprint
category: 05_learn
tags: [topic:threads, topic:bot-detection, topic:tos-compliance, tech:meta-graph-api, tech:robots-txt, tech:playwright, channel:threads, principle:local-first-anthropic, principle:composite-fingerprint-not-single-cause]
sources: [1228fa25-787b-4c38-b347-3a9231d5431a]
updated: 2026-05-11
---

# Threads スクレイピング不可の三重判定

## Summary

Threads (Meta) の競合スカウト系 change を propose する前に **3 段事前チェック** を済ませる: ① `robots.txt` でクライアントが明示 disallow されていないか、② Graph API surface に必要なエンドポイントが存在するか (owner-only か public か)、③ 同じ operator マシンから scrape したとき publish 側の humanness fingerprint を毀損しないか。1228fa25 (2026-05-09) で 3 段詰まりを実機検出し、scout 単独 change を撤退した実例から確立した判定軸。

## なぜ 3 段全部を見るのか

1 段だけだと「gray area で進められる」と判断ミスする。実際に scrape 路は **3 段同時に詰まる構造** で、どれか 1 つでも逃げ道が見えると propose しがちだが、3 段全部見ると逃げ道なしと早期確定できる。

## ① robots.txt — ClaudeBot 名指し disallow

`https://www.threads.com/robots.txt` (旧 .net は .com に 301 redirect):

```
User-agent: ClaudeBot       Disallow: /
User-agent: Amazonbot       Disallow: /
User-agent: GPTBot          Disallow: /
User-agent: PerplexityBot   Disallow: /
User-agent: Scrapy          Disallow: /
User-agent: *               Disallow: /

# automated data collection on Threads is prohibited without
# express written permission from Threads and must comply with
# Meta's Automated Data Collection Terms.
```

- **ClaudeBot は名指し** で完全 disallow リストに含まれる (Amazonbot / GPTBot / PerplexityBot / Scrapy 等と同列)
- catch-all `User-agent: *` も全 path disallow
- 唯一の例外は **Bingbot / Googlebot のみ部分的に許可** (= Google / Bing の SERP には Threads URL が出る)
- robots.txt 末尾に明示的禁止文言

**判定**: Claude Code 系 (ClaudeBot) でも Playwright (UA カスタムしても結局 IP / fingerprint で見られる) でも、Threads 由来 URL への automated access は ToS 違反扱い。「robots.txt は規制力なし」論は ToS と Automated Data Collection Terms に同等の拘束があるので無効化される。

## ② Graph API surface — owner-only model

Meta が公開している Threads Graph API のエンドポイント (2026-05-08 時点で確認できる範囲):

| エンドポイント | 何ができる |
|---|---|
| `POST /me/threads` | **自分の** アカウントから投稿 |
| `GET /me/threads` | **自分の** 投稿一覧 |
| `GET /me/threads/{id}/insights` | **自分の** 投稿の metrics |
| `GET /me/threads_mentions` | **自分への** mention 通知 |
| `GET /me/threads_replies` | **自分への** reply 通知 |
| `POST /oauth/...` | token refresh / exchange 系 |

**存在しないもの**:

- キーワード検索 API (例: `GET /search?q=interior+a.r10.to`) — Twitter/X v2 にあったタイプ
- 任意ハンドルの投稿取得 (例: `GET /users/{handle}/threads`)
- 任意ハンドルのフォロワー数取得
- Public 投稿の hashtag/keyword discovery

### なぜ Meta はこうしているか

X (Twitter) の歴史を見ているから。Twitter が public search API を提供していた時代、それが広範な scraping / sentiment business に使われ、Meta は同じ轍を踏まないよう Threads / Instagram の Graph API を **owner-only model** に最初から設計している。

### Instagram "Business Discovery" は使えない

Instagram には限定的に他者参照する `Business Discovery` があるが:

- **Business アカウント限定** + 自社が Business アカウントを持っていることが前提
- 個人クリエイター (≤ 20K follower) のスカウトには使えない (Business 化していないアカウントは見えない)

## ③ Local-First fingerprint — scrape ↔ publish 干渉

Local-First Anthropic Ops ([[05_learn/local-first-anthropic-ops]]) では publish と scrape が **同一 IP / device** で動く。具体的に何が起きるか:

- publish 側: oheyamemo の Threads Graph API token (long-lived 60 日有効) で投稿 → Meta は IP / device / 時刻パターンを fingerprint として保持
- scrape 側: 同じマシンから Playwright で `threads.com` にアクセス → Meta の bot detection が触れる → 同じ IP / device fingerprint に「automated access from this device」のフラグが立つ
- 結果: publish 側のアカウント (= oheyamemo) の humanness score が下がる → BAN リスク

### 前事例: @chokatsu_studio BAN (2026-05-04)

- 旧アカウント @chokatsu_studio が Meta の automated/inauthentic 分類器で BAN
- 分類器入力に **fingerprint 信号** (IP/device) が含まれていた可能性が高いと推定
- 詳細: memory `project_account_ban_pivot.md` (ThreadsPosts リポ memory 配下)

### account-pivot-warmup Decision 7

- oheyamemo の生存戦略は **「humanness 主力対処」** = 同じ operator マシンからの自動アクセスは禁忌
- W1 期 (2026-05-07〜13) 運用ルールでも `/me` 等の lightweight check も含めて API call ゼロが humanness signal 最強化

**判定**: scrape 自体が成功しても、その後 publish 側に BAN リスクが波及する → 二度目の BAN を引いたら復帰路がない (account_2 立ち上げが Stage 2 起動 milestone とリンク済)。

## 判定フロー (next session 参照用)

competitor scout / 任意ハンドル参照系の change を propose する前に:

```
[1] robots.txt に User-agent: ClaudeBot or * の Disallow があるか？
       Yes → scrape 路は撤回。次は [2] へ
       No  → scrape 路は条件付き OK (ただし rate limit / ToS は別途)

[2] Graph API に必要なエンドポイントが存在するか？
       Yes (public 系) → API 路で進める
       No (owner-only) → 次は [3] へ

[3] 後段に operator 手動工程 (= manual scout) を入れて成立するか？
   AND operator が手動工数を払う意思があるか？
   AND 取得データが auto 分析できる後段パイプラインがあるか？
       全 Yes → 部分自動化 propose 検討可
       いずれか No → change 起票しない、memory に記録

[4] Local-First で scrape と publish が同一 fingerprint になるか？
       Yes → publish 側 BAN リスク評価が必要 (Decision 7 等)
       No  → ②③ の判定のみで進める
```

## 横展開できる原則

- **「3 段詰まり」は早期確定の好機**: 1 段で詰まるとつい次の段で抜け道を探したくなるが、3 段全部見て退路なし確定すれば propose の手戻り 1 周分のコストを節約できる
- **後段 auto 分析路がない data 収集 change は提案しない**: 取得しても活用できないデータを集める change は「収集パイプラインだけ作って腐らせる」典型アンチパターン。1228fa25 は memory `feedback_competitor_scouting_automation.md` (ThreadsPosts) で抑制信号化済み
- **ChatGPT 路で先行 propose した直後に user が「Claude Code 自身で」と書き直しを要求するケース** = operator が「自動化前提 + 段階的 fallback なし」を望むケース。Claude 側で robots.txt + API surface + humanness 信号の 3 段事前チェックを **propose 段階で済ませる**べき。/opsx:apply の §1 Pre-flight で初めて exposed = 設計の手戻り 1 周分のコスト

## Links

- [[03_work/threadsposts]] — 2026-05-09 scout-interior-competitors-w1 abort 節
- [[02_diary/2026-05-09]]
- [[05_learn/local-first-anthropic-ops]] — publish↔scrape 同一マシンの fingerprint 干渉
- [[05_learn/threads-graph-api-setup]] — owner-only model の token / scope 一覧
- [[05_learn/instagram-multi-account-isolation]] — IP / device isolation の 4 軸設計
