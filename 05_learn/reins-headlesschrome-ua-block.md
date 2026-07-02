---
title: REINS WAF が HeadlessChrome UA を 503 で弾く
category: 05_learn
tags: [topic:waf, topic:user-agent-spoofing, topic:scraping, tech:selenium, tech:headless-chrome, tech:python, entity:reins]
sources: [e702af57-704f-45d2-b1c7-5545a1990670, 8c19b6ca-f61c-41d2-8c1c-0e5643f22140]
updated: 2026-07-02
---

# REINS WAF が HeadlessChrome UA を 503 で弾く

## 症状

Selenium で REINS (Real Estate Information Network System) を巡回するスクリプトを
CI で動かすと、HTTP 503 が返り続ける。同一 IP でも **curl / urllib は通る、
Headless Chrome だけ落ちる**。

## 原因

REINS の WAF はリクエストの `User-Agent` ヘッダをパターンマッチして
**"HeadlessChrome"** 文字列を含むものを block している。Selenium で
`chromedriver --headless=new` 等で起動した Chrome は既定で
`Mozilla/5.0 (...) HeadlessChrome/<ver> Safari/...` を送出するため弾かれる。

## 修正

WebDriver の起動オプションで UA を通常 Chrome に上書きする:

```python
opts = ChromeOptions()
opts.add_argument("--headless=new")
opts.add_argument(
    "--user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36"
)
```

(具体の文字列は被スクレイピング側で正常に通る Chrome のものに合わせる。
更新が止まると将来ブロックされるリスクがあるため、ローテーション戦略は別途検討)

## 診断パターン — UA matrix probe

WAF 起因か切り分ける最短手順は、複数 UA で同一 URL に投げて 200/503 の境界を見る:

| UA | 想定挙動 |
|---|---|
| `curl/8.x` | 200 (= シンプル UA は通す WAF が多い) |
| Python `urllib/3.x` | 200 (同上) |
| 通常 Chrome (デスクトップ) | 200 |
| `HeadlessChrome/<ver>` | 503 (= bot 判定) |

curl / urllib が通って Headless Chrome だけ落ちれば、ほぼ確実に **UA パターン
matching** が原因。IP block や cookie 不足ではない。

## 一般化

- **WAF は IP / レート / UA / ヘッダ構成 を組み合わせて bot を判定する**。Headless
  ブラウザを業務利用するときは UA だけでも先回りで Chrome 風に書き換えるのが
  defensive な既定値。
- `navigator.webdriver = true` 等の DOM 検知も別経路で残るため、より厳密な WAF を
  相手にする場合は `undetected-chromedriver` 等の評価も視野に。

## 出典

- session `e702af57` (`meguruit/land-searcher`, 2026-06-26→27): REINS WAF 503
  根治。commit `7bdc449` で UA 上書き、`b13cca1` / `30cc344` で UA matrix probe を
  仮設 → 確認後 `c79bf69` で revert。
- session `8c19b6ca` (`meguruit/land-searcher`, 2026-06-26→07-02): 上記と並行の
  原因追跡セッション。GCP 東京 VM (asia-northeast1-a) から curl 200 が返ることを
  一度確認して "IP block ではない" を証明した後、GitHub Runner 上での UA matrix
  probe に切り替えて **`HeadlessChrome` UA だけ 503、通常 Chrome UA なら 200** を
  同一 IP で観測し真因確定。GCP 移行は不要という判断で GitHub Actions 運用のまま
  close。
- [[03_work/land-searcher]]
