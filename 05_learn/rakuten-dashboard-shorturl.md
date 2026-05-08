---
title: 楽天 a.r10.to 短縮 URL の自動取得 — RWS API + dashboard 内部 API + 2 つの罠
category: 05_learn
tags: [topic:rakuten-affiliate, topic:web-automation, tech:nodejs, tech:playwright, tech:rakuten-rws, project:threadsposts]
sources: [e01596df-0fca-4571-bc96-599e88e0e72c, c0b0dfea-a81b-4470-b2f5-07cbbaa4aae8]
updated: 2026-05-09
---

# 楽天 a.r10.to 短縮 URL の自動取得

## Summary

ThreadsPosts の affiliate 自動挿入を Threads 500 字制約に収めるため、
`hb.afl.rakuten.co.jp/...` の長い URL（〜290 字）を `a.r10.to/xxxxxx`
（〜22 字）に短縮する pipeline を構築。Bitly Free（月 10 リンク上限）を
回避しつつ、楽天公式の短縮 URL を **RWS 公開 API + dashboard 内部 API
+ Playwright での 1 回 login** の三層で自動化。

実装中に **RWS API の affiliateId 副作用** と **検索クエリの中黒バグ**
の 2 つの罠で URL が全件壊れる事故が起き、両方とも修正済み。
詳細は ThreadsPosts repo の `pipeline/lib/rakuten_dashboard_client.js` /
`pipeline/resolve_rakuten_links.js` を参照。

## 全体アーキテクチャ — CI と人手の責務分離

```
┌─ CI (GitHub Actions, 自動) ────────────────────────────────────┐
│ resolve_affiliates.yml (SHORTEN_URLS=false)                    │
│   - 楽天 RWS API で long URL を refresh                         │
│   - hot set 計算・cooldown・差分書き戻し                         │
│   - 既存 a.r10.to は preserved status で保護                    │
│   - bot 検出リスクゼロ (login 試行なし)                          │
└────────────────────────────────────────────────────────────────┘
                          ↓ pull
┌─ ローカル (人手, 週1回〜) ─────────────────────────────────────┐
│  npm run rakuten:login   (session 期限切れ時のみ)                │
│  npm run resolve:rakuten -- --hot --write                       │
│  git commit && git push                                          │
└────────────────────────────────────────────────────────────────┘
                          ↓
┌─ CI (publish.yml, 30分毎) ─────────────────────────────────────┐
│  short URL 含んだ products.yaml を読んで Threads に投稿         │
└────────────────────────────────────────────────────────────────┘
```

CI は **公開 API のみ** で動かして bot 検出リスクをゼロに、
ダッシュボード操作（短縮 URL 取得）は **ローカル人手 + 1 セッションあたり数秒** で済むようにした。

## 罠 1 — RWS API は `affiliateId` を渡すと `Item.itemUrl` も書き換える

**症状**: 自動生成した `https://a.r10.to/xxxxxx` をブラウザで開くと
**全件が楽天トップにリダイレクト**して商品ページに着地しない。
中間で `%252F` の二重エンコードが発生していた。

**原因**: 楽天 RWS API（`/IchibaItem/Search/20260401`）は、`applicationId`
だけでなく `affiliateId` を渡すと、`Item.itemUrl` まで `Item.affiliateUrl`
と同じ `hb.afl.rakuten.co.jp/...` に書き換える。

```js
// affiliateId 無し
itemUrl: "https://item.rakuten.co.jp/healthy-good/chr-485/"   // clean

// affiliateId 有り（我々が普段渡している状態）
itemUrl: "https://hb.afl.rakuten.co.jp/hgc/<id>/?pc=..."      // wrapped
```

これを dashboard の `freelink?u=<itemUrl>` に渡すと、ダッシュボードが
**「既に存在するアフィリエイトリンク」と誤判定** して `/link/pc/url`
（anonymous URL link）に redirect、生成される短縮 URL が **旧パス
`/hgc/` + `pc=` の入れ子** で破綻する。

**修正**: `extractCleanItemUrl(itemUrl)` ヘルパで dashboard 投入前に
クリーンな `item.rakuten.co.jp/...` URL を取り出す:

```js
function extractCleanItemUrl(itemUrl) {
  if (itemUrl.startsWith('https://hb.afl.rakuten.co.jp/')) {
    // /hgc/...?pc=<encoded clean URL>&... から pc を取り出して decode
    const url = new URL(itemUrl);
    const pc = url.searchParams.get('pc');
    return pc ? decodeURIComponent(pc) : itemUrl;
  }
  return itemUrl.split('?')[0];   // rafcid 等のクエリを除去
}
```

修正後は `/ichiba/<affiliate-id>/?pc=<clean item URL>` の正しい構造で
短縮 URL が生成され、楽天商品ページに正しく着地。

**横展開可能な学び**: アフィリエイト系 SDK / API は **「affiliate id を
渡すと別のフィールドにも副作用が伝播する」** ケースがある。SDK の入力
パラメータと出力フィールドの直交性を仮定せず、affiliateId 有無での
レスポンス差分を実機で確認しておくこと。

## 罠 2 — 検索クエリの中黒（`・`）が AND マッチで 0 件

**症状**: `steamed_soybeans` だけ `auto_resolve_warning: rakuten_no_match`
になり 7 日 cooldown。products.yaml の `name` は人間向けの
`蒸し大豆・豆類ミックス` だった。

**調査**: 楽天 RWS Search を変えて叩いてみると:

```
"蒸し大豆・豆類ミックス"  → 0 件
"蒸し大豆 豆類ミックス"   → 0 件 (旧 fallback、中黒を半角空白で置換)
"蒸し大豆"                → 343 件 ← ここまで降りれば取れる
```

楽天市場の検索は **AND マッチ** なので、複合語をスペース区切りにしても
両方の単語を含む商品が無いと 0 件になる。`蒸し大豆` 単独まで降りれば
ヒット商品が出てくる。

**修正（汎用）**: `generateQueryVariants` で 3 段階フォールバック化:

```
[<full>] → [<先頭2語>] → [<先頭1語>]
順に試して最初に hit したクエリを採用
```

**修正（個別）**: `steamed_soybeans` に
`rakuten_search_query: '蒸し大豆'` を追加（`pickSearchQuery` で参照済み
の hooks）。`name` は人間可読性優先、検索クエリは検索精度優先で別管理。

**横展開可能な学び**:
- 商品マスターの `name` は人間向け説明的表記で、検索クエリは別フィールドに
  分離するのが筋（マスターデータ設計の定石）
- 中黒 `・` で繋いだ複合語は楽天検索でほぼヒットしない（楽天は AND マッチ）
- 1 段だけのフォールバックは複合語商品で失敗しがち、**「徐々に短くする」
  階層的アプローチ** が複合語問題に汎用的に効く

## 罠 3 — 楽天ログインのリダイレクト待ち（実装初期）

旧実装は `https://affiliate.rakuten.co.jp/`（ランディングページ、
**未ログインでもアクセス可能**）に navigate して、ページ表示で「成功」
判定 → 無効な 8 cookie を保存して終了する病的挙動だった。

**修正**: ログイン必須ページ
（`/link/pc/item?type=item&me_id=1369455&item_id=10000148`）に navigate
して、未ログインなら `login.account.rakuten.com` に redirect → ユーザが
ログイン完了で元の dashboard ページに戻る → URL が
`affiliate.rakuten.co.jp/link/pc/item` で始まることを検知 → session 保存。

`PLAYWRIGHT_HEADLESS` env も正しく読むよう修正（旧実装は env を未参照で
常に headless）。

## RWS API 移行 — 2026-05-14 で旧 API 廃止

楽天は 2026-05-14 で旧 RWS API を廃止。新 API は **UUID + accessKey + Origin**
ヘッダ必須。

```
GET https://openapi.rakuten.co.jp/ichibams/api/IchibaItem/Search/20260401
  ?applicationId=<app_id>
  &affiliateId=<affiliate_id>
  &keyword=<query>

Headers:
  Origin: <registered origin>      ← 必須
  X-Rakuten-AccessKey: <key>       ← 必須
  X-Rakuten-RequestId: <UUID v4>   ← 必須
```

新 API + 上記の罠 1 修正でようやく短縮 URL が安定生成できるようになった。

## ダッシュボード内部 API のセッション管理

短縮 URL 生成は dashboard 内部 API（`/api/link/item/shorturl`）を叩くが、
これは **session cookie + XSRF token** で叩ける普通の Web API。

- セッション cache: `.cache/rakuten_session.json`（数日〜数週間有効）
- 期限切れ警告が出始めたら
  `rm .cache/rakuten_session.json && PLAYWRIGHT_HEADLESS=false npm run rakuten:login`
  で再生成
- 楽天 2FA は機械化困難 → **人手 + cache の分業が現実解**

## 運用 SOP

`docs/operations.md` に記載済（ThreadsPosts repo）。要点:

1. CI が long URL を毎日 refresh（`SHORTEN_URLS=false`、login 試行なし）
2. 週 1 回ローカルで `npm run rakuten:login`（セッション期限切れ時のみ）
3. 同じ週 1 回で `npm run resolve:rakuten -- --hot --write`（11 商品で数秒）
4. `git commit && git push`、CI publish.yml が 30 分毎に短縮 URL 込みで Threads 投稿

## Links

- [[03_work/threadsposts]]
- [[05_learn/threads-graph-api-setup]]
- [[06_output/2026-05]]

## ⚠️ 旧 RWS Ichiba API は 2026-05-14 完全停止 — 新 endpoint への移行（2026-05-07 追加）

楽天 Web Service が 2026-02-10 に完全リニューアル済。**旧 endpoint と旧形式 applicationId は 2026-05-14 に完全停止** (本ページ初稿 2026-05-03 時点であと 11 日)。account_1 (oheyamemo) 立上げ時に user 指摘で再確認した。

| 項目 | 旧仕様 | 新仕様 |
|------|------|------|
| Endpoint | `https://app.rakuten.co.jp/services/api/IchibaItem/Search/...` | `https://openapi.rakuten.co.jp/ichibams/api/...` |
| `applicationId` | 19 桁数字 (例: `0cf35ebb...` 系) | **UUID 形式** (例: `375dca6b-f31d-4426-adbc-fc624ad92a36`) |
| `accessKey` | 不要 | **`pk_` 始まり、URL param 必須** |
| Developer Portal | `webservice.rakuten.co.jp` | `https://openapi.rakuten.co.jp/dashboard/` |
| 完全停止 | 2026-05-14 | — |

**ThreadsPosts pipeline の状態**: `pipeline/resolve_rakuten_links.js` は新 endpoint 対応済 (memory `reference_rakuten_api_2026_renewal.md` の archived `auto-resolve-rakuten-links` 投入時に切替)。新規 account 立上げ時 (例: account_1 oheyamemo) は **必ず新 Developer Portal でアプリを作成** する。

**`a.r10.to` 短縮 URL pipeline (本ページの主題) は別系**: アフィリエイト管理画面 (`https://affiliate.rakuten.co.jp/`) の dashboard 内部 API を Playwright で叩く構成なので、RWS Ichiba API の renewal とは独立。短縮 URL 取得ルートは現状のまま動作する。

→ memory `reference_rakuten_api_2026_renewal.md` で具体値・サンプルレスポンス込みの参照を保持。詳細経緯は [[02_diary/2026-05-07]] / [[03_work/threadsposts]]。
