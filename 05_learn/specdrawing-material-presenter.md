---
title: SpecDrawing material-presenter MVP（Woodone /pboard/ 自作版）
category: 05_learn
tags: [topic:specdrawing-material-presenter, tech:next-js, tech:konva, tech:typescript, tech:openspec, tech:vercel, stage:active]
sources: [84a5b2d0-402c-4114-a408-4bf81236eeb0, f16f3443-5ba1-4c74-9849-912a8b545d38]
updated: 2026-04-28
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

## Links

- [[05_learn/woodone-pboard-architecture]] — 出発点となった Woodone /pboard/ の調査
- [[06_output/2026-04]] — GitHub repo 初 push & PR 履歴
- [[02_diary/2026-04-25]]
- [[02_diary/2026-04-27]]
