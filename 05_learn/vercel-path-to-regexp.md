---
title: Vercel deployment 落とし穴 — vercel.json と path-to-regexp v6、preview URL の二重性
category: 05_learn
tags: [topic:vercel-deployment, tech:vercel, tech:path-to-regexp, tech:nextjs]
sources: [3c5be9c0-ca09-48a9-a034-8f8e46003dc3]
updated: 2026-05-03
---

# Vercel deployment — vercel.json と preview URL の落とし穴

## Summary

Vercel に Next.js + LFS 画像配信を deploy するとき遭遇した 2 つの落とし穴：(1) `vercel.json` の `headers` パターンが path-to-regexp v6 で reject される、(2) Vercel UI 上の deploy URL が 2 種類あり、ブラウザで「古い」と見えても実際は世代固定の immutable URL を見ているだけ。SpecDrawing `add-vercel-deployment` 着工時に踏んだ。

## path-to-regexp v6 で headers パターンが reject される

`vercel.json` の `headers` で **unnamed group** を使うと build 段階で `invalid-route-source-pattern` エラー。

NG（旧 v5 互換）:
```json
{
  "source": "/(mask_|shading_|base_).*\\.png",
  "headers": [{ "key": "Cache-Control", "value": "public, max-age=31536000, immutable" }]
}
```

OK（v6 互換）:
```json
{
  "source": "/:prefix(mask|shading|base)_(.*).png",
  "headers": [{ "key": "Cache-Control", "value": "public, max-age=31536000, immutable" }]
}
```

または `source` を分解して 3 ルールに分けるのがいちばんシンプル。

### 検出が難しい理由

- Vercel ダッシュボードの **Deployments** 一覧に build error が出ない場合がある（Status filter のデフォルト挙動か仕様か未確定）
- GitHub PR の **Checks** には "Vercel - Deployment failed" として出る → クリックすると Vercel の error 説明（`vercel.com/docs/errors/error-list#invalid-route-source-pattern`）に飛ぶだけで該当 deploy ページに飛ばないことも
- ローカル `vercel dev` は通る（path-to-regexp の version 差や、headers の eval timing が違う）

→ **PR Checks のリンクを必ず踏む**。Vercel UI と GitHub Checks のどちらか片方しか見ないと build error が長時間放置される。

## Preview URL は 2 種類ある

Vercel ダッシュボードの 1 deploy には:

| 種類 | 形式 | 性質 |
|---|---|---|
| **deploy-immutable URL** | `<project>-<hash>-<scope>.vercel.app` | その deploy commit に固定。新しい push でも書き換わらない |
| **branch-stable URL** | `<project>-git-<branch>-<scope>.vercel.app` | そのブランチの最新 deploy を指す。push で更新される |

ブラウザで開いて「古い」と感じる時は **deploy-immutable URL** を見ていることが多い。**branch-stable URL** に切り替えれば最新が見える。

production も同様で `<project>-<scope>.vercel.app` が production-stable URL。

## Branch deploy が走らない場合

`Settings → Git` を最初に確認:
- **Production Branch**: production にする branch（通常 `main`）
- **Preview Deployments / Git Deployments**: `All Branches` / `Only Production Branch` / `Specific Branches` の制御
- **Deployment Protection** (Pro プラン): branch 制限が別レイヤで存在し得る

`Only Production Branch` 設定で feature branch deploy が走らないケースは多い。

## LFS 画像を Vercel build 時に解決する

`installCommand` に `git lfs pull` を仕込む:

```json
{
  "installCommand": "npm ci && git lfs pull"
}
```

Vercel build image には git-lfs が同梱されているので追加 install 不要。LFS で配信される画像（base / mask / shading PNG など）が pointer file のまま deploy されるのを防ぐ。LFS quota が枯渇していると `batch response: Repository or object not found` で落ちるので、容量超過は data pack 購入か LFS migration を検討。

build smoke check（pointer file 化していないか確認）は `installCommand` に同居させるのが楽:

```json
{
  "installCommand": "npm ci && git lfs pull && file public/assets/base/main/base_natural.jpg | grep JPEG"
}
```

ただし Vercel 標準 build image の `file` コマンド有無は事前確認推奨。

## 環境別 routing（preview と production で挙動を分ける）

`/dev/trace` のような開発専用 UI は preview / development のみ有効化したい:

```ts
// app/dev/trace/page.tsx
import { notFound } from "next/navigation";

export default function Page() {
  if (process.env.VERCEL_ENV === "production") notFound();
  return <TraceTool />;
}
```

`VERCEL_ENV` は Vercel が自動注入する環境変数で `production` / `preview` / `development` を取る。`NODE_ENV` は production と development しか取らないので Vercel 環境を判別できない。

## 検証手順（覚え書き）

1. push 後 GitHub PR Checks に "Vercel - Deployment failed" が付かないか確認
2. branch-stable URL を開く（preview deploy 完了後数分）
3. preview 画像が表示されること、`/dev/trace` が有効なこと確認
4. production-stable URL で `/dev/trace` が 404 を返すこと、`/api/dev/parts` も 404 確認
5. LFS で配信される画像が production でも問題なく表示されること

## Links

- [[05_learn/specdrawing-material-presenter]]
- [[02_diary/2026-05-01]]
- [[06_output/2026-05]]
