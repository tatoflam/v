---
title: AfterSchoolPlatform (小金井市 放課後プラットフォーム MVP)
category: 03_work
tags: [project:afterschoolplatform, client:koganei-city, entity:icu, stage:in-progress, tech:nextjs, tech:typescript, tech:postgresql, tech:prisma, tech:react-pdf, tech:trustdock, tech:vitest, tech:playwright, domain:education, capability:user-accounts, capability:identity-verification, capability:program-catalog, capability:municipal-billing, status:active]
sources: [cbfe2df6-6fe3-4ef0-9c18-3795800a122b, 3ca18b54-5b6e-41c2-91d1-315125bc379d, b005bb0f-a089-4a94-a211-d24289f71d34]
updated: 2026-06-12
---

# AfterSchoolPlatform

## Summary

小金井市の公立小学校に対する放課後プラットフォーム MVP。「空き教室 × ICU 留学生講師 × 共働き保護者の需要」の 3 つの未活用リソースを単一の行政グレード web サービスに接続する。1 年目 PoC (1 校・約 20 名・3 ヶ月) を 2 年目補助金申請 (こども家庭庁 / IT 導入補助 / 日本財団 / 東京都) のエビデンス基盤として設計。

**初出**: 2026-05-16 — `cbfe2df6` / `3ca18b54` の 2 セッションが `/wiki-ingest` の SessionEnd 自己 enqueue 経由で queue に出現したが、内容は wiki-ingest no-op のみ。本ページは repo 自体の存在記録のためのスタブで、substantive な進捗ログは次以降のセッションで追記する。

## Details

### スコープ (`openspec/changes/define-mvp-scope/proposal.md` 抜粋)

- **シングルテナント**: 小金井市 1 自治体向け web app、公立小学校施設内・週次プログラム・ICU 留学生講師
- **4 ユーザロール**: admin (自治体職員) / instructor (ICU 留学生、eKYC 必須) / parent (保護者、eKYC 必須) / child (プロファイルのみ、ログインしない)
- **B2G 課金モデル**: 教育委員会へ月次請求 (¥300〜¥500 / 在籍 / 月)。**保護者はプラットフォーム上で支払わない**。Stripe / クレカは MVP 範囲外、銀行振込ベース
- **行政グレード監査ログ**: 児童 PII / 在籍 / 出席 / eKYC / 請求書の読書全アクションを actor + IP + UA + timestamp で 3 年以上保持、CSV エクスポート可
- **モバイル & 日本語ファースト**: 保護者主スマホ、英語 UI は別 change で後送り
- **明示的非ゴール**: アプリ内メッセージング / ウェイトリスト / push&SMS 通知 / フィードバック評価 / マルチテナント / native mobile / 英語 UI / 自動決済 / 銀行入金自動消込 / LMS 連携

### 新規 capabilities (MVP)

- `user-accounts` — 4 role + email+password + RBAC
- `identity-verification` — 外部 eKYC ベンダー (第一候補: TRUSTDOCK / LIQUID / Pocket Sign)
- `program-catalog` — 教室スコープ・週次スケジュール・定員・月額単価・講師割当
- `enrollment` — 保護者→児童 1 名予約、定員強制、保護者 `kyc_status=verified` 条件
- `municipal-billing` — 月次 invoice 生成 (draft → issued → paid/void)、PDF + 銀行振込照合
- `attendance` — 講師セッション単位 出席/欠席/遅刻、保護者は自分の児童のみ閲覧
- `audit-logging` — 追記専用、未成年 PII + invoice 全アクセスを記録

### 技術スタック (推定)

- **Frontend**: Next.js (App Router) + TypeScript、モバイルファースト UI
- **Backend**: PostgreSQL (日本リージョン マネージド)、`argon2id` パスワードハッシュ、HTTPS-only、cookie session (HttpOnly/Secure/SameSite=Lax)
- **PDF 生成**: `@react-pdf/renderer` または `pdfkit`
- **外部依存**: eKYC ベンダー / トランザクションメール送信プロバイダー / マネージド PostgreSQL
- **コンプライアンス**: APPI (個人情報保護法) 初日対応、保管時暗号化、暗号化バックアップ、URL/ログから PII 排除

### コンテキスト

- **client**: 小金井市教育委員会 (municipality)、ICU (講師供給)、保護者 (申込者)
- **stage**: spec documentation 完了 (`openspec/changes/define-mvp-scope/proposal.md` 起票)、green-field 実装はこれから
- **補助金トリガー**: 1 年目補助金 (こども家庭庁 放課後児童健全育成事業) が「安全で監査可能な運用エビデンス」を評価する → MVP の capability セットはそのエビデンス生成の最小面積として設計

### docs ファイル一覧 (`~/repo/github/tatoflam/AfterSchoolPlatform/docs/`)

- `proposal-koganei.md` — 小金井市向け提案書
- `outreach-icu.md` — ICU 接触用文書
- `outreach-school.md` — 学校接触用文書

## Links

- [[02_diary/2026-05-16]] — 初出セッションの ingest メモ
- [[05_learn/wiki-automation-pipeline]] — cbfe2df6 / 3ca18b54 は SessionEnd 自己 enqueue 病理 6 の観測対象

## 2026-06 — ChatGPT 提案を proposal 起源にして openspec apply で MVP 主要 Section 大量着地 (session b005bb0f)

### 入口

`/openspec-propose` をスタート点に、ChatGPT で先行整理されていた **小金井市 放課後グローバル交流教室運営事業 1 枚要約 + 補助金申請ストーリー** を proposal.md の起源として注入。openspec の proposal/design/specs/tasks 4 artifact 生成 → そのまま `/opsx:apply` に流して **Section 5 (KYC) + Section 6 (Programs/Classrooms) + Section 9 (Billing)** を 1 セッションで連続着地。

### 仕様レイヤの方針調整 (本セッションで合意)

- **OpenSpec docs は全日本語化**: 機能影響なしを確認後、proposal/design/spec/tasks の language を日本語統一
- **B2G 課金モデルへ pivot**: 保護者課金 ¥3,000〜¥5,000/月 → **教育委員会側課金 ¥300〜¥500 / 在籍児童 / 月**、運用コストも ~1/10 にスケールダウン。保護者はプラットフォーム上で支払わない (= 銀行振込ベース、Stripe 不要)
- **Section 着手順序**: ユーザ提案 1,2 → 4 (外部依存 = eKYC は時間がかかるので並行待ち) → 残り直線

### Section 5 — Identity Verification (KYC) 完了

`@react-pdf/renderer` ではなく Trustdock を第一候補に確定 → IKycProvider 抽象 + Trustdock 実装。HMAC-SHA256 webhook signature 検証 + `timingSafeEqual` (タイミング攻撃対策) + dev フォールバックを純粋関数群で実装。

| ガード | 実装 |
|---|---|
| `kyc_cases.raw_payload` は **平文保存禁止** | AES-256-GCM (`KYC_PAYLOAD_KEY` 32 byte env)、`v1:iv:tag:ct` 形式、IV 毎回ランダム |
| Webhook 署名なし / 改竄署名で副作用ゼロ | HMAC-SHA256 + `timingSafeEqual`、401 応答前に全検証 |
| 同一 case の同 result 再配信は no-op | `applyWebhookResult` で `result === existing.result` を idempotent 判定 |
| 未知 `provider_case_id` の webhook は 200-noop | enumeration attack 対策 |
| 不存在ユーザの dashboard アクセスは 404 (存在漏洩防止) | `requireSignedIn` / `requireRole` |

- crypto.ts: 5 unit (round-trip / IV ランダム性 / 改竄検知 / v2 拒否) ── 後方非互換を明示 reject
- kyc-trustdock.ts: 10 unit (status 正規化 3 + 署名失敗 6 + dev フォールバック)
- kyc-service.ts: 9 integration (initiate / apply / 失敗→再 initiate / override / reissue)
- kyc-webhook.ts: 5 integration (不正署名 401 / 未知 case 200 / verified / べき等)

### Section 9 — Billing (月次請求 + PDF) 完了

| ガード | 実装 |
|---|---|
| 同期間で **draft/issued/paid 二重作成不可** | `municipal_invoices_period_active_uniq` partial unique + service 事前チェック |
| 連番 **ギャップなし** (同自治体・同月単位) | `SELECT ... FOR UPDATE on municipalities` 行ロック内で次番号採番。`scripts/check-invoice-sequence.ts` 連番ギャップ検出 CI |
| 明細は **発行時点のスナップショット** | `child_display_name / program_title / unit_price_jpy` をコピー、後の child 名変更は波及しない |
| `paid` / `void` は **終端状態** | `state.ts` の遷移ガード (`InvoiceTransitionError`) |
| PDF は **発行時 1 回だけ生成** | `issuedAt !== null` で再発行を拒否 |
| PDF DL は **admin のみ + 監査ログ** | `requireRole("admin")` + `logAccess(read)` |

- `@react-pdf/renderer` + Noto Sans JP フォールバック (= bundled 化試行が外部 DL 拒否で失敗 → 「あれば使う」フォールバック方式に切替、`assets/fonts/README.md` で利用者導線)
- Storage 抽象: S3 / LocalFs env で自動切替、Email 抽象: Resend / dev-log
- 14 integration (3 明細 / 期間外除外 / 重複 / void 後再生成 / month 跨ぎ連番 / 状態遷移 / 二重発行禁止 / PDF DL audit)

### Section 6 — Programs/Classrooms CRUD + publish + 保護者カタログ 完了

| 制約 | 実装場所 |
|---|---|
| `capacity > 0` かつ `≤ classroom.capacitySeats` | `assertCapacityFitsClassroom` |
| `monthly_price_jpy ∈ [300, 500]` 整数 | `assertCommonInvariants` (B2G 課金モデルの数値ガード) |
| 講師は `role = instructor` かつ `kyc_status = verified` | `assertInstructorEligible` |
| 公開時 instructor を **再検証** | `publishProgram` 内で再 check (kyc 取消ケース対策) |
| publish 後の schedule / capacity / 単価 / 教室 / 講師 / title 編集を拒否 | `updateProgram` の `SCHEDULE_FIELDS` ガード (description のみ可) |
| publish はトランザクション内で sessions materialize と同時 | `publishProgram` の `$transaction` |
| archive は **一方向** (un-archive 不可) | `archiveProgram` + `updateProgram` の archived ガード |
| sessions は **Asia/Tokyo** で materialize、`weekday` は **JS getUTCDay 規約** (0=日..6=土) | `schedule.ts` |

### CI ガード (現在 4 種)

| Script | 用途 |
|---|---|
| `pnpm typecheck` | TS 厳格モード (strict + noUncheckedIndexedAccess + noImplicitOverride) |
| `pnpm lint` | ESLint flat config + typescript-eslint |
| `pnpm test` | Vitest unit + integration (Section 5/6/9 で 115 pass) |
| `pnpm check:invoice-sequence` | 連番ギャップ検出 (per-municipality / per-month) |
| `pnpm e2e` | Playwright 6 シナリオ (auth middleware redirect 等) |

### 状態 (本セッション終了時)

- 完了 Section: 5 (KYC) / 6 (Programs/Classrooms) / 9 (Billing) — typecheck / lint / **115 unit+integration** / 6 E2E / production build 全 green
- stage を `planning` → `in-progress` に昇格
- 次手は Section 2 (User Accounts 詳細) + Section 4 (eKYC 外部接続テスト = Trustdock sandbox 申込) — user 提案で 4 から並行着手

### 副産物・学び

- **ChatGPT 先行整理 → openspec proposal.md 化** のフローは proposal の論点抜けが少なくなる。事業計画 1 枚要約 + 補助金申請ストーリーが既に Markdown 化されていると proposal の "What/Why" にそのまま流せる
- **Noto Sans JP の build-time DL は Vercel/CI 環境で拒否されがち**: 「あれば使う」フォールバック + README ガイダンスが運用負担最小
- **連番ガード = 2 段 (DB unique + CI check)**: DB 側で重複を block しつつ、CI で gap 検出を毎回回せばユーザは「番号体系が壊れる」恐怖から解放される。請求書系の必須 pattern

see also: [[02_diary/2026-06-12]], [[05_learn/openspec-retroactive-flow]]
