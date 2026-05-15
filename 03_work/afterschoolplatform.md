---
title: AfterSchoolPlatform (小金井市 放課後プラットフォーム MVP)
category: 03_work
tags: [project:afterschoolplatform, client:koganei-city, entity:icu, stage:planning, tech:nextjs, tech:typescript, tech:postgresql, domain:education, status:active]
sources: [cbfe2df6-6fe3-4ef0-9c18-3795800a122b, 3ca18b54-5b6e-41c2-91d1-315125bc379d]
updated: 2026-05-16
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
