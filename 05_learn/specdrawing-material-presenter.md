---
title: SpecDrawing material-presenter MVP（Woodone /pboard/ 自作版）
category: 05_learn
tags: [topic:specdrawing-material-presenter, tech:next-js, tech:konva, tech:typescript, tech:openspec, tech:vercel, stage:active]
sources: [84a5b2d0-402c-4114-a408-4bf81236eeb0, f16f3443-5ba1-4c74-9849-912a8b545d38, 06fe1d24-37d8-4e1f-806d-c8119ea2e8d2, 04e50b3d-6f4c-4645-88a7-39291c8b65b4]
updated: 2026-04-30
---

# SpecDrawing material-presenter MVP

## Summary

Woodone「ラクラクプレゼン」(`/pboard/`) のアーキテクチャ調査（[[05_learn/woodone-pboard-architecture]]）を踏まえ、**ベースパース画像 + マスク合成で任意色対応**する自作プレゼンボードの MVP を OpenSpec ワークフローで仕様化〜実装〜GitHub push まで一気通貫で構築。リポジトリ: <https://github.com/tatoflam/SpecDrawing> (`b9b297b`、77 files / 12,387 行)。

## 採用スタック（design.md）

| レイヤ | 採用 | 不採用と理由 |
|---|---|---|
| フレームワーク | **Next.js 14 App Router + TypeScript** | CRA（メンテ停止）、Vite 単体（SSR 不要だが将来 BFF 接続を想定） |
| Canvas | **Konva**（Stage / Layer / Group） | EaselJS（Flash 出自で重い）、生 Canvas API（ヒットテスト等を自前実装したくない） |
| 状態管理 | **Zustand** | Redux（boilerplate 過多）、React Context（再レンダ問題） |
| スタイリング | **Tailwind** | CSS Modules、styled-components |
| バリデーション | **Zod** | カタログ JSON 取り込み時のスキーマ検証必須 |
| ビルド/パッケージ | **npm**（pnpm 不在） | tasks.md 記載の `pnpm` は `npm run` に読み替え |
| 画像生成（seed） | **sharp** devDep | ImageMagick 不在のため |

## Single-tier アーキテクチャ判断（D10）

MVP では **Frontend / Backend を分けない**。`backend/` フォルダがないのは意図的、未着手 TODO ではない。

- 分けないもの: API サーバ / DB / 認証サービス / 別デプロイ単位
- 安全な根拠: 永続化なし・カタログ静的・エクスポートはクライアントサイド
- Server / Client Component は Next.js 内部の話で「分離」ではない
- **将来分離するトリガ**:
  1. 永続化要件（保存・履歴・共有）
  2. 高解像度 PDF 出力（サーバ側レンダ必要）
  3. 本番カタログ取り込み
  4. 認証 / マルチテナント
- 最初に固まる契約: D5 の **Zod カタログスキーマ** — 分離した時点でこれが API 契約になる

代替案（最初から分離 / Route Handlers BFF / `next export` 完全静的）は却下し design.md に却下理由を残した。

## 実装で見つかった spec の誤りと修正

OpenSpec で書いた `specs/color-composition/spec.md` に **2 件の合成順誤り**を実装中に発見、spec ＋ tasks ＋ コードを同時更新して `openspec validate` を pass させた。

### 誤り 1: `source-in` は色を消す

- **元 spec**: 色 → マスク (`source-in`) → シェーディング
- **問題**: `source-in` は「ソースをデスティネーションの形でクリップ」だが、ソースをマスクの**色で置き換える**動作になり、色が失われる
- **修正**: `destination-in` に変更（デスティネーション = 既に描いた色を、マスクの alpha > 0 領域で残す）

### 誤り 2: マスクは最後にかける

- **元 spec**: シェーディング → 色 (`multiply`) → マスク
- **問題**: `multiply` 後にマスクをかけても、複数 part を 1 Layer で合成する場合、後続 part の `multiply` が前 part の masked 領域に灰色を漏らす（floor が灰色になる退行を観測）
- **修正**: **マスクを最終ステップに**移動。順序を `シェーディング → 色 (multiply) → マスク (destination-in)` に固定

### 誤り 3: 1 part = 1 Konva Layer

- **元実装**: 全 part を 1 Layer に Group として並べる
- **問題**: 後続 part のフルシーン shading 描画が前 part の masked 領域を上書き（壁の青を床の override が消す）
- **修正**: **part ごとに専用 Konva Layer**。各 part の合成チェーンが独立した canvas に閉じる

## Catalog 設計（material-catalog spec）

- 多軸属性（known axes ＋ unknown axes）
- 既知軸: シリーズ / デザイン / カラー / 間口 / 高さ / 開き方 / ミラー / タイプ
- 未知軸: 「その他の軸」パネルでキー名ごとに動的グルーピング — Woodone カタログのように軸が無限に増えても UI 側で吸収できる
- Zod でロード時検証 → スキーマ違反は build / runtime の両方で fail-fast

## Procedural seed assets

`npm run seed:assets` で sharp によるリビングルーム base image ＋ material thumbnail を再生成。**バイナリをコミットせず、生成スクリプトをコミット**する方針（diff の追いやすさと再現性のため）。

## Quality gates（tasks.md §8）

- `npm run typecheck` ✅
- `npm run lint` ✅（warnings ゼロ）
- `npm run build` ✅（Next.js production build）
- Playwright smoke test ✅（壁の色変更 / 床の色変更 / window 領域は影響なし / PNG export ダウンロード確認）

## OpenSpec ワークフローの所感

- `/openspec-propose` で proposal / design / tasks / specs を一括生成 → `openspec validate` で構造保証
- `/opsx:apply` で tasks.md 上から実装、各 §単位で Playwright smoke
- 実装中に spec の誤りを発見したら **コードと spec を同時更新**（spec が真）
- `.claude/`、`.codex/`、`.cursor/` の OpenSpec scaffold（slash command / skill 定義）は**チーム共有用なのでコミット対象**、`node_modules/`、`.next/`、`.playwright-mcp/`、`smoke-*.png` は `.gitignore`

## MVP スコープ外（後続チェンジ送り）

- サーバーサイド PDF / 2840×2000 印刷
- テキスト / シェイプ / ライン / undo-redo / 整列 / 回転
- 認証・永続化
- CMS
- 本番カタログ取り込みパイプライン
- モバイル最適化

## 2026-04-27 — base-variant 仕上げと dev-trace sidecar drift 修正

`add-base-variant-finishes` change を実装〜archive まで完走。動機は **multiply 系の合成では再現できない仕上げの素材違い**（キッチン天板の大理石パターン、レンジフードの艶感、玄関床の素材違いなど）。

### Base-variant の設計

- ベースパース 1 枚を **`_natural` / `_sharp` / `_flat` の 3 バリアント**に分割（カラー軸の質感ごとの事前レンダ）
- `(part, option)` 単位の **マスク適用済みピクセル差し替え** — option ごとに「どのバリアントから切り出すか」を `scenes.json` の `variantOverrides` で指定
- `scripts/cut-base-variants.{ts,sh}` で各 part の bbox に従って 3 バリアントから切り出し → dedupe → `public/assets/base/main/finishes/<part>/<option>.png` に格納
- `FinishOption` schema に `customTextureUrl?: string` を追加せず、暗黙の variant override で対応（schema 拡張は次フェーズ）
- LFS 対象パターンを `*.png` 全部から `finishes/**/*.png` に追加で拡大

### enhance-dev-trace の bug fix

`/dev/trace` でポリゴン編集→保存しても、メイン画面では **更新前のポリゴン領域に色が載る** という drift バグ#3 を解消:

- 原因: マスク `.png` と `parts.json` の更新タイミングが乖離していた（`.bak` diff 比較では検知漏れあり）
- 解決:
  - **per-part FNV-1a hash sidecar**（`mask_NN.hash`）を `parts.json` 保存と同 atomic で更新
  - メイン画面の URL に `?_rev=<hash>` を付ける **per-part cache-bust**（lock-step）
  - `?force=true` 全マスク再生成ボタン（sidecar drift からの復旧手段）
- 副次的に Konva の `listening={false}` でクリック貫通、200px 固定幅 + `whitespace-nowrap` でヘッダ高さ固定（バグ#1, #2 もこの change で解消）

### ⑨ スポットライト polygon を 30 頂点に

`/dev/trace` で 4 頂点プレースホルダ矩形 → 30 頂点で天井トラック形状をトレース（bbox 414-2427 × 0-727、PR #5）。`mask_09.png` も sidecar 経由で自動 regen。

### 残課題（PR #8 で 2 提案を起票）

`improve-finish-fidelity`（5 項目）:
1. 複数ポリゴン領域のキャプチャ・反映（1 part = N polygon ring）
2. ポリゴン内の "穴"（even-odd ルール、窓サッシだけ除外など）
3. オプション別テクスチャ画像（`customTextureUrl` フィールド ＋ `seed:custom-textures` パイプライン、`seed:parts` 保護）
4. 生成 AI inpainting spike（SD/ControlNet で 5 サンプル生成→go/no-go）
5. 背景画像の色補正（顧客側 re-render を先に依頼、代替で sharp `.modulate()` 1 行）

`add-vercel-deployment`:
- **GitHub Pages 不採用** — LFS pointer がそのまま返る（gh-pages ブランチに実体コピーする workflow を組まないと致命的）、Route Handler の `output: 'export'` 不可、`/dev/trace` を本番から除外する手間
- **Vercel 採用** — API routes そのまま動く / `<Image>` 最適化動く / LFS auto-resolve / sub-path 不要 / preview deployments が PR ごとに URL を発行
- 用途: デザイナーが `/dev/trace` を含めて触る環境を URL で共有

### 工数振り返り（人時間ベース、senior 1 名 単独想定）

完了済 ~166 h:
| Phase | 内訳 | 時間 |
|---|---|---:|
| MVP | Next.js 14 + Konva + Zustand 一式 + OpenSpec 初期化 | 30 h |
| Redesign（numbered-part finish picker） | scenes/parts/finishes loader + xlsx→JSON + numbered overlay | 54 h |
| Designer follow-ups | 実 shading 抽出 / mask anti-alias / `/dev/trace` 初版 | 25 h |
| enhance-dev-trace | sidecar regen / cache-bust / undo-redo / バグ#1-3 修正 | 32 h |
| ⑨ pol 手調整 | 30 頂点トレース | 1 h |
| add-base-variant-finishes | spec / cut script / FinishOption 描画 / LFS 拡張 | 19 h |
| archive 系 | live spec 取り込み × 5 件 | 5 h |

フェーズ② 残: `improve-finish-fidelity` 56–80 h（multi-ring 30h / per-option custom 6h / AI spike 16h / impl 16-24h / bg fix 4h） + Vercel 4–8 h。

**AI assist 効率**: 単独 11.5 h セッションで人月相当の進捗（コード＋仕様＋アーカイブ管理）。

## 2026-04-29 — multi-ring polygons (`add-multiring-polygons` Phase A/B/C)

`improve-finish-fidelity` Item-1（複数ポリゴン領域 + 穴）を `/opsx:apply add-multiring-polygons` で実装。28/32 タスク完了、`proposal-memos-fidelity-and-vercel` ブランチに 4 commit を push（`bbcdf4c` / `a711b38` / `22468c7` / `b26cb83`）。

### Schema 進化（v0 → v1 → v2）

| 世代 | 形 | 用途 |
|---|---|---|
| v0 | `polygon: Vertex[]` | 初期 MVP（単一 ring、穴なし） |
| v1 | `polygon: Vertex[]` ＋ optional `polygons: { outer }[]` | 過渡期（loader が両方読める） |
| v2 | `polygons: { outer: Vertex[], holes?: Vertex[][] }[]` | 完成形。`outer` ＋ optional `holes`、part あたり N polygon |

loader は **3 世代後方互換**で読み込み、書き戻しは v2 に正規化。`firstOuter` / `withFirstOuter` / `appendOuter` / `appendHole` を `lib/parts/polygonOps.ts` に集約して呼び出し側はスキーマ世代を意識しない。

### Crash バグ — legacy parts.json の `firstOuter` undefined

Phase A 単体 commit 後に `/dev/trace` を開くと `Cannot read properties of undefined (reading '0') @ firstOuter`。原因は **古い v0 parts.json が API/draftStore 内部で v2 形に正規化されていなかった**こと。

修正は **API + draft 境界で正規化**:
- `app/api/dev/parts/route.ts` で読み込み直後に v2 へ
- `lib/dev/draftStore.ts` で保存前 / hydrate 後に v2 へ
- 結果、UI コードは「常に v2 が来る」前提でよくなり `polygons[0]?.outer ?? []` のような defensive な書き方が不要に

### Even-odd マスク rasterizer & hit-test

複数 outer + holes を 1 part 内で扱うため、マスク描画と hit-test を **even-odd ルール**で書き換え:
- 描画は outer fill → hole で xor で抜く（`Path2D` の `evenodd` モード）
- hit-test は ray casting + holes も同じカウントに参加

`scripts/verify-mask-parity.mjs --capture / --check` で **既存 17 parts が SHA-256 byte-identical** を保証（migration が描画を変えていないことの数値ガード）。

### Phase B — `/dev/trace` UI

- **`ActiveRing` 状態**（outer / hole）と `holeBuildMode` フラグを導入。`editingId` 切替で自動リセット（part を切り替えると hole 編集モードが残らない）
- ボタン 3 つ：「ポリゴンを追加」「穴を追加」「穴を完了 (Esc)」 ＋ キーボード Esc
- 各 vertex `<Circle>` がどの ring に属すか視覚的に分離（outer / hole の頂点を別色で表示）
- mutation handler はすべて `ActiveRing` を target に取る → outer / hole の編集 API が統一

### Phase C — マスク再生成 + デザイナー実編集

- migration script `scripts/migrate-parts-multiring.mjs` を `parts.json` に適用、`npm run seed:masks` でマスク `.png` を全部再生成
- 続けてデザイナー（=セッションオーナー本人）が `/dev/trace` 上で **10 部材に sub-polygon ＋ 穴を実編集**。`parts.json` ＋ `public/assets/base/main/masks/*.png` を 1 commit にまとめて push（`b26cb83`）

### 残 4 タスク（次セッション送り）

1. multi-ring 専用 Playwright smoke（穴領域は色が載らないことの screenshot diff）
2. `firstOuter` 等の **段階的廃止**（呼び出し側を `polygons.flatMap(p => p.outer)` 形に置換）
3. `add-multiring-polygons` の archive（`/opsx:archive` で live spec 取り込み）
4. README / AUTHORING.md の v2 schema 記述更新

### 学び

- **境界で正規化**するパターンは、schema migration の最終クッションとして強力。UI コードを defensive に書かなくて済むので可読性が大きく回復した
- mask byte-parity の数値ガードは「描画ロジックを書き換えても出力が変わっていないこと」を確実にする。spec 変更を伴わない refactor との切り分けに必須

## 2026-04-28 — OVERVIEW_JA.md（全体仕様 + 提案サマリ + 工数 + 運用コスト）

`openspec/OVERVIEW_JA.md` を新規作成し、capability 8 本の現行仕様、進行中の 2 提案サマリ、完了済み 166 h と残工数の総合表、社内向け運用コスト試算を 1 ドキュメントに統合（§1–§5 現行仕様 / §6 提案サマリ / §7 工数 / §8 運用コスト）。

### §8 運用コスト試算の要点

社内設計者・PM・営業利用、画像 Export 1 日 100 件想定:

- **PNG Export はクライアント生成**でサーバ帯域消費なし。サーバ負荷はアセット配信のみ。
- 月間トラフィック想定: 1,500–3,000 セッション × 平均 8 MB = **12–24 GB/月**（Vercel Hobby 100 GB の 1/4 以下、Pro 1 TB の 2 % 程度）。
- **推奨構成: Vercel Pro $20 + LFS 無料枠 → 月 ¥3,000–4,000、年 ¥38,000–49,000**。
- 1 export あたり **約 ¥1.1**。1 日 1,000 件まで増えても構成変更不要。
- コスト増要因: ① Vercel team seat 追加、② 監視ツール（Sentry/Datadog 等）、③ 複数シーン並列展開、④ 社外認証（SSO・Okta）。

## 2026-04-30 — urban-sea variant switcher + 部材リスト.xlsx 列構造リライト

`add-urban-sea-variants-and-parts-export` ＋ `rewrite-seed-for-variant-keyed-workbook` の 2 提案を立ち上げて MVP の **runtime 多様性軸**を 1 つ加えた。アーバンシー sheet で Natural / Flat / Sharp の base-variant を runtime に切り替えられるようにし、texture-mode part が variant 切替に追従するパイプラインに揃えた。コミット 9 本（`2fc870b` → `6c9fcac`）、`proposal-memos-fidelity-and-vercel` ブランチ、まだ origin 未 push（ahead 9）。

### スキーマ追加（ランタイム側）

- **`scenes.json` / `scene.json`**: `variants: { key, label, baseImageUrl }[]` と `variantsEnabled: boolean` を追加。`variantsEnabled === true` の sheet だけ UI に variant switcher が出る
- **`finish-options.json`**: texture-mode option に `textureUrlByVariant: Record<VariantKey, string>` と `iconUrl: string`。Excel export がカラム埋め込み画像として `iconUrl` を使う
- **`parts.json`**（アーバンシー scene）: 非アクセントクロス part を全部 `renderMode: "texture"` に書き換え（**designer-side breaking**）。アクセントクロス（キッチン accent / 収納 accent）だけ `color` mode のまま残し、ユーザの色選択を尊重

### スキーマ追加（seed 側）

- **`finishOptionSchema`** に `defaultForVariants: z.array(z.string()).default([])`
  - **空配列 = "alternative"**（ユーザが手で選ぶ option）
  - **non-empty 配列 = "per-variant default"**（その variant では何も選んでいない時に自動表示される option）
  - 旧来の `isDefault` boolean を多次元化せずに **1 つの enum 配列に圧縮**した（あえてフラグを増やさない判断）
- ランタイム側は variant 切替時に「現在の選択 option がその variant で texture を持つなら維持、持たない / 未選択なら variant default にフォールバック」のルールで動く

### 部材リスト.xlsx 列構造リライト

顧客が `部材リスト_20260430.xlsx` を新 layout で再支給。旧 layout は「D 列以降が flat な option 列」だったが、新 layout は **D / E / F = Natural / Flat / Sharp の per-variant default**、**G+ = alternative options**。`scripts/extract-finish-options.mjs` を全面書き換え:

- ヘッダー行を読んで `Natural` / `Flat` / `Sharp` を**列名で動的に発見**（D/E/F 固定の前提を撤廃）。デザイナが将来列順を変えても seed が壊れない
- 同じ part header 行の variant 列で「白/白/黒」のような重複ラベルが出ても、**1 option per distinct label に collapse**して `defaultForVariants` を埋める。3 option / 2 重複だった旧出力（`missing-swatch` 198 件発生）が消える
- 製品コードは header 行**直下の sub-row（row + 1）**から、サブラベル（②照明の「電球色」「光無し」等）も同サブ行から取得
- 画像 anchor は `xl/drawings/drawing*.xml` を読み、ラベルとは**異なる column × row の swatch cell** にマッチさせる（新 workbook はヘッダー直下の行に画像を置く）。`from`/`to` セル座標を辿る素朴な実装で安定マッチ
- `SPECDRAWING_WORKBOOK` env-var fallback（旧 archive を seed 入力に指定する逃げ道）を撤去、`部材リスト.xlsx` を canonical 名に戻して `old/` 配下に旧版を歴史保存

### Variant と option 選択の直交（`37b7ce4`）

Variant switcher と option 選択は**直交**にした:

- variant が切り替わったとき、選択中 option が新 variant で `textureUrlByVariant` を持てば **そのまま維持**
- 選択 option がその variant で texture を持たない or そもそも未選択の場合 → **variant default**（`defaultForVariants` に当該 variant key を含む option）に fall back

ユーザが Natural で手動選択した option を Sharp に切り替えただけで失わせない、という体験上重要なルール。

### Cache-bust と auto-derive と collapsed-label texture override

収束フェーズの 3 commit が一見小さいがどれも非自明:

- **`5836a21` cache-bust**: option panel と Excel export の `thumbnailUrl` / `iconUrl` に **mtime ベースの query string** を付けて、seed 再実行直後にブラウザキャッシュを貫通させる。「部材リスト.xlsx にタイトル / アイコンを追記したのに画面に反映されない」問題の真因がブラウザキャッシュだった
- **`5d1dcbb` auto-derive textureUrl**: option が **単一 variant の `defaultForVariants`** を持つ場合（つまり「該当 variant でしか登場しない collapsed-label option」）、`textureUrl` を該当 variant の swatch から自動派生する。デザイナが手で `textureUrl` を埋めなくても variant 切替時に正しい part 画像が表示される
- **`6c9fcac` collapsed-label texture-following**: part header 直下の "default" option 群（UI 上は label が collapse される）について、variant 切替に追従する texture を表示するよう描画パイプラインを修正。さらに⑮（床）を `renderMode: "color"` → `"texture"` に flip。`finish-base-overrides.json` は collapsed-label のケース専用 hook と README で明文化して定義を簡素化（現状は登録不要で空のまま温存）

### 学び

- **新しい状態軸（variant）を入れるときは、既存軸（option 選択）との直交ルールを最初から決めておく**。後付けで決めようとすると "切替で何が消える / 残るか" のメンタルモデルがブレる
- **enum + 配列で表現すれば boolean フラグの組み合わせ爆発を回避できる**（`defaultForVariants: VariantKey[]` のパターン）
- **mtime cache-bust は seed パイプラインのある SPA に必須**。アセット URL を `?v=<mtime>` で叩くだけで、seed 再生成 → 画面反映の経路がデバッグレスになる

## Links

- [[05_learn/woodone-pboard-architecture]] — 出発点となった Woodone /pboard/ の調査
- [[06_output/2026-04]] — GitHub repo 初 push & PR 履歴
- [[02_diary/2026-04-25]]
- [[02_diary/2026-04-27]]
- [[02_diary/2026-04-28]]
- [[02_diary/2026-04-29]]
- [[02_diary/2026-04-30]]
