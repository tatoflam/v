---
title: OpenSpec レトロアクティブ起票フロー（既実装 → spec 化）
category: 05_learn
tags: [topic:openspec-retroactive-flow, tech:openspec, pattern:retroactive-spec, workflow:propose-archive, stage:done]
sources: [6a2f552b-d79a-4c1e-93ca-5b6b3bc4a045]
updated: 2026-05-02
---

# OpenSpec レトロアクティブ起票フロー

## Summary

既に実装済みの capability を OpenSpec の正規 spec として後付けで起票する手順。`add-async-chat-pipeline`（[[03_work/habi-bff]]）で確立した定型。後続 change が「この capability は既知」として依存できるようになる。

## 5 ステップ

### 1. `/opsx:propose` で 4 artifacts 一気生成

```bash
/opsx:propose add-async-chat-pipeline
```

`openspec/changes/add-<name>/` 配下に proposal / spec / design / tasks の 4 artifacts が生成される。

### 2. tasks.md は既実装のためチェック済にする

レトロアクティブの場合、tasks.md の項目は **既にコードに存在する**ので一括チェック。残るのは `validate` と `archive` のみ。

### 3. `openspec validate <change> --strict` で構造保証

```bash
openspec validate add-async-chat-pipeline --strict
```

スキーマ違反（必須セクション欠落、リンク切れ、フィールド型エラー）を検出。`--strict` で warning も failure に。

### 4. `/opsx:archive <change> --yes` で specs に正規化

```bash
/opsx:archive add-async-chat-pipeline --yes
```

`openspec/changes/add-<name>/` の delta を `openspec/specs/<capability>/` にマージ、change を `openspec/changes/archive/<date>-<change>/` に移動。

### 5. archive 時に auto-generated TBD-Purpose を実コンテキストで埋める

archive 直後の spec.md には `TBD-Purpose` プレースホルダが残ることがある。**手動で**:

- 依存 capability への参照
- ロードマップ link（`docs/plans/HABI_DEVELOPMENT_v2.md` 等）
- source handler / repo / queue / SAM resource ポインタ

を埋めてから commit するとレビュー時の文脈が圧倒的に明瞭になる。

## 適用例: `add-async-chat-pipeline`

- 7 requirements: `POST /api/v1/async/chat` 202 応答 / Job record (UUID + 24h TTL) / SQS-trigger worker 状態遷移 / DLQ redrive / status / result endpoint / `ChatJobMessage` payload contract
- 7 design decisions: SQS+DDB vs Step Functions / 24h TTL / `BatchSize=1` / 入力フィルタ二重実行回避 / userId フォワーディング / 結果整形 / 観測性
- 2 commits push: `7c62128` propose + `47d47a5` archive

## 学び

- レトロアクティブ起票の最大の価値は **後続 change の依存解析が clean になる**こと。spec 化されていないと「この機能は前提として存在する」が暗黙になり、design.md の Trade-offs セクションが曖昧になる
- 既実装からの起票は spec の Scenario を「動いているコードからの逆引き」で書けるので、新規より精度が高い
- `validate --strict` を最初に通せば、後続 archive 時に予期せぬエラーで止まることがほぼない

## Links

- [[03_work/habi-bff]] — 適用先プロジェクト
- [[06_output/2026-05]] — 7c62128 / 47d47a5 commit
- [[02_diary/2026-05-02]]
