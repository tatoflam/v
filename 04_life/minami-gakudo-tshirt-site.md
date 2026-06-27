---
title: みなみ学童 Tシャツ申し込みサイト (Google Form 置換)
category: 04_life
tags: [domain:minami-gakudo, entity:minami-gakudo, tech:cloudflare-pages, tech:github-pages, tech:google-apps-script, tech:google-sheets, tech:openspec, tech:github-actions, tech:clasp, stage:live, milestone:tshirt-form-live]
sources: [572df4d1-cf1f-491c-bfe8-c608cb79ab67, c30a13e1-06cb-47b7-a1db-fd47e70dedb1]
updated: 2026-06-27
---

# みなみ学童 Tシャツ申し込みサイト

## Summary

[[04_life/minami-gakudo-fubokai-2026|みなみ学童父母会]] で運用していた
**Google Form 版 Tシャツ申し込みフォーム**
(`docs.google.com/forms/d/16hMrsuuZCR2sM3Bit2-4Uz8bfWHxQsc8tSXDdMhPfJM/edit`) を
カスタム静的サイトに移行する初期検討。
**動的明細 (複数種類 × サイズ × 枚数)** が Google Form ではうまく組めない点が移行最大の動機。
2026-06-25 19:51-23:08 JST のセッションで要件整理 → アーキ決定 → 新リポジトリ
[`tatoflam/minami-gakudo-tshirt`](https://github.com/tatoflam/minami-gakudo-tshirt)
(private) を作成、OpenSpec change `tshirt-order-site` を `valid` 状態で初期コミット
`468c292` 上に push 完了。実装は次セッション以降。

## アーキ判断 (design.md より)

```
[利用者ブラウザ]
   カスタム HTML/JS フォーム  ← Cloudflare Pages or GitHub Pages (無料・HTTPS)
        │ fetch POST JSON
        ▼
[Google Apps Script Web App] ← サーバー兼 DB 書き込み口 (無料)
        │ ① 1行追記
        ▼
[Google スプレッドシート]   ← DB 兼 一覧画面 (送信日時付き自動蓄積)
        │ ② 自動返信メール (申込内容を整形して本人へ)
        │ ③ 入庫確定時、対象行だけ選んで一斉メール (手動トリガー)
        ▼
[Gmail / MailApp 送信]
```

採用理由:
- **静的フロント (GH/CF Pages)** = 無料 HTTPS、リポジトリ管理で更新追跡容易
- **GAS Web App** = サーバーレスでフォーム受付 + メール送信が一気通貫、無料
- **スプレッドシート = DB** = 受付内容の一覧 + 入庫ステータス手動操作 + 一斉メール
  対象選択がスプレッドシートの UI でそのまま運用できる (= 新規 DB 不要)
- 連絡先 (`tatsuroh.319@gmail.com`, `ataken01@gmail.com`, LINEID `tatohomma`) と
  GAS の Web App URL は `config.js` で外部化、`.gitignore` 済

なぜ Google Form のままにしないか:
- **複数の種類・サイズ・枚数を「追加して」指定**できる動的フォームが Form の
  固定枠では作れない (= ユーザーが「アイテム1 / アイテム2 / アイテム3 …」の不格好な
  固定列を埋める形になり、現行フォームの「サイズ表がわかりにくい」問題が拡大する)

## 取り扱う Tシャツ品番 (大人/女性/子供 3 ライン)

- **大人用**: `085-CVT-TP` https://tonyagai.shop/?pid=190241257 — XS/S/M/L/XL/XXL/XXXL
- **大人用 (女性)**: `085-CVT-TL` https://tonyagai.shop/?pid=190241258 — WM(157)/WL(165)
- **子供用**: `085-CVT-TK` https://tonyagai.shop/?pid=190241255 — 100/110/120/130/140/150

## 旧フォームからの変更点 (要件)

1. 連絡先 (問い合わせ先メール + LINEID) はコード埋め込みせず `config.js` で外部化
2. サイズ表セクションは削除 (「わかりにくい」)
3. サイズ指定を動的明細 (種類/サイズ/枚数を 1 セットとして N 件追加可能) に変更
4. 氏名 + 連絡手段 (電話/メール/LINEID のいずれか) は必須
5. 受渡方法は自由記述 (例: 7/25 第 2 回キャンプ実行委員会 / 8/22 第 3 回キャンプ実行委員会
   などで受け取り)
6. PayPay 事前支払希望はオプションのラジオボタン (選択しなければ受け取り時支払)
7. 「納期は募集締切から 1 ヶ月ほど」を明文表示

## OpenSpec change `tshirt-order-site`

新リポジトリ `~/repo/github/tatoflam/minami-gakudo-tshirt/` で
`openspec` 初期化 → change `tshirt-order-site` を 4/4 アーティファクト完成で
`openspec validate` → **valid** ステータス。

| ファイル | 内容 |
|---|---|
| `openspec/changes/tshirt-order-site/proposal.md` | 移行動機・変更点・3 ケイパビリティ |
| `.../design.md` | アーキ判断 (CF Pages / GAS / Sheets DB)、リスク、移行/ロールバック、未決事項 |
| `.../specs/order-form/spec.md` | 公開フォーム要件 (動的明細・サイズ切替・合計計算・連絡手段必須・設定外部化) |
| `.../specs/order-intake/spec.md` | 受付バックエンド (永続化・サーバ検証・ハニーポット・自動返信メール) |
| `.../specs/order-fulfillment/spec.md` | 管理運用 (一覧・入庫ステータス・一斉メール再送防止・PayPay 可視化) |
| `.../tasks.md` | 実装ステップ 5 グループ・全 32 タスク |
| `README.md` / `.gitignore` | アーキ概要 + `config.js` 等の秘匿設定除外 |

## 次工程

- 次セッションで `~/repo/github/tatoflam/minami-gakudo-tshirt/` を開き、tasks.md の
  5 グループ 32 タスクに沿って実装着手 (フロントの HTML/JS → GAS Web App → スプレッドシート
  テンプレ → 自動返信メール → 入庫一斉メール)
- 公開直前まで private 維持。公開予定のフォーム性質上、後で
  `gh repo edit tatoflam/minami-gakudo-tshirt --visibility public` で公開化候補
  (`config.js` は `.gitignore` 済のため連絡先・GAS URL は漏れない)

## 実装着地 + 本番公開 (2026-06-25→27, session c30a13e1)

6/25 初期コミット直後を引き取り、フロント実装 + GAS バックエンド + GitHub Actions →
Cloudflare Pages 自動デプロイ + clasp による GAS 再デプロイ までを一気通貫で着地。
2026-06-27 段階で **公開フォームが live**、締切 (2026-07-03) まで募集中。

### 公開 URL

- **公開フォーム**: https://minami-gakudo-tshirt.pages.dev (Cloudflare Pages)
- **GAS Web App (バックエンド)**:
  `https://script.google.com/macros/s/AKfycbzFSQWRznHf5e4Lr4RwvLqiqPsjnVp4RL9aODobECbdXATeTJHk4oiroWdDo1WybowQ/exec`
  (deployment ID `AKfycbzFSQWRznHf5e4Lr4RwvLqiqPsjnVp4RL9aODobECbdXATeTJHk4oiroWdDo1WybowQ`)

### CI/CD

- GitHub Actions `main` push 連動で Cloudflare Pages へ自動 build/deploy
  (`839e6ee ci: GitHub Actions で main push 時に Cloudflare Pages 自動デプロイ` +
  `61ea88f ci: push 連動デプロイの動作確認`)。デプロイ URL は `*.pages.dev` で固定、
  preview には別 hash の suffix が付く。
- GAS 側は `clasp push && clasp deploy` で同一 Web App ID を保ったまま再デプロイ
  (= URL 不変、版だけ更新)。最新版 `@2` は電話 validation 反映済。

### 公開フォーム機能 (実装着地)

- **動的明細**: 種類 × サイズ × 枚数 を 1 セットとして N 件追加可能 (旧 Form の固定枠
  問題を解消)
- **学年プルダウン化**: テキスト入力 → 1年/2年/3年 のセレクト (`1d1846a`)
- **電話/メール簡易検証**: 数字+ハイフンのみ・最低 10 桁 (client + server 両方)、
  メールは `@` 必須形式チェック (`1d1846a`)
- **プライバシー文言**: 「いただいた個人情報は、Tシャツのお申し込み対応以外の用途では
  使用いたしません。」(押し付けがましくないトーン、`1d1846a`)
- **迷惑メール注記**: メール送信者は迷惑メールフォルダも要確認の旨を完了画面と
  フォーム下部に淡く併記
- **読みやすさ整備** (`94a5eab`): 段落分け、「学童関係者はどなたでも購入できます」
  「目印」を太字、「1枚 800円」を青強調
- **締切後も受付明記** (`94a5eab`): 「締切以降もお申し込みを受け付けます」
  (締切は GitHub Secrets 経由で build 時注入、`config.js` に外部化済)

### OpenSpec change の archive

- `2c34104 spec: tshirt-order-site をアーカイブ＋本体specsへsync` — 当初の OpenSpec
  change `tshirt-order-site` を本体 specs に同期 + archive 移動

### 学び (Cloudflare Pages × GAS Web App)

- Cloudflare Pages の **デプロイ URL は固定** (`<project>.pages.dev`)、production
  ブランチが変わっても URL は維持。preview だけ別 hash。
- GAS Web App の **再デプロイは Web App ID 不変** (=URL 不変)。`clasp deploy
  --deploymentId <id>` で同一エンドポイントの版だけ進める運用が安定。
- バリデーションは **二重持ち** (client = 即時 UX フィードバック、server = 検証
  権威)。電話は表示は「数字とハイフンのみ」、保存はハイフンを strip した数字のみで
  正規化。
- Cloudflare Pages の 25MB アセット制限を意識して、ビルド成果物は `dist/` 限定に
  寄せる方針。
- Node.js 20+ on GitHub Actions (= Cloudflare Pages action の現行要件)

## Links

- [[04_life/minami-gakudo-fubokai-2026]] (親活動 = 父母会本体)
- [[06_output/2026-06]] (= GitHub repo push + Cloudflare Pages live URL + GAS Web
  App 記録)
- [[02_diary/2026-06-25]] — 初期 design + repo push
- [[02_diary/2026-06-27]] — 実装着地 + 本番公開記録 (run-107 ingest)
