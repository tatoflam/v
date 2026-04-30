---
title: habi-bff — HABI BFF / インフラ層
category: 03_work
tags: [project:habi-bff, client:hlab, entity:habi, tech:typescript, tech:aws-lambda, tech:dynamodb, tech:openai, tech:openspec, stage:active]
sources: [c2dd2c85-7cc6-45d2-8df6-ebd5f5358bc4, e6de9be8-7152-4213-b913-f501d258dafe]
updated: 2026-05-01
---

# habi-bff

## Summary

HABI エコシステムの **BFF / インフラ層**（AWS Lambda + API Gateway + DynamoDB + SQS + OpenAI）。
ビジネスロジックは BFF に置かず、人格 OS は外部 npm パッケージ
`@hlab-it-sys/habi-core`（人格 OS 本体）と `@hlab-it-sys/habi-os`（運用ロジック /
processing flow）に切り出し、`src/services/habi-client.ts` で DI 注入する。
**2027 年 1 月リリース**を目標（前倒し意識）。

リポ: `/Users/tato/repo/github/hlab-it-sys/habi-bff`（GitHub `hlab-it-sys/habi-bff`）。

## ロードマップと現状（2026-05-01）

### 一次ソース
- [docs/plans/HABI_DEVELOPMENT.md](https://github.com/hlab-it-sys/habi-bff/blob/main/docs/plans/HABI_DEVELOPMENT.md) — v1（月別タスク、テキスト中心）
- **[docs/plans/HABI_DEVELOPMENT_v2.md](https://github.com/hlab-it-sys/habi-bff/blob/main/docs/plans/HABI_DEVELOPMENT_v2.md)** — 2026-04-30 新規作成。Excel
  シート `260216` の **「7 つの層 × 3 バージョン × Month 配置」** マトリクスを v1 にマージ。バージョン軸（v1.0 / v2.0 / v3.0）と層別 × Month の達成度を整理
- `★★★（M1完了時）ハビバージョン別機能マトリクス260217.xlsx` — 顧客側オリジナル（リポに置きあり）

### マトリクスから判明した v1 未掲載の 4 層
| 層 | 役割 | OpenSpec 提案 |
|---|---|---|
| Attunement Policy（介入選択層） | Presence/Mirror/Probe/Structure/Hold の選択、上方ジャンプ禁止、`MOVE_DOWN_OR_HOLD` | [`add-attunement-policy`](https://github.com/hlab-it-sys/habi-bff/tree/main/openspec/changes/add-attunement-policy) — 21 tasks（実装中、§1+§2+§3.2 完了 = 11/24）|
| BFF Guard（逸脱停止層） | BLOCK / REWRITE / DOWNGRADE / HOLD、`max_rewrite`、HOLD テンプレ | [`add-bff-guard`](https://github.com/hlab-it-sys/habi-bff/tree/main/openspec/changes/add-bff-guard) — 29 tasks（未着手）|
| 品質層・在り方テスト（常時） | Seed30 本／A/B（Core on/off）／Founder 逸脱／Core 再チェック／条文番号差分 | [`add-quality-always-on`](https://github.com/hlab-it-sys/habi-bff/tree/main/openspec/changes/add-quality-always-on) — 26 tasks（未着手）|
| BFF Policy／コスト・遅延ガード | 構造化メトリクス計測（v1.0 は計測のみ、閾値監視は v2.0） | [`add-bff-policy-monitoring`](https://github.com/hlab-it-sys/habi-bff/tree/main/openspec/changes/add-bff-policy-monitoring) — 30 tasks（未着手）|

すべて 2026-04-30 に作成、`openspec validate --strict` 通過。
**適用順（依存解析から）**：`add-attunement-policy` →
`add-bff-guard` →
`add-bff-policy-monitoring` →
`add-quality-always-on`。M3 以降（Narrative Memory / Context Builder /
温度推定 / Silence Engine / 心モード / Persona）は HABI_DEVELOPMENT_v2.md §6
に **未起票** として一覧化、着手月で順次起票する方針。

## 認証アーキテクチャ

ユーザー登録・ログイン・トークン発行・リフレッシュ・ログアウトは
**`habi-identity`** に分離済み。habi-bff が持つのは:
- `JwtAuthorizerFunction`（API Gateway Lambda Token Authorizer）— `iss=habi`,
  `aud=habi-api`, `type=access` を検証。鍵は `habi-identity-secrets` の
  `JWT_ACCESS_SECRET` を共有
- `AuthProxyFunction` — `/auth/{signup,login,refresh,logout}` を
  `${HABI_IDENTITY_API_BASE}` へ HTTPS 透過プロキシ

## 主要パス（Lambda BFF 内）

| パス | 概要 |
|---|---|
| `src/handlers/{sync,async,auth,tools}/*` | API Gateway → Lambda エントリーポイント（`errorHandler` 必須、zod で `validateRequest`）|
| `src/services/habi-client.ts` | habi-core / habi-os DI コンポジションルート。Direction → Selector → Drafting → Quality を配線 |
| `src/services/attunement/{types,rules,selector}.ts` | 2026-04-30 新規。Attunement Policy 純関数群（`AttunementSelector.select` ルールベース v1.0）|
| `src/services/{dynamodb,sqs,openai,filter,search}/*` | 永続化・キュー・LLM・I/O フィルタ・検索（OpenSearch は **無効化中**）|
| `src/middleware/` | validation, error-handler |
| `src/config/{env.ts,aws-clients.ts}` | 環境一元管理。LocalStack 自動切替 |

## 重要な制約

- **API Gateway timeout = 29s** → 長時間処理は `/api/v1/async/chat` パターン（Job ID → status → result）
- **OpenAI GPT-5 系**：`max_tokens` ではなく `max_completion_tokens`、`temperature` 非対応（`src/services/openai/client.ts` で対応済み）
- **JWT_ACCESS_SECRET は habi-identity と必ず一致**（不一致は 401）
- **OpenSearch Serverless 無効化中** — `/api/v1/search` はデプロイ環境では未稼働
- **シークレットは Secrets Manager**（`OPENAI_API_KEY`, `JWT_ACCESS_SECRET = habi-identity-secrets` 共有）

## 直近のキー判断（2026-04-29 → 04-30 セッション c2dd2c85）

- **CLAUDE.md と README.md の棲み分け**：CLAUDE.md = AI 向け索引（規約・タブー・読むべき
  ソースのルーティング）、README.md = 人間向け取扱説明書。重複禁止、CLAUDE.md
  → README に向けて `> 詳細: README.md` で委譲、README → CLAUDE.md へは
  委譲しない（人間は CLAUDE.md を読まない前提）
- **Attunement Selector 配線方式の選択（Option C 短期 B / 中期 A）**：habi-os の
  `DraftingInput` には `interventionLevel` 専用フィールドが無いため、短期は
  habi-bff 単独で `[INTERVENTION_LEVEL] {level}` タグを `systemPrompt` に
  注入（既存の `[DIRECTION]` `[TONE]` `[STRUCTURE]` `[BOUNDARY CAUTION]` と同じ
  タグ書式）、中期で habi-os に typed field を追加する PR を切る
- **spec の "structured input" 解釈**：spec.md の Scenario「`intervention_level`
  as a structured input equal to the Selector's `chosen_level`」は、既存の
  Direction タグ書式に倣ったタグ化マーカーでも満たせる（自由文には溶けて
  おらず、structured input の定義として通る）と解釈
- **`AttunementSelector` v1.0 の選好（先勝ち）**：(1) `direction.boundaryFlags` あり →
  `mirror`／(2) `shouldAllowSilence` → `presence`／(3) `slower` または
  `minimal` → `mirror`／(4) `detailed` → `probe`／(5) default → `mirror`。その後
  `confidence === 'low'` で無条件 `MOVE_DOWN_OR_HOLD`、それ以外で上方
  ジャンプ検知時に clamp（`lowerByOne(proposed)`）
- **メトリクス露出**：`ExtendedChatResponse.metadata.attunement = { chosen_level,
  proposed_level, jump_blocked, reason }`、pino で
  `attunement.{chosen_level, proposed_level, jump_blocked}` を構造化フィールド
  として記録（`add-bff-policy-monitoring` がこのフィールドを読む前提）

## 残ブロッカー / 次の動き

- **`add-attunement-policy`**：§3.1（StepTrace に `attunementInjection` 追加）/ §3.3（同 Quality 側）/ §4.4（StepTrace の e2e）は habi-os 側で `StepTrace` 型を拡張する PR が必要（[openspec/changes/add-attunement-policy/tasks.md §8](https://github.com/hlab-it-sys/habi-bff/blob/main/openspec/changes/add-attunement-policy/tasks.md) に follow-up note 済み）
- 次の自然な動きは `/opsx:apply add-attunement-policy` の §5（LocalStack）— ただし上記 habi-os ブロッカー解消が先

## 関連

- 2026-04-30 のセッション全容: [[02_diary/2026-05-01]]（4-30 の作業を翌朝 ingest）
- 関連リポ: `hlab-it-sys/habi-core`（人格 OS）, `hlab-it-sys/habi-os`（運用ロジック）, `hlab-it-sys/habi-identity`（認証分離先）
