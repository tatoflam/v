---
title: Woodone「ラクラクプレゼン」(/pboard/) アーキテクチャ調査
date: 2026-04-25
source: https://wwws.woodone-net.jp/pboard/?ref=cp
tags: [architecture, canvas, color-simulator, angular, createjs, sprite]
---

# Woodone「ラクラクプレゼン」(`/pboard/`) アーキテクチャ調査レポート

調査日: 2026-04-25
対象URL: https://wwws.woodone-net.jp/pboard/?ref=cp
調査手段: Playwrightでのブラウザ実行 + アセットURL直叩き（CSS/JSONの実体取得）

## 1. 機能要件（観察できた範囲）

「プレゼンボード（建材カタログプレゼン作成ツール）」で、ユーザは次を行える。

- **ベース台紙の選択** — 表紙(黒/青/茶)、自動配置(オリジナル/商品一覧/建具一覧/玄廻/階段/収納/カウンター/建具表)、フリー、オリジナルテンプレートの4タブ
- **建材・建具の配置** — シリーズ・デザイン・カラー・間口・高さ・開き方・ミラー・タイプの多軸（=カタログ全軸）で製品バリエーションを選び、パース画像として板上に貼り付け
- **編集レイヤ** — 画像/テキスト/シェイプ/ライン追加、コピー&ペースト、最前面/最背面、整列、回転、Undo/Redo、全選択、全削除、ズーム
- **入出力** — 保存、PDF出力（サーバ側で2840×2000の高解像レンダ）、終了
- **状態のディープリンク** — `?ref=cp` のほか、隠しinput `#tateguId` `#colorId` から建具ID/カラーIDを受け取って初期表示

URLの `?ref=cp` はリファラ識別子（カタログプリント由来）と推定。色シミュレータ単体ではなく、プレゼンボード上で建材ごとに色・パターンを選択する作り。

## 2. 技術スタック

| レイヤ | 採用技術 |
|---|---|
| フレームワーク | **Angular 6.1.6**（タグprefix `wo-`、`_nghost`/`_ngcontent` 属性、Angular CLI 出力 `runtime/polyfills/scripts/main` + ハッシュバンドル） |
| 補助JS | **jQuery 3.3.1**、**jQuery UI**（accordion）、**Spectrum**（カラーピッカー、`wo-spectrum` ラッパー）、**EaselJS/CreateJS**（`shapeObject.json` のコンパクトパスは Toolkit for CreateJS（旧 Flash CC HTML5 Canvas エクスポート）形式） |
| 画像合成 | `<canvas>` 1105×1132（メイン編集面）+ `external-color-canvas` 150×150（補助） |
| アイコン/スウォッチ | CSSスプライト（`sprites.<hash>.png` + 部品別 `sprites-color/design/series/maguchi/hirakitype/height/mirror/type/designK/fitting.css`） |
| バックエンド | **PHP**（`io.php`, `/pboard/DataServ`, `/woodone/api/printHistory`、サーバ側PDF/印刷画像生成 2840×2000） |
| エンコーディング | Shift_JIS（`<meta>` は utf-8 と書きつつ実体はSJIS） |
| 計測 | Pardot (`pi.pardot.com`)、GTM、GA4 |

検出したAngularコンポーネント: `wo-app-root`, `wo-app-leftside`, `wo-app-presenter`, `wo-app-canvas`, `wo-app-footer`, `wo-tab`, `wo-imagebutton`, `wo-selectmenu`, `wo-numberspinner`, `wo-spectrum`, `wo-block-ui`, `wo-template-dialog`, `wo-message-dialog`

## 3. 「色・パターンを選ばせる」実装の核心

肝は **「リアルタイムにピクセルを recolor していない」** という点。

### 3.1 スウォッチUI（カラーピッカー側）

- `assets/Sprite/fitting/sprites-color.css` に **製品ごとのカラーコード単位**（例 `mBN`, `mCP`, `p4A` …）で 40×40 のGIF/PNGをクラス化
- 各カラーは `通常 / _on / _over` の3ステート画像を持つ典型的なロールオーバーUI
- カラーパレット全体やシリーズボタン・上下矢印などUI部品は単一PNG `sprites-color-tool.png` に統合し、`background-position` で切り出し（約280クラス、座標例 `-371px -281px`）
- フリーカラー入力には **Spectrum** コンポーネント（`sp-palette-toggle`/`sp-cancel`/`sp-choose`）

### 3.2 パース画像合成

- 製品バリエーションごとに **事前レンダ済みのパース画像を全パターン用意**（`series × design × color × maguchi × height × hirakitype × mirror × type` の組み合わせ網羅）
- 命名規則は CSSクラス名と1:1 対応：例 `.design-N-FG`(44×71px)、`.color-mBN`(40×40px)
- `template.json` の各ページ定義が `swf`(現は.png)と `xml`(レイアウト) を指す。XMLには配置スロット座標が入っており、Angular側のパーサがcanvasに配置
- Canvas描画は **CreateJS**：`shapeObject.json` に格納された "コンパクトパス" データ（`AhXDPQgngRgg…` のような独自base32エンコード）はFlash→HTML5 Canvasへの自動移植時に出力される形式。SVGではなく、CreateJSの `Graphics.decodePath` で読まれる
- 隠し input `#tateguId` `#colorId` でディープリンク → Angular初期化時に `DataServ` を叩いて該当の事前画像URLを取得 → `canvas.drawImage` で描画

### 3.3 保存・印刷

- 編集状態は xml 形式で `io.php` に POST されて永続化（旧Flex資産そのまま）
- 印刷時は `print_php_url` がサーバ側で 2840×2000 PNG をレンダし `print_image_url` から配布
- **ブラウザのcanvasは編集用、最終出力はサーバ生成** という二層構成

### 3.4 出自

`flex_action_url: "io.php"`、`swf` キー、`*.xml` レイアウト、CreateJSコンパクトパスの併存から、**元はAdobe Flex/Flash 製で、HTML5 (Angular6 + CreateJS) へ移植** したものとほぼ確定。Shift_JISはその名残。

### 3.5 実体ファイル例

```css
/* sprites-color.css — 製品ごとカラーコードに1ファイル */
.color-mBN     {width:40px;height:40px;background:url("color/mBN.gif") no-repeat;}
.color-mBN_on  {width:40px;height:40px;background:url("color/mBN_on.gif") no-repeat;}
.color-mBN_over{width:40px;height:40px;background:url("color/mBN_over.gif") no-repeat;}

/* sprites-color-tool.css — UI部品は単一PNGをbackground-positionで切り出し */
.f_c_bc       {width:30px;height:30px;background:url("./sprites-color-tool.png") no-repeat -371px -281px;}
.button_down  {width:40px;height:40px;background:url("./sprites-color-tool.png") no-repeat  -75px -531px;}

/* sprites-design.css — デザインバリエーションも1コードに3ステート */
.design-N-FG     {width:44px;height:71px;background:url("design/N-FG.gif") no-repeat;}
.design-N-FG_on  {width:44px;height:71px;background:url("design/N-FG_on.gif") no-repeat;}
.design-N-FG_over{width:44px;height:71px;background:url("design/N-FG_over.gif") no-repeat;}
```

```json
// serverConfigLan.json — Flash由来の名残が残るバックエンド設定
{
  "user_url":"https://ppo.woodone.net/",
  "flex_action_url":"io.php",
  "image_url":"/pboard/assets/image/",
  "tool_color_data_url":"assets/data/color/",
  "tool_fitting_data_url":"assets/data/fitting/",
  "dataserv_url":"/pboard/DataServ",
  "print_image_url":"/printImage/",
  "print_image_height":"2000",
  "print_image_width":"2840",
  "print_php_url":"/woodone/api/printHistory"
}
```

## 4. 評価

**強み**

- ピクセル recolor 不要で見た目の品質が常にカタログ通り（プロが撮ったレンダ画像のまま）
- 描画が `drawImage` 主体で軽い・ブラウザ依存が小さい・印刷品質をサーバ生成で担保
- データが xml/json に切り出されており、商品追加=画像とxmlを差し替えるだけで済む

**弱み**

- バリエーション数 × ステート数で **画像点数が爆発**（数万点規模）。新色追加=全パース再レンダ
- CSSスプライト管理のCIが必要（`sprites.f0db…png` のハッシュ命名から自動生成パイプラインがあるはず）
- Angular 6 / Shift_JIS / Flex出自XMLはもう保守限界。CreateJSコンパクトパスはSVGに戻すと差分PR可
- 真のユーザーフリーカラー（任意HEX）は `external-color-canvas` 経由でしか反映できない（おそらくスウォッチタイル化のみで、パース画像本体への反映は不可）

## 5. もし自前で実装するなら（推奨アーキ）

### A. 画像戦略を二層に分ける

- *正規バリエーション*: 今と同じく事前レンダ採用（写実性最優先のカタログUI）
- *任意色のシミュレーション*: ベースパース画像を **マスク画像 + 色合成** で実装
  - 部材ごとに `base.jpg` + `mask_<part>.png`（αチャンネル）+ `shading_<part>.png`（明暗のみ）を保持し、canvasで `multiply`/`overlay` 合成 → 任意色をユーザに開放できる
  - WebGL（Three.js / regl）を使えばGPUで瞬時。CSSの `filter: hue-rotate` は色相だけで質感が崩れるので非推奨

### B. フロントエンド

- **Next.js (React) + Zustand**（状態管理）+ **Konva.js または Fabric.js**（canvas編集ライブラリ。CreateJSの後継として情報量◎、TypeScript対応）
- 旧XMLレイアウトは JSON Schema 化、shapeObjectのコンパクトパスは **SVGパスに変換** してリポジトリに置き直す（diff/レビュー可能化）
- スウォッチUIはCSSスプライトをやめ、`<picture>` + `srcset` + 高速CDN（Cloudflare Images / imgix の variant 機能）に寄せる

### C. バックエンド

- 印刷は **Puppeteer / Playwright のサーバ側スクリーンショット** か、もしくは正規SVGをそのまま PDF 化（Resvg, PDFKit）。PHPの再実装より移行コスト低
- カタログメタは Postgres + pgvector / SQLite + Algolia 等で検索可能に

### D. 最終形のシンプル版

- 最初は「製品=画像URL、軸=ドロップダウン、合成=Konva」でMVP → 任意色対応はマスク方式で後付け
- 文字エンコは UTF-8 一択

## 6. 次のステップ

1. **要件をマトリクスで切る** — 軸（series/color/...）、ステート（on/over/off）、ページタイプ（表紙/自動/フリー）の3次元表を1ページに作る → そのままDBスキーマになる
2. **画像戦略を決める** — 全パターン事前レンダ vs マスク合成のどちらか or ハイブリッド。意思決定の根拠は「対応カラー総数」と「写実性要件」
3. **prototype** — Konva + Next.js で「base画像1枚＋マスク1枚＋色変更」だけの最小再現を作る

## 付録: ネットワーク構造の全体像

```
[Angular SPA bundle]
  runtime.<hash>.js  / polyfills.<hash>.js / scripts.<hash>.js / main.<hash>.js
  styles.<hash>.css  + jQuery 3.3.1 + Spectrum + jQuery UI

[設定JSON]
  /pboard/assets/setting/
    serverConfigLan.json   ← API/画像/印刷のエンドポイント
    template.json          ← 表紙・自動配置ページのカタログ定義
    shapeObject.json       ← CreateJSコンパクトパス図形ライブラリ
    property.json          ← 接続種別 (conn_type:"L")
    woodone_pictures.json  ← 空。ランタイムで API から取得？

[スプライト/タイル群]
  /pboard/assets/Sprite/fitting/sprites-{color,design,designK,fitting,
                                          height,hirakitype,maguchi,
                                          mirror,series,type}.css
  /pboard/assets/Sprite/color/sprites-color-tool.{css,png}
  /pboard/assets/image/<auto3|auto6|auto7|auto_youzou|...>.{jpg,xml}

[バックエンド (PHP)]
  /pboard/DataServ            ← 商品メタ・カラーデータ取得
  io.php                      ← 状態保存 (Flex由来)
  /printImage/                ← 高解像出力配布
  /woodone/api/printHistory   ← 印刷履歴
```
