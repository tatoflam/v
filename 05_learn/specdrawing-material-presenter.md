---
title: SpecDrawing material-presenter MVP（Woodone /pboard/ 自作版）
category: 05_learn
tags: [topic:specdrawing-material-presenter, tech:next-js, tech:konva, tech:typescript, tech:openspec, stage:active]
sources: [84a5b2d0-402c-4114-a408-4bf81236eeb0]
updated: 2026-04-25
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

## Links

- [[05_learn/woodone-pboard-architecture]] — 出発点となった Woodone /pboard/ の調査
- [[06_output/2026-04]] — GitHub repo 初 push の記録
- [[02_diary/2026-04-25]]
