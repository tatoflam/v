---
title: habi-bff — HABI BFF / インフラ層
category: 03_work
tags: [project:habi-bff, client:hlab, entity:habi, tech:typescript, tech:aws-lambda, tech:dynamodb, tech:openai, tech:openspec, tech:sqs, capability:async-chat-pipeline, capability:attunement-policy, capability:bff-guard, stage:active]
sources: [c2dd2c85-7cc6-45d2-8df6-ebd5f5358bc4, e6de9be8-7152-4213-b913-f501d258dafe, 6a2f552b-d79a-4c1e-93ca-5b6b3bc4a045, c5c0230b-b3e6-43ae-ba7f-ea585ad01a6e, c6b59a1d-11af-4eb4-8f38-5910c5644ab3]
updated: 2026-05-08
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

## 2026-05-02 — `add-async-chat-pipeline` をレトロアクティブに OpenSpec 化（session 6a2f552b）

既実装の async-chat-pipeline capability（API Gateway 29 秒制約を SQS + DynamoDB + worker でバイパスする非同期パターン）をレトロアクティブに OpenSpec 化。`auth(4req)` + `user-os-persistence(5req)` に並ぶ **3 本目のスペック**として `openspec/specs/async-chat-pipeline/` に正規化。

### 7 requirements

1. `POST /api/v1/async/chat` — 202 応答契約（`jobId` 即時返却）
2. Job record — UUID 生成 + DynamoDB 24h TTL
3. SQS-trigger worker — 状態遷移 (`pending` → `processing` → `completed` / `failed`)
4. DLQ redrive — 失敗時の Dead Letter Queue 処理
5. `GET /api/v1/async/chat/{jobId}` — status endpoint
6. `GET /api/v1/async/chat/{jobId}/result` — result endpoint
7. `ChatJobMessage` payload contract — SQS message schema

### 7 design decisions

1. SQS + DDB vs Step Functions（コスト・観測性で SQS+DDB 採用）
2. 24h TTL（再送せず期限切れを許容）
3. `BatchSize=1`（並列 invoke で 1 ジョブ = 1 worker、エラー隔離）
4. 入力フィルタ二重実行回避（worker 側でフィルタを通さない契約）
5. `userId` フォワーディング（API GW 認証 → SQS message → worker context に伝搬）
6. 結果整形（worker が `result` を JSON で書き戻し）
7. 観測性（CloudWatch Logs + DLQ alarm）

### 動機

後続の change（`add-attunement-policy` ほか 4 本）が「async-chat-pipeline は既知の capability」として依存できるよう、ベースを正規化しておきたかった。`/opsx:propose` で proposal / spec / design / tasks を一気生成 → tasks 全部 既実装チェック → `openspec validate --strict` 通過 → `/opsx:archive` で `openspec/specs/async-chat-pipeline/` に delta マージ。

### 2 commits push（`origin/main`）

- `7c62128` — `/opsx:propose add-async-chat-pipeline`（4 artifacts 起票）
- `47d47a5` — `/opsx:archive add-async-chat-pipeline`（specs に正規化）

### 並行進行中の change（touch せず未コミット）

- `add-attunement-policy`（21 tasks、§1+§2+§3.2 完了 = 11/24）
- `add-bff-guard`（29 tasks、未着手）
- `add-bff-policy-monitoring`（30 tasks、未着手）
- `add-quality-always-on`（26 tasks、未着手）
- `src/services/attunement/` ファイル群

### 横展開可能な学び

OpenSpec のレトロアクティブ起票フロー（既実装 → spec 化）は定型化できる。詳細は [[05_learn/openspec-retroactive-flow]] に切り出し。

## 2026-05-06 → 05-07 — M2 バッチ着手：attunement-policy + bff-guard を 1 セッションで連続 archive (session c5c0230b)

`/opsx:explore` で M2 バッチ 4 changes の依存解析 → user 確定の順序 (attunement → guard → monitoring → quality) のうち **2 本を 1 セッションで完走**。3 commits (`a73f672` / `c5a92ae` / `637fabe`) を `origin/main` push、unit 171/171 + integration 24/24 pass、ワーキングツリー clean。

### 適用順序の確定（依存解析）

```
add-attunement-policy ──provides: chosen_level / attunement.* ──┐
                                                                ▼
                                        add-bff-policy-monitoring ◀── provides: rewrite_count
                                                                ▲
                                        add-bff-guard ──────────┘

add-quality-always-on (独立・CI 層、Seed の expected_traits が attunement 段名に依存)
```

- attunement と guard は両者とも `src/services/habi-client.ts` Review BOX 配線を触るので **シリアル必須** (マージ衝突回避)
- monitoring を最後に置けば attunement の `chosen_level` + guard の `rewrite_count` が両方揃って集約しやすい
- quality は M2 の柱が立った後に CI ゲートとして被せるのが効率的

### `add-attunement-policy` archive (`c5a92ae`、17/24)

今セッションで +6 完了 (§3.3 PM Chat UI / §4.4 短期 workaround / §5.1 LocalStack e2e / §5.2 mock UI / §6.1 validate / §6.2 v2 plan 更新 / §6.3 archive)。

**deferred 7 件 (back-fill 条件付き)**：

- §3.1 StepTrace 拡張 → habi-os PR 待ち (§8.1〜§8.3 完了後)
- §7.1 dev デプロイ → ユーザー承認 + 別セッション
- §7.2 Seed30 + A/B → `add-quality-always-on` 完了後
- §8.1〜§8.3 habi-os 別リポ PR → habi-os 側で follow-up

**capability spec**: `openspec/specs/attunement-policy/` 新規 4 requirements。

### `add-bff-guard` archive (`637fabe`、27/29)

5 値 Verdict ステートマシン (PASS / BLOCK / REWRITE / DOWNGRADE / HOLD) を Review BOX 直後に挿入。**Guard は 1 ターン 1 回必ず走る** (PASS でも Verdict 記録)。

| 機能 | 実装 |
|---|---|
| **5 値 Verdict** | `GuardEvaluator.evaluate()` 純関数。draft + attunement output → Verdict |
| **max_rewrite 制御** | `MAX_REWRITE` env (既定 2) 超過で次の非 PASS Verdict は強制 HOLD コアサ。Drafting LLM 呼び出しを必ず止める |
| **HOLD は LLM ゼロ** | `pickHoldTemplate()` 純関数で Presence/Mirror 級テンプレを返す。失敗モードで失敗を重ねるリスクを断つ |
| **DOWNGRADE は attunement 1 段下げ** | `lowerByOne()` で `chosen_level` を 1 段下げ → `[INTERVENTION_LEVEL]` を再注入して Drafting 戻し |
| **BLOCK は 422 + reason** | `GuardBlockError` (`AppError` 継承) を throw、`error-handler` が reason を body に出す |
| **構造化 ViolationLog** | pino warn `{ type, count_in_session, attunement_level, action, rewrite_count, draft_excerpt? }`。本番は `excerpt` 省略 (PII) |
| **PM Chat UI** | Guard セクションに verdict バッジ + 4 項目、mock Pattern C で HOLD 視認可 |

**deferred 2 件**: §8.1 dev deploy (ユーザー承認待ち) / §8.2 Seed30 + A/B (quality-always-on 完了後 back-fill)。

### §5.2 で発覚した PM Chat ローカル開発の構造的ギャップ

§5.2 (PM Chat 3 ターン目視) を SAM Local で踏もうとして詰まり、本 change スコープ外の問題が露出。詳細は [[05_learn/habi-bff-pmchat-localdev-gap]]。要点:

- SAM Local の `env.json` に `AuthProxyFunction` エントリが無く、`HABI_IDENTITY_API_BASE` が container に渡らない → `/auth/login` が habi-identity に到達できない
- AWS dev URL でのログインも別軸の問題で不通 (habi-identity 側でパスワードリセット / DB 再作成 / `JWT_ACCESS_SECRET` ローテートのいずれか)
- 対処: §5.2 を A 案 (mock UI で `jump blocked` バッジ視認) で closed、実フロー検証は §7.1 dev deploy 後 back-fill。**B 案 (env.json 整備 + habi-identity ローカル起動) は別 change 案件**

### 学び

- **explore → apply の橋渡しは「順序確定 + change スコープ境界判定」まで explore でやる**: explore stance は実装しないが、依存解析と「どこまでが本 change / どこからが別 change」の判断は explore 内で済ませると apply がタスク潰しに集中できて滑らか
- **5 値 Verdict は 3 値 (PASS/REWRITE/HOLD) より細かい意味がある**: BLOCK / REWRITE / DOWNGRADE / HOLD はコスト・遅延・安全性で異なるプロファイル。3 値に圧縮すると意図がブレる
- **HOLD は LLM ゼロのテンプレ返却**: 失敗モードで LLM を再度呼ばないことで (1) 失敗の連鎖を断つ、(2) コストゼロ、(3) Presence/Mirror 級テンプレで "そばに居る" 振る舞いを崩さない。ガードレール設計の参考 pattern
- **deferred タスクは tasks.md に back-fill 条件を明記して archive**: archive 後も deferred 項目が追跡可能になる。spec の「実装完了」と change の「全タスク完了」が乖離しても OK

### 残 in-progress changes (依存順序通り)

```
[3] add-bff-policy-monitoring (0/30)  ← attunement.chosen_level + guard.rewrite_count を集約
[4] add-quality-always-on    (0/26)  ← Seed30 + A/B + 逸脱検知 CI ゲート
```

see also: [[02_diary/2026-05-07]], [[05_learn/habi-bff-pmchat-localdev-gap]]

## 2026-05-07 — Plan C 確定 + docs/plans 統廃合 + PM 依頼書刷新 + policy-monitoring を M3 へ繰り下げ (session c6b59a1d)

`/opsx:explore` で M1 マトリクス (`260216`) と現状実装の突合 → アクションプラン Plan C を採択 → ドキュメント整理と PM 依頼書刷新を 1 セッションで完走。**3 commits push (`a2f2883` / `33ace48` / `546794a` 全て `origin/main`)**、unit/integration テストノータッチ (docs のみ)。

### マトリクス突合の結論

| 層 | M | v1.0 要件 | 現状 |
|---|---|---|---|
| Habi Core / Engagement Boundary | M1 | ◎ | **◎** [habi-client.ts:321/669](src/services/habi-client.ts) で system prompt 注入 + BoundaryFlags 配線済 |
| User OS 保存・読込 | M2 | △ | **◎相当** DynamoDB + 楽観ロック as-built ([user-os-persistence/spec.md](openspec/specs/user-os-persistence/spec.md)) — v1.0 要件超過達成 |
| Attunement Policy | M2 | ◎ ルールベース | **◎** [selector.ts](src/services/attunement/selector.ts) + [rules.ts](src/services/attunement/rules.ts) |
| BFF Guard 5値Verdict | M2 | ◎ | **◎** [evaluator.ts](src/services/guard/evaluator.ts) + [state-machine.ts](src/services/guard/state-machine.ts) |
| 段ジャンプ制御 / 違反ログ | M2 | △ | **△** StepTrace + [violation-log.ts](src/services/guard/violation-log.ts) |
| **Narrative Memory** | M3 | △ | **× 未着手** (`grep narrative\|memory\|abstract.?log` 0 件) |
| **Context Builder (削減)** | M4 | △ | **× 未着手** |

**結論**: M3/M4 のみ未着手。M3/M4 OpenSpec 提案は v1.0 リリース計画確定後に持ち越し。

### Plan C — PM Seed 手数を最優先

```
[今] ┬─→ add-bff-policy-monitoring (★ M3 へ繰り下げに変更)
     │
     └─→ add-quality-always-on (CTO 足場 / PM Seed 30 本)
              ↓
          [v1.0 リリース計画確定]
              ↓
          add-narrative-memory (M3) / add-context-builder (M4) を起票
              ↓
          v1.0 リリース
```

### Fast/Deep ルーティングを v2.0 送り

マトリクス上 v1.0 では未要求のため Month 2.2 を v1.0 必須から外す。HABI_DEVELOPMENT.md 第1部に新節 **§1.9「ルーティング層 — v2.0 送り」**、第3部 Month 2.2 に callout、第6部 OpenSpec ロードマップに `add-processing-flow-fast-deep` (未起票) を追加。HABI_LOADMAP.md Phase 1 §5 を Phase 2 §7-bis へ移動。

### docs/plans/ ファイル統廃合 (4 → 3 + archive、commit `a2f2883`)

- HABI_DEVELOPMENT.md (v1, 1003 行) と HABI_DEVELOPMENT_v2.md (v2, 265 行) を **統合 1270 行** へマージ → 旧 v2 は `git mv archive/` (履歴保持)
- HABI_DEVELOPMENT_CHANGELOG.md / HABI_LOADMAP.md に [2026-05-07] エントリ + 進化マップ
- 統合後章構成: 第0部 (3 バージョン位置づけ) / 第1部 (層×Month×Vマトリクス 1.1〜1.9) / 第2部 (v2.0 で追加された 4 層解説) / 第3部 (M1-M12 月別) / 第4部 (テスト計画) / 第5部 (リスク管理) / 第6部 (OpenSpec ロードマップ) / 第7部 (関連)
- 7 files changed、+521/-122。active な change の参照リンクも更新済 (`add-bff-policy-monitoring/tasks.md`, `add-quality-always-on/tasks.md`, `docs/README.md`)

### PM 依頼書を §8/§9/§10 で刷新 (commit `33ace48`、+251/-4)

- `PM_REQUEST_MONTH2_USER_OS.md` に **§8 Attunement Policy 監修 / §9 BFF Guard 監修 / §10 Step Debug 検証 (外部仕様のみ)** を追加 (+358 行)
- 冒頭に「🆕 2026-05-07 1 週間期限の優先確認サマリ」表 → A〜D ブロック (推定 0.5〜1 日 each) で全体俯瞰
- 期限 **2026-05-14** (1 週間)
- 旧 `HABI_ARCH_STEP_DEBUG.md` は `git mv archive/` へ退避し外部仕様のみを §10 へ吸収
  - **割愛した内部仕様**: LLM Off 時の JSON 構造、`< 5ms` メトリクス、`[OFF]` バッジ色 → F4「Input/Output 表示は検証に十分か」で抽象化、ユニット/統合テスト範囲とした
- 完了条件チェックリスト: 従来 6 項目 + 新規 3 項目 (Attunement/Guard/Step Debug)
- テスト環境: `https://ww6knpkhu4.execute-api.ap-northeast-1.amazonaws.com/development/pm/chat` / `pm-test@example.com / TestPass123` (PM Chat Tool で A1〜E4 自動実行)
- フィードバック方法: **会話ログコピー** + **Google Document に転記済み → PM が赤字記入で連絡 → CTO がリポジトリへ反映** の併用 (PM はリポを直接編集しない)
- メール文面はドラフト作成したが「送信用なので残さない」(本文は user 手元から送信、リポには残さず)

### add-bff-policy-monitoring を M2 → M3 へ繰り下げ (commit `546794a`、3 files、+57/-7)

性格は「**M2 単発の Done ではなく、M2 以降毎回の継続観測**」。マトリクス上は v1.0 = △ (計測のみ) だが、Month 2 完了条件 (Done) には載っていなかった (CTO タスクには記載 / Done には未反映 → ドリフト)。

判断: **PM Seed 30 本オーサリングが M2 直後の最大手数**になるため、CTO は quality-always-on の足場作りに集中、policy-monitoring は M3 (`add-narrative-memory` と並行) で着手。pino ログに metrics 列を足すだけなので M3 の本命と並行可能。

反映:
- HABI_DEVELOPMENT.md §1.8 マトリクス行・§2.4 見出し: 「M2 以降毎回」→「M3 以降毎回」
- 第3部 Month 2 CTO タスクから Month 3 CTO タスクへ移設 (callout で「M3 へ繰り下げ」明記)
- 第6部 OpenSpec ロードマップ表の Month 列を更新
- proposal.md の Why に「PM Seed の手数を優先するため M3 へ繰り下げ」4 行追記、Roadmap alignment を Month 3 に修正
- HABI_DEVELOPMENT_CHANGELOG.md に [2026-05-07] 単独エントリ
- `openspec validate add-bff-policy-monitoring --strict` 通過、tasks.md は無修正

不要だったもの: PM 依頼書の追記 (PM 監修対象ではない CTO 内部観測)、Month 2 完了条件 (そもそも Done にゲートしていなかった)。

### 副産物の小ネタ

- **Excel ロックファイル `~$★★★…マトリクス.xlsx`** を git add 時にスキップする運用：Excel を開いている間だけ生成される一時ファイル、閉じれば消える。コミット対象から除外する
- **archive 内の不変原則**: CHANGELOG L219 の 2026-04-06 当時の v2 参照は **過去の事実** なので不変、書き換えない (改ざんしない)

### 残 (Plan C ベース)

```
[M2 残り]    PM 監修待ち (5/14) → HOLD 語感など feedback 反映
[M2 完了後]  add-quality-always-on 足場 (CTO 単独着手可)
[M3 着手]    add-narrative-memory (本命) + add-bff-policy-monitoring (並行)
```

see also: [[02_diary/2026-05-08]], [[06_output/2026-05]]
