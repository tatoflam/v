---
title: みなみ学童 Tシャツ申し込みサイト (Google Form 置換)
category: 04_life
tags: [domain:minami-gakudo, entity:minami-gakudo, tech:cloudflare-pages, tech:github-pages, tech:google-apps-script, tech:google-sheets, tech:openspec, tech:github-actions, tech:clasp, stage:live, milestone:tshirt-form-live, milestone:item-level-fulfillment, milestone:pr-1-merged]
sources: [572df4d1-cf1f-491c-bfe8-c608cb79ab67, c30a13e1-06cb-47b7-a1db-fd47e70dedb1, 2fbcae5b-54ac-42db-83bf-2afb5359bd66]
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

## 入庫＝明細単位 + 発注便で運用モデル再設計 (2026-06-27、session 2fbcae5b、PR #1 MERGED)

本番公開 (`c30a13e1`) の同日午後、運用モデルを **申込(人)単位 → 明細(種類×サイズ)
単位** へ再設計。`発注便` (= 便1, 便2…) を導入し、フォームを継続開放したまま区切って
発注確定する形に変更。[PR #1](https://github.com/tatoflam/minami-gakudo-tshirt/pull/1)
で `4a62021` を merge (`9b6efef`)、GAS Web App `@3` で本番反映。

### なぜ申込単位を捨てたか

旧モデルは `入庫ステータス` `受渡日` `一斉連絡済` を `申込` シート (= 人単位) に
持っていた。実務では:

- **発注はサイズ別バッチ**で出すので「同一人物の T シャツ 3 種類」が同時に揃わない
- **入荷もサイズ別**にバラバラに来る → 入庫済の分から先に渡したい (= 部分受渡)
- 募集を切らずに継続開放しつつ、ある時点までの未手配だけ便発注したい

→ 状態を **明細(種類×サイズ)単位** に移し、`発注便` で論理的に区切るのが業務粒度と
一致する。`申込` シートのステータスは「入荷確定 2/3」のような **派生サマリ** で十分。

### 採用した運用モデル

- `明細` シートに `入庫ステータス` `発注便` `受渡日` `一斉連絡済` の 4 列を持つ
- 1 申込 = 1 行 + N 明細行 (= 種類×サイズ×枚数の組ごと)。明細 ID は採番で安定参照
- **発注便**: 提案時点では `便N` (連番) を既定、日付式 (`2026-07-04 便`) も可
  (= 体裁は運用で確定予定)
- **部分受渡**: 明細ごとに「入庫確定」「受渡済」を立てる、対応する申込は派生サマリで集計
- **一斉連絡**: 「入庫確定 AND 未連絡」の **明細** を人ごとに 1 通へ束ねて送る。
  連絡済フラグも明細単位 → 後便で同じ人に別 T シャツが入っても、初回連絡済アイテムは
  再連絡対象から自動的に外れる (= 重複連絡の構造的防止)

### 主要コード変更 (PR #1、11 files / +763 / -104)

| ファイル | 変更内容 |
|---|---|
| `apps-script/Storage.gs` | 明細ヘッダ拡張 (4 列追加)、明細 ID 採番、`getItems_()` 系の絞り込み引数 |
| `apps-script/Admin.gs` | 便発注フロー (便番号採番 + 対象明細マーキング)、集計絞り込み (便/サイズ/未連絡)、`/broadcast-pending` を明細単位化 |
| `apps-script/Config.gs` | `ADMIN_EMAILS = ['ataken01@gmail.com', 'tatsuroh.319@gmail.com']` を集約 (= 全送信メールの CC 既定) |
| `apps-script/Mailer.gs` | 明細粒度の broadcast 関数 (1 人 1 通に束ねる + 連絡済フラグ更新を明細側に書く) |
| `apps-script/Migrate.gs` (新規) | `migrateToItemStatus_()` ヘルパ — 既存 `申込` シートの 3 列を明細側に転記 + 申込側の該当列を派生サマリへ縮退 |
| `README.md` | 運用モデル + ライフサイクル図 + メニュー一覧 + 移行手順を追記 |

### OpenSpec change `item-level-fulfillment` の同期

- 同セッション内で `/opsx:propose` → `/opsx:apply` → `/opsx:archive` を完走
- ADDED/MODIFIED 要件を本体 `openspec/specs/order-fulfillment/spec.md` に反映
- 全 3 spec (`order-form` / `order-intake` / `order-fulfillment`) で `openspec validate` ✅

### 設計上の学び

- **状態の置き場は業務粒度に合わせる** — 発注・入荷・受渡・連絡が種類×サイズで起きる
  運用なら、状態も最初から明細単位に。後付けで申込→明細にバラすより、最初から
  「申込はサマリ」と決め切るほうが補助フラグが増えない
- **継続開放 × 区切り発注を成立させる装置 = 発注便**: 締切と発注を分離。締切は周知
  UI 上の目印に格下げし、発注は便番号で論理的に区切る
- **送信宛先の単一集約**: `ADMIN_EMAILS` を `Config.gs` 1 か所に集約。名簿変更時の
  漏れリスクを構造的に消す

### 関連 memory

- `item-level-fulfillment-model` — 運用方針固定 (= 申込単位を捨てて明細＋便で持つ
  根拠と適用箇所)

## Links

- [[04_life/minami-gakudo-fubokai-2026]] (親活動 = 父母会本体)
- [[06_output/2026-06]] (= GitHub repo push + Cloudflare Pages live URL + GAS Web
  App 記録 + PR #1 merge)
- [[02_diary/2026-06-25]] — 初期 design + repo push
- [[02_diary/2026-06-27]] — 実装着地 + 本番公開 (run-107) + 入庫=明細単位再設計 + PR #1 merge (run-108)
