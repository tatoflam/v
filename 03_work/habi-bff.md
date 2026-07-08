---
title: habi-bff — HABI BFF / インフラ層
category: 03_work
tags: [project:habi-bff, client:hlab, entity:habi, tech:typescript, tech:aws-lambda, tech:dynamodb, tech:openai, tech:openspec, tech:sqs, tech:cloudformation, tech:sam, capability:async-chat-pipeline, capability:attunement-policy, capability:bff-guard, capability:quality-always-on, capability:comparison-mode, capability:narrative-memory, milestone:pm-inquiry-260508, milestone:add-quality-always-on-m1-m2, milestone:pm-260613-integration, milestone:founder-master-260618, milestone:dev-deploy-260703, stage:active, topic:aws-profile-account-mismatch, topic:step-debug-ab-comparison]
sources: [c2dd2c85-7cc6-45d2-8df6-ebd5f5358bc4, e6de9be8-7152-4213-b913-f501d258dafe, 6a2f552b-d79a-4c1e-93ca-5b6b3bc4a045, c5c0230b-b3e6-43ae-ba7f-ea585ad01a6e, c6b59a1d-11af-4eb4-8f38-5910c5644ab3, 8694d4d3-0a31-40a3-8cf9-f711376af20b, a1f12954-3832-48ce-8f5c-92c23f413365, 5b553af9-8076-45d0-8a8c-05e809a7fdc0, 1889f8ec-b67c-482b-a0aa-3301f546e04c, 6d328a3b-7b3e-44e1-bfd7-29bc66f889a7]
updated: 2026-07-04
---

# habi-bff

## Summary

HABI エコシステムの **BFF / インフラ層**（AWS Lambda + API Gateway + DynamoDB + SQS + OpenAI）。
ビジネスロジックは BFF に置かず、人格 OS は外部 npm パッケージ `@hlab-it-sys/habi-core`（人格 OS 本体）と `@hlab-it-sys/habi-os`（運用ロジック / processing flow）に切り出し、`src/services/habi-client.ts` で DI 注入する。
リリース目標は当初 **2027 年 1 月**（前倒し意識）→ 2026-06 に **2026-09 中旬** へ前倒し確定。
リポ: `/Users/tato/repo/github/hlab-it-sys/habi-bff`（GitHub `hlab-it-sys/habi-bff`）。関連リポ: `hlab-it-sys/habi-core`（人格 OS）, `hlab-it-sys/habi-os`（運用ロジック）, `hlab-it-sys/habi-identity`（認証分離先）。

## 現在の状態

（2026-07-03 時点）

- **dev デプロイ実機成功**: スタック `habi-bff-dev`（アカウント `062759670692` / ap-northeast-1、CloudFormation `UPDATE_COMPLETE`）。API `https://ww6knpkhu4.execute-api.ap-northeast-1.amazonaws.com/development/`、PM Chat Tool `https://ww6knpkhu4.execute-api.ap-northeast-1.amazonaws.com/development/pm/chat`。`NarrativeMemoryTable`（DynamoDB）が初めて実環境に載り、**Founder が Web 実機で「器」（単発差・構造差）を観測できる状態 = PM 側 Lv1 到達**（Founder 確認① 可）。
- **canonical マスター**: `docs/plans/UPDATED_MASTER_TEXT_JUNE2026`（Founder 260618 パック、13 文書 + Seed core/tuning）。Status: **Draft / Gate 1 未ロック**、Holdout (11) は非公開・repo 非搭載。
- **待ち**: 先方 AI からの Gate 1（Policy/Enum/Schema Lock）・Seed 確定。並行して CTO 側は **Step 5（Prompt Contract/Compiler 実装）** または **6.4（Founder Annotation + Seed 出力 = 調律の入口）** を進行可能。
- **未完タスク**: 5.3（async の trace_id/versionSet 永続、SQS payload / job record / result endpoint）、6.2（記憶経路表示 = Summarize / Memory Candidate / Core Validation）、7.3（LocalStack E2E 目視）。
- **OpenSpec specs（正規化済み capability）**: `auth`（4req）/ `user-os-persistence`（5req、DynamoDB + 楽観ロック as-built で v1.0 要件超過達成: [user-os-persistence/spec.md](openspec/specs/user-os-persistence/spec.md)）/ `async-chat-pipeline`（7req）/ `attunement-policy`（4req）/ `bff-guard`。
- **in-flight changes**: `add-narrative-memory` **41/61**（archive 保留、理由は決定事項参照）/ `add-quality-always-on` **20/26**（PM Seed 30 本待ち）/ `add-bff-policy-monitoring` **0/30**（M3 繰り下げ）/ 2026-06 派生 6 本: `adopt-founder-master-canonical`（他 in-flight change の portfolio 統合方針を内包）・`adopt-habi-v1-canonical-baseline`・`add-founder-approval-gates`（Founder Approval Gate 0–9）・`add-core-validation-memory-gate`・`add-prompt-contract-compiler`・`add-seed-quality-runner`（Founder Seed 25 本 = Core 9 + Tuning 12 + Holdout 4 前提で quality-always-on の runner を置換する設計）。M3 以降の未起票（Context Builder / 温度推定 / Silence Engine / 心モード / Persona、`add-processing-flow-fast-deep`）は HABI_DEVELOPMENT の OpenSpec ロードマップ節（旧 v2 §6 / 統合後 第6部）に一覧。
- **PM 側の積み残し**（2026-06-12 に初可視化）: Month 2 PM 監修 §1〜§10 = 10 項目未確認（期限 2026-05-14 から当時 29 日超過、合計工数 2〜4 日見積）/ M3 PM 設計タスク 7 項目未着手（意味粒度 / `memory_update_candidate` 6 サブタイプ / `relation_note` / `mid_summary` — Narrative Memory の意味設計の柱、CTO 側だけでは決められない）/ Quality Seed **0/30**。Inquiry_20260508 思想前提共有は完了（CTO 回答済み、CLAUDE.md 固定化済み）。
- **主要リスク**: R1 ★★★★★ habi-os の Deep Summarize 分離出力 PR が出るまで Narrative Memory はインフラのまま / R2 ★★★★★ PM Seed 30 本オーサリングが v1.0 リリースの単一クリティカルパス / R3 ★★★★☆ M3→M12 を短期間で押し切る耐性（R1 が滑ると M4 ごと連鎖遅延）/ P1〜P4（PM 監修オーバーラン / 意味粒度停滞 / Seed オーサリング / Step Debug 体感確認滞留）。
- **提言**（2026-06-12 時点、優先順）: (1) habi-os に Deep Summarize 分離出力 PR を最優先起票 (2) `tests/quality/seeds/SEEDING_GUIDE.md` を先出しして PM の Seed オーサリング並行開始 (3) BFF Policy Monitoring はインフラだけ先着地（`MetricsBuilder` + `turn.completed` ログ）(4) PM 集中監修日の確保 + 意味粒度ワークショップ + Seed オーサリングのガイド化。

### アーキテクチャ

認証（ユーザー登録・ログイン・トークン発行・リフレッシュ・ログアウト）は **`habi-identity`** に分離済み。habi-bff が持つのは:
- `JwtAuthorizerFunction`（API Gateway Lambda Token Authorizer）— `iss=habi`, `aud=habi-api`, `type=access` を検証。鍵は `habi-identity-secrets` の `JWT_ACCESS_SECRET` を共有
- `AuthProxyFunction` — `/auth/{signup,login,refresh,logout}` を `${HABI_IDENTITY_API_BASE}` へ HTTPS 透過プロキシ

主要パス（Lambda BFF 内）:

| パス | 概要 |
|---|---|
| `src/handlers/{sync,async,auth,tools}/*` | API Gateway → Lambda エントリーポイント（`errorHandler` 必須、zod で `validateRequest`）|
| `src/services/habi-client.ts` | habi-core / habi-os DI コンポジションルート。Direction → Selector → Drafting → Quality を配線。[habi-client.ts:321/669](src/services/habi-client.ts) で system prompt 注入 + BoundaryFlags 配線 |
| `src/services/attunement/{types,rules,selector}.ts` | Attunement Policy 純関数群（[`AttunementSelector.select`](src/services/attunement/selector.ts) ルールベース v1.0 + [rules.ts](src/services/attunement/rules.ts)）|
| `src/services/guard/{evaluator,state-machine,violation-log}.ts` | BFF Guard 5 値 Verdict（[evaluator.ts](src/services/guard/evaluator.ts) / [state-machine.ts](src/services/guard/state-machine.ts) / [violation-log.ts](src/services/guard/violation-log.ts)）|
| `src/services/comparison-mode.ts` | canonical `ComparisonMode` を skipHabiCore / processingFlow / 各 Step LLM に写像 |
| `src/services/{dynamodb,sqs,openai,filter,search}/*` | 永続化・キュー・LLM・I/O フィルタ・検索（OpenSearch は **無効化中**）|
| `src/middleware/` | validation, error-handler |
| `src/config/{env.ts,aws-clients.ts}` | 環境一元管理。LocalStack 自動切替 |

### 重要な制約

- **API Gateway timeout = 29s** → 長時間処理は `/api/v1/async/chat` パターン（Job ID → status → result）
- **OpenAI GPT-5 系**：`max_tokens` ではなく `max_completion_tokens`、`temperature` 非対応（`src/services/openai/client.ts` で対応済み）
- **JWT_ACCESS_SECRET は habi-identity と必ず一致**（不一致は 401）
- **OpenSearch Serverless 無効化中** — `/api/v1/search` はデプロイ環境では未稼働
- **シークレットは Secrets Manager**（`OPENAI_API_KEY`, `JWT_ACCESS_SECRET = habi-identity-secrets` 共有）

### 一次ソース（計画ドキュメント）

- [docs/plans/HABI_DEVELOPMENT.md](https://github.com/hlab-it-sys/habi-bff/blob/main/docs/plans/HABI_DEVELOPMENT.md) — v1（月別タスク、テキスト中心）→ 2026-05-07 に v2 と統合（1270 行）→ 2026-06 にステップ制へリファクタ
- [docs/plans/HABI_DEVELOPMENT_v2.md](https://github.com/hlab-it-sys/habi-bff/blob/main/docs/plans/HABI_DEVELOPMENT_v2.md) — 2026-04-30 新規作成。Excel シート `260216` の **「7 つの層 × 3 バージョン × Month 配置」** マトリクスを v1 にマージ（バージョン軸 v1.0 / v2.0 / v3.0 × 層別 × Month）。2026-05-07 に v1 へ統合し `git mv archive/`（履歴保持）
- `★★★（M1完了時）ハビバージョン別機能マトリクス260217.xlsx` — 顧客側オリジナル（リポに置きあり）
- `docs/plans` 配下は git 除外・機微・ローカルのみ（今後の commit から外す方針、開発時共有リポからは将来的に除外）

## 決定事項

- 2026-04-30: **CLAUDE.md と README.md の棲み分け** — CLAUDE.md = AI 向け索引（規約・タブー・ソースのルーティング）、README.md = 人間向け取扱説明書。重複禁止、委譲は CLAUDE.md →`> 詳細: README.md` の一方向のみ — 人間は CLAUDE.md を読まない前提
- 2026-04-30: **v1 未掲載 4 層を OpenSpec 4 change として起票** — Attunement Policy（介入選択層: Presence/Mirror/Probe/Structure/Hold、上方ジャンプ禁止、`MOVE_DOWN_OR_HOLD`）/ BFF Guard（逸脱停止層）/ 品質層・在り方テスト常時 / BFF Policy・コスト遅延ガード（v1.0 は計測のみ、閾値監視は v2.0）— Excel マトリクス突合で判明、全て `openspec validate --strict` 通過
- 2026-04-30: **Attunement Selector 配線は Option C（短期 B / 中期 A）** — habi-os `DraftingInput` に `interventionLevel` 専用フィールドが無いため、短期は habi-bff 単独で `[INTERVENTION_LEVEL] {level}` タグを `systemPrompt` へ注入（既存 `[DIRECTION]` `[TONE]` `[STRUCTURE]` `[BOUNDARY CAUTION]` と同書式）、中期で habi-os に typed field 追加 PR
- 2026-04-30: **spec の "structured input" 解釈** — 「`intervention_level` as a structured input equal to the Selector's `chosen_level`」は Direction タグ書式に倣ったタグ化マーカーで満たせる（自由文には溶けておらず定義として通る）
- 2026-04-30: **`AttunementSelector` v1.0 の選好（先勝ち）** — (1) `direction.boundaryFlags` あり → `mirror` (2) `shouldAllowSilence` → `presence` (3) `slower`/`minimal` → `mirror` (4) `detailed` → `probe` (5) default → `mirror`。その後 `confidence === 'low'` で無条件 `MOVE_DOWN_OR_HOLD`、それ以外は上方ジャンプ検知時に clamp（`lowerByOne(proposed)`）
- 2026-04-30: **メトリクス露出** — `ExtendedChatResponse.metadata.attunement = { chosen_level, proposed_level, jump_blocked, reason }` + pino で `attunement.{chosen_level, proposed_level, jump_blocked}` 構造化記録 — `add-bff-policy-monitoring` がこのフィールドを読む前提
- 2026-05-02: **async-chat-pipeline をレトロアクティブに OpenSpec 化** — 後続 change（`add-attunement-policy` ほか 4 本）が「既知の capability」として依存できるようベースを正規化
- 2026-05-02: **async 設計 7 決定** — SQS + DDB 採用（Step Functions 比でコスト・観測性）/ 24h TTL（再送せず期限切れ許容）/ `BatchSize=1`（1 ジョブ = 1 worker、エラー隔離）/ worker 側で入力フィルタを再実行しない / `userId` を API GW 認証 → SQS message → worker context にフォワード / worker が `result` を JSON で書き戻し / 観測性 = CloudWatch Logs + DLQ alarm
- 2026-05-07: **M2 適用順を attunement → guard → monitoring → quality で確定** — attunement と guard は両方 `habi-client.ts` Review BOX 配線を触るため**シリアル必須**（マージ衝突回避）、monitoring は `chosen_level` + `rewrite_count` が揃う最後、quality は柱が立った後の CI ゲート
- 2026-05-07: **Guard は 3 値でなく 5 値 Verdict（PASS/BLOCK/REWRITE/DOWNGRADE/HOLD）、1 ターン 1 回必ず実行（PASS でも Verdict 記録）** — 各 Verdict はコスト・遅延・安全性で異なるプロファイル、3 値圧縮は意図がブレる。**HOLD は LLM ゼロのテンプレ返却**（失敗連鎖を断つ・コストゼロ・Presence/Mirror 級で「そばに居る」を崩さない）
- 2026-05-07: **§5.2 PM Chat 目視は A 案（mock UI で `jump blocked` バッジ視認）で closed** — 実フロー検証は §7.1 dev deploy 後 back-fill、B 案（env.json 整備 + habi-identity ローカル起動）は別 change 案件
- 2026-05-07: **Plan C 採択 — PM Seed 30 本の手数を最優先**、`add-bff-policy-monitoring` は M2→M3 繰り下げ（性格は「M2 単発 Done でなく M2 以降毎回の継続観測」、Month 2 Done には未掲載のドリフトも確認。pino に metrics 列を足すだけで M3 本命 `add-narrative-memory` と並行可能）。M3/M4 の OpenSpec 提案は v1.0 リリース計画確定後に起票
- 2026-05-07: **Fast/Deep ルーティングは v2.0 送り** — マトリクス上 v1.0 未要求のため Month 2.2 を v1.0 必須から外す。HABI_DEVELOPMENT.md に §1.9「ルーティング層 — v2.0 送り」新設、`add-processing-flow-fast-deep`（未起票）をロードマップに登録、HABI_LOADMAP.md Phase 1 §5 → Phase 2 §7-bis へ移動
- 2026-05-07: **PM フィードバック方式** — 会話ログコピー + Google Document 転記 → PM が赤字記入 → CTO がリポジトリへ反映（PM はリポを直接編集しない）。送信用メール文面はリポに残さない（本文は user 手元から送信）
- 2026-05-07: **archive 内の過去記述は不変（改ざんしない）** — CHANGELOG L219 の 2026-04-06 当時の v2 参照は過去の事実として書き換えない。Excel ロックファイル `~$★★★…マトリクス.xlsx`（Excel を開いている間だけ生成）は commit 対象から除外
- 2026-05-09: **PM/外部読者向けドキュメントは「リポ参照ゼロ」を要件に書く** — コードリンク削除 + 設計上の固有名は本文展開 +「> 注:」短縮サマリ併記 + 用語前置きセクション。docx 入力 → Markdown インライン回答 → PM が再 docx 化のフローで章立てを保つ
- 2026-05-16: **PM Seed 待ちは「意味のある待機」（単独着手可 × ブロック前進可）に転換** — quality CI 配管を先行し、Word の DO NOT リストを `CLAUDE.md` + `openspec/project.md` に常駐化（AI エージェント共通則 = 多層防御の 1 層。CLAUDE.md + project.md + OpenSpec workflow + Quality Always-On のどれかに引っかかれば止まる）
- 2026-06-12: **`add-narrative-memory` は archive 見送り** — spec に未実装 2 requirement（(1) Pre-write Core compliance gate discards violating payloads = Section 5 wiring 必要 (2) Processing Flow wires Deep Summarize output to the repository = habi-os M2.2 Deep Summarize 分離出力 PR 待ち、現行 `SummarizeService.emotionalContext` がスペック違反になるため強引繋ぎ不可）が残存。両 requirement 着地まで保留。運用則候補「実装ファイル grep で requirement キーワード非ヒットなら archive 見送り」（`openspec validate` では検出不能）→ [[05_learn/openspec-retroactive-flow]] に追記候補
- 2026-06-16〜07-03: **リリース目標を 2027-01 → 2026-09 中旬に前倒し**（「早く進められるなら数ヶ月でリリースまでこぎつけたい。そのタイム観でスケジュール」）。外部向け表現は Habi 側 GPT レビュー起点で「機能数の完了ではなく Founder/PM が Habi 品質を観測・判断・調律できる状態」に補正 → [[05_learn/external-planning-docs-observability-framing]]
- 2026-06-16〜07-03: **Founder 260618 マスター（`docs/plans/UPDATED_MASTER_TEXT_JUNE2026`）を Product Charter / Policy / 要件 / 設計指針の canonical に採用** — 読解優先順位 **01→07→05→04→02→03→06→08→seeds→12→13**（Founder Deliverables Index が入口、Type Enum → Prompt Contract → Review/Guard Verdicts → Attunement 5 Levels の順で意味を積む）
- 2026-06-16〜07-03: **CTO / Founder-PM の責務境界を明文化** — CTO = 器（Schema / Trace / Step Debug / Guard / A-B / Runner）、Founder/PM = Policy 確定と Seed 作成（Attunement 5 段の意味 / Output Type / Review verdict / Prompt Contract / Narrative Memory boundary は CTO が推測で固めない）。Habi 側 GPT レビューでも「器は先行・調律は Founder 依存」の切り分けが高評価
- 2026-06-16〜07-03: **`HABI_DEVELOPMENT.md` を Month×12 モデル → ステップ制へリファクタ**（ステップ／設計・実装・統合・テスト状況／対応 change ／要件・アーキテクチャ・コンポーネントを 1 表で見える体裁、CHANGELOG にエントリ）。**`docs/plans` は今後の commit から外す**（秘匿性の repository 分離戦略）
- 2026-07-03: **comparison_mode でも Safety は常時 ON**（Guard/boundary は全モードで実行）— 「素の LLM で比較する」用途でも安全側は下りない。**A/B プローブは会話履歴を汚さない**（メモリ append を stub、本流実行時に混線しない）
- 2026-07-03: **dev デプロイは `AWS_PROFILE=bff-lambda-dev` 固定** — default プロファイル（CREW-USER）は本番系アカウント `864310138286`（MFA 必須）のため触らない

## 手順・Runbook

### dev デプロイ

- `AWS_PROFILE=bff-lambda-dev`（アカウント `062759670692` / user tatoflam / MFA 不要 / `s3://habi-bff-deploy-dev` アクセス可）で `scripts/deploy.sh` → `sam deploy`。default（CREW-USER）は本番系 `864310138286` で `arn:aws:iam::864310138286:policy/hlab-prod-MFA-required-policy` の explicit Deny（`make_bucket failed ... AccessDenied`）を食う
- `scripts/deploy.sh` は環境短縮名マップ（`development→dev` / `staging→staging` / `production→prod`）で `S3_BUCKET`（`habi-bff-deploy-dev` 等）と `STACK_NAME` を導出（commit `f3924dc` で修正済、3 環境 samconfig 完全一致、`bash -n` 構文 OK）
- 再発防止案: スクリプト冒頭で `sts get-caller-identity` を期待値比較して不一致 abort → [[05_learn/aws-profile-account-hlab-mfa]]
- 前提シークレット: Secrets Manager `OPENAI_API_KEY` + `JWT_ACCESS_SECRET`（habi-identity と一致必須）

### 実機動作確認（dev）

1. PM Chat Tool `https://ww6knpkhu4.execute-api.ap-northeast-1.amazonaws.com/development/pm/chat` にログイン — PM テスト用アカウント `pm-test@example.com / TestPass123`（PM Chat Tool で A1〜E4 自動実行可）。MFA verify あり
2. 実行 → **「Processing Flow (4-step)」+「Step Debug (StepTrace)」ON** で canonical Step Debug（`direction→attunement_selector→drafting→review→bff_guard→output→summarize`）を表示
3. **「A/B 比較」プリセット**（Habi vs 素の LLM / Review ON-OFF / Core ON-OFF / Summarize ON-OFF）で同一入力の構造差を並列確認（左右並置、各サイド Step Debug 折りたたみ、公平性行 `same_input` / `state` / `model` + `run_id`）

### ローカル開発の既知ギャップ

- SAM Local の `env.json` に `AuthProxyFunction` エントリが無く `HABI_IDENTITY_API_BASE` が container に渡らない → `/auth/login` が habi-identity に到達不能。AWS dev URL ログインも別軸で不通の場合あり（habi-identity 側でパスワードリセット / DB 再作成 / `JWT_ACCESS_SECRET` ローテートのいずれか）。env.json 整備 + habi-identity ローカル起動は別 change 案件 → [[05_learn/habi-bff-pmchat-localdev-gap]]

## 経緯

- **2026-04-29→30**（session c2dd2c85）: HABI_DEVELOPMENT_v2.md 新規作成（Excel `260216` マトリクスを v1 にマージ）。v1 未掲載 4 層の OpenSpec 提案を作成: [`add-attunement-policy`](https://github.com/hlab-it-sys/habi-bff/tree/main/openspec/changes/add-attunement-policy) 21 tasks / [`add-bff-guard`](https://github.com/hlab-it-sys/habi-bff/tree/main/openspec/changes/add-bff-guard) 29 tasks（BLOCK/REWRITE/DOWNGRADE/HOLD、`max_rewrite`、HOLD テンプレ）/ [`add-quality-always-on`](https://github.com/hlab-it-sys/habi-bff/tree/main/openspec/changes/add-quality-always-on) 26 tasks（Seed30 本／A/B Core on/off／Founder 逸脱／Core 再チェック／条文番号差分）/ [`add-bff-policy-monitoring`](https://github.com/hlab-it-sys/habi-bff/tree/main/openspec/changes/add-bff-policy-monitoring) 30 tasks。`src/services/attunement/{types,rules,selector}.ts` 新設、attunement-policy §1+§2+§3.2 完了 = 11/24。M3 以降（Narrative Memory / Context Builder / 温度推定 / Silence Engine / 心モード / Persona）は v2 §6 に未起票一覧化。§3.1/§3.3/§4.4 は habi-os 側 `StepTrace` 型拡張 PR が必要（[tasks.md §8](https://github.com/hlab-it-sys/habi-bff/blob/main/openspec/changes/add-attunement-policy/tasks.md) に follow-up note）。セッション全容: [[02_diary/2026-05-01]]
- **2026-05-02**（session 6a2f552b）: 既実装の async-chat-pipeline（API GW 29 秒制約を SQS + DynamoDB + worker でバイパス）をレトロアクティブに OpenSpec 化、`auth` + `user-os-persistence` に並ぶ 3 本目の spec として `openspec/specs/async-chat-pipeline/` に正規化。7 requirements: (1) `POST /api/v1/async/chat` 202 応答 + `jobId` 即時返却 (2) Job record = UUID + DynamoDB 24h TTL (3) SQS-trigger worker 状態遷移 `pending`→`processing`→`completed`/`failed` (4) DLQ redrive (5) `GET /api/v1/async/chat/{jobId}` status (6) `GET .../{jobId}/result` (7) `ChatJobMessage` payload contract。`/opsx:propose` 4 artifacts → 既実装チェック → validate --strict → `/opsx:archive`。commits `7c62128`（propose）+ `47d47a5`（archive）を `origin/main` push。レトロアクティブ起票フローの定型化 → [[05_learn/openspec-retroactive-flow]]
- **2026-05-06→07**（session c5c0230b）: M2 バッチ 2 change を 1 セッションで連続 archive、3 commits（`a73f672` / `c5a92ae` / `637fabe`）push、unit 171/171 + integration 24/24 pass。`add-attunement-policy` archive（`c5a92ae`、17/24、+6 = §3.3 PM Chat UI / §4.4 短期 workaround / §5.1 LocalStack e2e / §5.2 mock UI / §6.1 validate / §6.2 v2 plan 更新 / §6.3 archive。deferred 7 件 back-fill 条件付き: §3.1 StepTrace 拡張 = habi-os PR 待ち、§7.1 dev デプロイ = ユーザー承認、§7.2 Seed30 + A/B = quality-always-on 後、§8.1〜§8.3 habi-os 別リポ PR。capability spec `openspec/specs/attunement-policy/` 4 requirements 新規）。`add-bff-guard` archive（`637fabe`、27/29、deferred = §8.1 dev deploy / §8.2 Seed30+A/B）: `GuardEvaluator.evaluate()` 純関数で 5 値 Verdict を Review BOX 直後に挿入、`MAX_REWRITE` env（既定 2）超過で次の非 PASS Verdict は強制 HOLD（Drafting LLM 呼び出しを必ず止める）、HOLD は `pickHoldTemplate()` 純関数、DOWNGRADE は `lowerByOne()` で `chosen_level` 1 段下げ + `[INTERVENTION_LEVEL]` 再注入、BLOCK は `GuardBlockError`（`AppError` 継承）throw → 422 + reason、ViolationLog は pino warn `{ type, count_in_session, attunement_level, action, rewrite_count, draft_excerpt? }`（本番は excerpt 省略 = PII）、PM Chat UI に verdict バッジ + 4 項目 + mock Pattern C で HOLD 視認。§5.2 で SAM Local の構造ギャップ発覚（Runbook 参照）。学び: explore で「順序確定 + change スコープ境界判定」まで済ませる / deferred は tasks.md に back-fill 条件明記で archive 可。see [[02_diary/2026-05-07]]
- **2026-05-07**（session c6b59a1d）: M1 マトリクス突合 — M1/M2 層は実装済（Habi Core/Engagement Boundary ◎、User OS 保存読込 ◎相当、Attunement ◎、Guard ◎、段ジャンプ制御/違反ログ △ = StepTrace + violation-log.ts）、**M3 Narrative Memory / M4 Context Builder のみ未着手**（`grep narrative|memory|abstract.?log` 0 件）。Plan C 採択（quality-always-on 足場 → v1.0 リリース計画確定 → M3/M4 起票 → v1.0）。3 commits push: `a2f2883` docs/plans 統廃合 4→3+archive（v1 1003 行 + v2 265 行 → 統合 1270 行、章構成 = 第0部 3 バージョン位置づけ / 第1部 層×Month×V マトリクス 1.1〜1.9 / 第2部 v2.0 追加 4 層解説 / 第3部 M1-M12 月別 / 第4部 テスト計画 / 第5部 リスク管理 / 第6部 OpenSpec ロードマップ / 第7部 関連。7 files +521/-122、`add-bff-policy-monitoring/tasks.md`・`add-quality-always-on/tasks.md`・`docs/README.md` の参照リンク更新）/ `33ace48` PM 依頼書刷新（+251/-4: `PM_REQUEST_MONTH2_USER_OS.md` に §8 Attunement 監修 / §9 Guard 監修 / §10 Step Debug 検証（外部仕様のみ）で +358 行、冒頭に「🆕 2026-05-07 1 週間期限の優先確認サマリ」A〜D ブロック各 0.5〜1 日、期限 **2026-05-14**。旧 `HABI_ARCH_STEP_DEBUG.md` は `git mv archive/`、内部仕様 = LLM Off 時 JSON 構造・`< 5ms` メトリクス・`[OFF]` バッジ色は F4「Input/Output 表示は検証に十分か」で抽象化。完了条件チェックリスト 6+3 項目）/ `546794a` policy-monitoring M3 繰り下げ（3 files +57/-7: §1.8/§2.4「M3 以降毎回」、Month 2→3 CTO タスク移設 + callout、第6部 Month 列更新、proposal.md Why に 4 行追記、validate --strict 通過、tasks.md 無修正）。see [[02_diary/2026-05-08]], [[06_output/2026-05]]
- **2026-05-09**（session 8694d4d3）: ハビ（PM 横で動作する GPT エージェント）の 15 問 `(質問)ハビからの現時点での内容確認用質問260508.docx` に、Word の章立てを保ったまま `docs/plans/Inquiry_20260508/answers_260509.md` でインライン回答。1 周目はリポ相対パス + 行番号リンク（例 `[habi-client.ts:275-617](src/services/habi-client.ts#L275-L617)`）→ user 指摘「PM/Habi はリポを参照しない」→ 2 周目で全リンク削除 + 「> 注:」ブロック（Verdict 5 種 / Quality Always-On 5 種 / Narrative Memory 抽象ログ方針等を本文化）+ 用語前置き（4BOX / habi-bff / habi-core / habi-os / habi-identity / OpenSpec）。回答要点: Q1〜Q5 構造（4BOX 独立改善 / Direction 出力拡張）= すべて Yes、Fast/Deep のみ v1.0 は Attunement 5 段で代替 / Q6〜Q9 AI ガード = CLAUDE.md + openspec/project.md + OpenSpec ワークフロー + Quality Always-On の多層防御 / Q10 進捗 = 1 ループ◎ rewrite◎ Summarize ログのみ△ UserOS◎ / Q11/Q12 = 不安定は Summarize と Attunement のルール詰め、硬さは UserOS スキーマ・API GW 29s・意図的に硬い habi-core 不変条文 / Q13〜Q15 A/B = `stepOptions` フラグで個別 OFF 可、専用 CI は quality-always-on で構築中。総合回答「**器は壊れていない、むしろ意図的に空けてある**」。次アクション 5 件（DO NOT 常駐化 / Seed 30 本 / Narrative Memory 提案 / Policy Monitoring / 月次 Step Debug）。see [[02_diary/2026-05-09]]
- **2026-05-16**（session a1f12954、~75 min）: quality-always-on M1-M2 足場。2 commits（push は「2 commits ahead of origin/main — no push attempted per the safety protocol」で user 判断保留、後の `/git push` 前提）: [`5cc63bd`](https://github.com/hlab-it-sys/habi-bff/commit/5cc63bd) `feat: Add Quality Always-On CI gate (runner + A/B + Core re-check)` — runner + A/B（Core on/off）+ Founder 逸脱 + Core 再チェック CI 配管、`QUALITY_SEED_MIN_COUNT` env で seed 数 gate 制御 / [`a6fd2a1`](https://github.com/hlab-it-sys/habi-bff/commit/a6fd2a1) `docs: Pin Habi relational DO/DON'T as AI-common rules`。change は §1-§7 概ね完了、§8 validate + archive と §9 PR テンプレート + 既定値昇格は Seed 30 本投入後に back-fill。M3 `add-narrative-memory` 提案は「PM 動きが見えるまで休む」を選択。see [[02_diary/2026-05-16#00:36-01:50 JST]]
- **2026-06-12**（session 5b553af9）: プロダクト計画 × 実装状況レポート HTML を `/tmp/habi-bff-status-report-20260612.html` にローカル生成（配信なし = 06_output 該当なし）。CTO 単独 → user フィードバックで **PM ↔ CTO 並列構造** + Mermaid 3 図（システム全体図 / 4 step Processing Flow / PM ↔ CTO 監修フロー）に拡張。スナップショット: M1–M2.1 完、M2.2 v2.0 送り、M3 進行中、M4 以降未着手、2026-01 リリースまで残 7 ヶ月。PM 積み残し・リスク R1〜R3/P1〜P4・提言 4 件を初可視化（現在の状態に転記済）。Mermaid は R-1 縦 TB → R-2 横 LR → R-3 メイン縦 + Narrative Memory subgraph 横並びで着地、Guard verdict 4 種 + max_rewrite を 1 行統合、点線エッジ誤記 `-.|label|.->` → 正規 `-. "label" .->` → [[05_learn/mermaid-dotted-edge-label-syntax]]。学び: 1 行 = 1 Month × 列 = CTO / PM / 受入ブロッカー の表で待ち合わせ点が即可視化 / HTML レポートはローカル限定でも Mermaid のズーム・整形でレビュー密度が上がる。see [[02_diary/2026-06-12]]
- **2026-06-12**（session 1889f8ec）: `add-narrative-memory` を `/opsx:propose` → 実装 → push（M3 BFF-side、archive 見送り）。設計の核: DynamoDB テーブル新設（`pk=user_id`, `sk=memory_id`, attributes = kind / version / payload / source_turn_id / created_at）/ `NarrativeMemoryRepository.append / list / get` 3 メソッド + 単体テスト / 1 BFF turn = 1 メモリ書き込み（midway 中断は no-op）/ Pre-write Core compliance gate（禁止カテゴリ・個人情報・法的リスク検証）と Processing Flow 配線は要件として spec 記載のみ（Section 5、依存待ち）。`/opsx:apply` で Section 1〜4 着地。commit `de15bd4`（`5cc63bd..de15bd4`、19 files +1808/-7）`feat: Propose and implement narrative-memory infra (M3 BFF-side)` を `hlab-it-sys/habi-bff` main へ push（配信物: `https://github.com/hlab-it-sys/habi-bff/commit/de15bd4`）。spec: [add-narrative-memory/specs/narrative-memory/spec.md](https://github.com/hlab-it-sys/habi-bff/blob/main/openspec/changes/add-narrative-memory/specs/narrative-memory/spec.md)。気づき: 未実装 requirement を spec に書けば「設計確定・実装依存待ち」を正規表現でき、後続 PR は wiring 追加のみで spec 不変。see [[02_diary/2026-06-12#14:50 JST  run-82b]] / [[06_output/2026-06#GitHub commits — hlab-it-sys/habi-bff add-narrative-memory M3 BFF-side (2026-06-12)]] / [[05_learn/openspec-retroactive-flow]]
- **2026-06-16→07-03**（session 6d328a3b、長期: 開始 06-16 09:38、最終 user turn 07-03 13:14）: PM 260613 指示書パック（`docs/plans/UPDATED_PLAN_JUNE2026`、26 文書 — プロジェクト憲章元データ / 責務分担・コミュニケーション定義 / CTO 報告・CTO/PM 共有 gate 定義 / ルール / 実装レベル規約 / 設計思想 / API 規約）を吸収。CTO 向け先読 3 文書 =「Founder PM への確認・連絡タイミング 260613」「Habi Ver1.0 AI コーディング実装方針 260613」ほか。→ Founder 260618 マスター canonical 採用、ステップ制リファクタ、2026-09 中旬前倒し（決定事項参照）。派生 change 6 本起票（現在の状態参照）。PM Chat MFA verify（`212992`）+ ログイン成立、`crew-user_hlab_device` の指定違い（別 crew role 混入）修正、Month 2 PM テストケース `docs/tests/PM_TESTCASE_MONTH2_USER_OS.md` を実運用で踏破。`CTO_STATUS_REPORT_260703.html` + `HANDOVER_TO_FOUNDER_AI_260703.md`（先方 AI に渡すドキュメントのリスト化）を `docs/plans/UPDATED_MASTER_TEXT_JUNE2026/` 配下に生成。see [[02_diary/2026-06-16]], [[05_learn/external-planning-docs-observability-framing]]
- **2026-07-02→03**（同 session 6d328a3b 最終盤、run-118 で抽出）: **Step 4.3 完了** — `src/services/comparison-mode.ts` 新規、canonical `ComparisonMode` 7 モード（`full_habi` 現状不変・既定 / `habi_core_off` / `direction_llm_off` / `review_llm_off` / `summarize_llm_off` / `all_habi_flow_off` = flow は残し全 Step LLM off / `baseline_llm` = single-call + Core off）を skipHabiCore / processingFlow / 各 Step LLM に写像。validation → 非同期経路（`chat-start` / `queue` / `chat-processor`）→ `executeChatPipeline` に貫通、分岐前に effect 適用。純関数テスト付き、**unit 249 green**（pre-existing warning 1 = 不変）。**Step 6.3 完了** — PM Chat UI の A/B 比較パネル（`runChatJob` 抽出 + 再利用、プリセット 4 種、詳細は Runbook）。**dev デプロイ実機成功**（最初の試行は default プロファイルで `hlab-prod-MFA-required-policy` explicit Deny → user 直感「`crew-user_hlab_device` が指定されているのが違う気がする」→ `~/.aws/config` 精査で `bff-lambda-dev` プロファイル判明 → 成功。詳細 Runbook + [[05_learn/aws-profile-account-hlab-mfa]]）。`scripts/deploy.sh` バグ修正 commit `f3924dc`（`S3_BUCKET="habi-bff-deploy-${ENVIRONMENT}"` が `habi-bff-deploy-development` に展開され samconfig `habi-bff-deploy-dev` と不一致 / `STACK_NAME="habi-bff-$(echo $ENVIRONMENT | cut -c1-4)"` が staging を `habi-bff-stag` に切り詰め → 環境短縮名マップ導入）。docs 3 点（すべて `docs/plans/` = git 除外・機微・ローカルのみ）: HABI_DEVELOPMENT.md §3「現在地」を 2026-07-03 更新（Founder 確認① 可）+ §9「環境・デプロイ」新設（dev アカウント / プロファイル / stack / PM Chat Tool URL / default は本番系の旨 / 前提シークレット）/ `CTO_STATUS_REPORT_260703.html`（結論 3 行 / 到達点 / 実装状況ステップ表 / Web で試す手順 URL+3 手順 / Founder が今できること = 単発差・構造差の観測 / Founder 依頼 = Gate 1・Seed が律速 / 次の実装 / ガバナンス前提）/ `HANDOVER_TO_FOUNDER_AI_260703.md`（A: 当方→先方 = 状況レポート / ステップ計画 / CHANGELOG / openspec change 群 + master doc ↔ 当方 spec 対応表、B: 先方→当方 = Gate 1 Policy/Enum/Schema Lock・禁止表現・Seed 期待値/Rubric・Memory 境界・[UNRESOLVED] 解消、C: 実機 URL、D: 渡し方の推奨手順 + 秘匿方針 = Holdout は渡さない、openspec は生 Policy 非含有なので共有可）。see [[02_diary/2026-07-03]] / [[06_output/2026-07]]

## Links

- [[02_diary/2026-05-01]] — 2026-04-30 セッション全容（翌朝 ingest）
- [[02_diary/2026-05-07]] — M2 バッチ（attunement + guard archive）
- [[02_diary/2026-05-08]] — Plan C + docs 統廃合 + PM 依頼書
- [[02_diary/2026-05-09]] — Habi 15 問 inquiry 回答
- [[02_diary/2026-05-16#00:36-01:50 JST]] — quality-always-on 足場
- [[02_diary/2026-06-12]] — ステータスレポート HTML
- [[02_diary/2026-06-12#14:50 JST  run-82b]] — add-narrative-memory
- [[02_diary/2026-06-16]] — PM 260613 統合 + Founder Master 260618
- [[02_diary/2026-07-03]] — dev デプロイ実成功
- [[05_learn/openspec-retroactive-flow]] — レトロアクティブ起票フロー + archive 見送り運用則
- [[05_learn/habi-bff-pmchat-localdev-gap]] — PM Chat ローカル開発の構造ギャップ
- [[05_learn/mermaid-dotted-edge-label-syntax]] — Mermaid 点線エッジ syntax
- [[05_learn/external-planning-docs-observability-framing]] — 外部向け計画の observability framing
- [[05_learn/aws-profile-account-hlab-mfa]] — AWS プロファイル取り違い + 再発防止
- [[06_output/2026-05]] / [[06_output/2026-06#GitHub commits — hlab-it-sys/habi-bff add-narrative-memory M3 BFF-side (2026-06-12)]] / [[06_output/2026-07]] — 配信物記録
