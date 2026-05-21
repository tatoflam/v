---
title: ToDoBot — LINE グループ業務会話 → 日次 ToDo レポート MVP
category: 05_learn
tags: [topic:todobot, project:todobot, tech:openspec, tech:python, tech:firebase, tech:firestore, tech:line-messaging-api, tech:anthropic-claude, tech:google-workspace, tech:gmail-api, tech:domain-wide-delegation, stage:dogfood]
sources: [2648ee43-ade1-4be4-b64a-b31c9d21bfb3, f9415d55-991f-4d85-8f11-50e87deb910b]
updated: 2026-05-21
---

# ToDoBot — LINE グループ業務会話 → 日次 ToDo レポート MVP

## Summary

LINE グループに常駐する Bot が業務会話を受信し、1 日 1 回 LLM で「誰が・いつまでに・何を」を構造化抽出、20:00 JST（プロファイル可変）に LINE push と メールで配信する。OpenSpec で proposal / design / specs / tasks 一式を起票（change 名 `line-todo-bot-mvp`、`openspec validate` 通過）。リポジトリ: `~/repo/github/tatoflam/ToDoBot`。

## 採用スタック（design.md）

Q&A 4 件（LLM、メール、Firebase、抽出範囲）の回答反映後の最終形:

| レイヤ | 採用 |
|---|---|
| ランタイム | **Cloud Functions for Firebase 2nd gen (Python 3.11)** |
| DB | **Firestore**（TTL 30 日、scheduled function で集計） |
| スケジューラ | **Scheduled Functions**（Cloud Scheduler は使わない） |
| LLM | **Anthropic Claude**（既定 `claude-haiku-4-5`、必要時 Sonnet）。`tools` ベースの構造化出力＋プロンプトキャッシュ |
| メール送信 | **Gmail API + Domain-wide Delegation (キーレス DWD)**（5/21 に SMTP Relay から切替、`iamcredentials.googleapis.com` 経由で `developer1@` の short-lived token を発行 → `gmail.users.messages.send`）。`Notifier` 抽象で吸収済み、置換はモジュール 1 つで完結。SMTP Relay 案は archive 扱い（user が Workspace 管理者本人で 2SV を 1 サービスアカウントにも入れたくなかったため鍵廃止に振り切り） |
| LINE | **Messaging API**（webhook → Bot push） |

旧案（Cloud Run + Postgres + Cloud Scheduler）は捨て、Firebase に一本化することで Docker / Alembic / Scheduler の独立セットアップを削除。

## Capabilities（4 本）

`openspec/changes/line-todo-bot-mvp/specs/<name>/spec.md`:

- **`line-bot-ingestion`** — Webhook 受信・署名検証・グループメッセージ収集
- **`todo-extraction`** — LLM ＋ JSON Schema で構造化抽出、PII マスキング、保存 30 日
- **`daily-report`** — 集計・LINE/メール配信・冪等・指数バックオフ再送
- **`notification-profiles`** — `config/profiles.yaml` ＋ `ACTIVE_PROFILES` 環境変数で複数プロファイル切替（LINE グループ ID と通知先メールを差し替え可能）

## 工数見積（tasks.md）

| # | セクション | 工数 |
|---|---|---:|
| 1 | プロジェクト初期化 | 1.5d |
| 2 | 設定／プロファイル | 1.5d |
| 3 | データ層（Firestore） | 2.0d（旧 SQLAlchemy 案より +1.0d） |
| 4 | LINE Webhook 受信 | 2.5d |
| 5 | ToDo 抽出（LLM） | 4.0d |
| 6 | 日次レポート配信 | 3.0d |
| 7 | スケジューラ起動口（Scheduled Functions） | 1.0d |
| 8 | 観測・運用 | 1.0d |
| 9 | デプロイ（Firebase） | 1.5d（旧 Cloud Run 案より −1.5d） |
| 10 | 動作確認 | 1.5d |
| 小計 | | **19.0d** |
| バッファ 20% | | +4.0d |
| **合計** | | **≈ 23.0 人日（約 4.5 週間）** |

不確実性ホットスポット: 抽出プロンプト設計、Workspace SMTP Relay の管理者承認リードタイム（1–3 営業日、並行着手推奨）、Firestore TTL/index 学習。

## 運用コスト試算（3 グループ × 150 msg/日）

`docs/line-todo-bot-mvp-report.md §9` に独立セクションとして集約。

### 前提

- LINE グループ 3、各 150 msg/日 = 450 msg/日
- 抽出 LLM 呼出 90 回/月、LINE push 90 通/月、メール 90 通/月
- LLM = Claude Haiku 4.5 + プロンプトキャッシュ（system + few-shot ~3,500 tok を 1 日 1 回 write）
- 1 抽出呼出: 入力 ~17,500 tok、出力 ~1,500 tok

### 月額（30 日）

| 項目 | 月額 |
|---|---:|
| Anthropic Claude Haiku 4.5 | ≈ $2.10 |
| Firebase / GCP | $0（無料枠内） |
| Workspace SMTP Relay | $0（既存契約） |
| LINE Messaging API | $0（無料 200 push/月以内） |
| **合計（中央値）** | **≈ $2 / ¥320** |

精度優先で全グループ Sonnet 4.6 に上げても **月 ¥1,000–1,500** に収まる。Static IP（VPC Connector）採用なら +¥1,500–2,250。

### スケール閾値

- LINE push 200 通/月（=Bot 応答含めて約 6 push/日まで無料）
- Anthropic Tier 1（$5/月）
- Firestore 20K writes/日（=1 日 1 万メッセージ程度）

## 残課題（Open Questions）

OpenSpec design.md の OQ 区分:

- **OQ1–OQ4**: 解決済（LLM=Claude、メール=Workspace SMTP、ランタイム=Firebase、抽出範囲=全文＋メンション重み付け）
- **OQ5**: ~~SMTP Relay の許可 IP / VPC Connector 要否~~ **2026-05-21 close** — メール送信を Gmail API + DWD に切替えたため SMTP Relay の許可 IP 議論自体が消滅。Gmail API は HTTPS 経由で VPC Connector 不要
- **OQ6**: Anthropic 残データ取扱と Workspace データ持出ポリシーの整合（社内法務確認）

## メール送信方式の変更 (2026-05-21)

SMTP Relay → Gmail API + Domain-wide Delegation (キーレス DWD) への切替。理由と手順を [[03_work/todobot]] §「2026-05-21 E2E 疎通の流れと詰まりポイント」で詳述。要点:

- Workspace アプリパスワードは Workspace の 2SV 強制設定がプロジェクト管理者本人 (`thomma@`) でも避けたく、SA 鍵も発行したくない → `iamcredentials.googleapis.com` で **キーレス impersonation**
- DWD 登録: admin.google.com → セキュリティ → API の制御 → ドメイン全体委任、クライアント ID = ランタイム SA の Numeric ID、スコープ `https://www.googleapis.com/auth/gmail.send`
- ランタイム SA に自己 `roles/iam.serviceAccountTokenCreator` を付与（同一 SA が自身に対し短命トークンを発行）
- `iamcredentials.googleapis.com` の enable と SA self Token-Creator の binding は **`thomma@` （super-admin）でないと PERMISSION_DENIED**（`developer1@` に Service Usage Admin を付けても org policy で弾かれる）

## @mention 解決の修正 (2026-05-21)

`resolve_assignee` の初版は @mention の user_id を `users/` キャッシュと照合してから採用していた。`users/` は LINE Profile API の制約で「グループで発言したことのあるメンバー」しか格納されず、**未発言の人を @mention しても「未割り当て」に分類されていた**バグ。

修正後 (`b83d678`):

- 一意の @mention user_id があればキャッシュ未登録でもその user_id を担当者として採用
- 表示名はメッセージ本文の mention span (`mentionees[].index` + `length`) から `@` を除いて抽出（=新ヘルパー `_mention_display_name`）

design.md の「mention boost」方針はそのまま維持しつつ、boost の前提条件（発言履歴あり）を緩めた形。テストは `test_extraction.py` に未発言メンバー @mention の 4 ケースを追加。

## 実装進捗 (2026-05-11 時点)

planning (4-28) の 23.0 人日見積に対し、**§1-§4 + B1-B4 + ops docs の 5 commit が landed**（4-29〜4-30 で 1 セッション完走、54 tests pass）。残は §5-§10。

| § | 内容 | 状態 | コミット |
|---|---|---|---|
| 1 | プロジェクト初期化 | ✅ | `8b98f60` (root) |
| 2 | 設定／プロファイル | ✅ (29 tests) | `2b22b35` |
| 3 | データ層 (Firestore) | ✅ (11 tests) | `106f9fd` |
| 4 | LINE Webhook 受信 | ✅ (14 tests) | `dac0875` |
| 5 | ToDo 抽出 (LLM) | ⬜ next | — |
| 6 | 日次レポート配信 | ⬜ | — |
| 7 | Scheduled Functions | ⬜ | — |
| 8 | 観測・運用 | ⬜ | — |
| 9 | デプロイ (Firebase) | ⬜ | — |
| 10 | 動作確認 | ⬜ | — |
| B1-B4 | 外部準備チェックリスト | ✅ docs | `710cb9b` |
| Ops | 運用ドキュメント (二層) | ✅ docs | `c7556f9` |

詳細とリポ状態は [[03_work/todobot]]。

### 設計→実装で確定したスペック

- **config.py**: `ProfilesFile` + `Settings` (pydantic-settings)、`HH:MM` 正規表現 / `zoneinfo.ZoneInfo` / `EmailStr` (`email-validator`) / `active_profiles` ⊆ `profiles` の `model_validator`。env override + CSV active_profiles parse + シークレット未設定の早期検出 (`assert_runtime_secrets_present()`)
- **models.py**: `RawMessage`（mentions / quoted_message_id 含む）/ `UserCache` / `Todo`（信頼度 0-1、source 非空、TTL 30 日）/ `ReportRun`
- **firestore_repo.py**: 4 コレクション facade、`try_acquire_report_run` でトランザクション冪等
- **line_handler.py**: `WebhookParser` 署名検証、group/room の text のみ収集、`UserMentionee` / `AllMentionee` / `quoted_message_id` をスペック通り捕捉
- **main.py**: `@cache` で cold-start 後 handler 再利用、`InvalidSignatureError`→403。`firebase-functions` SDK の sync/async ユニオン型に `# type: ignore` を `get_user` / `get_message` で揃える対処
- **テスト 54 件**: `pytest` / `ruff` / `black --check` / `mypy --strict` 全クリア

### 4-29 実装時のハマりポイント

- **`.python-version=3.11` → pyenv に未インストール**（`python3.11 not found`） → `.python-version` を `3.10.11` に書き換え（system に既にインストール済）で対応。**pyenv install せず既存版に揃える** が手早い
- **`firebase-functions` SDK の型 stub が sync/async ユニオン** → 部分的 `# type: ignore` で対処、同じスタイルに揃える
- **`ruff` UP037（quote 付き forward ref）+ I001（import 並び）** → auto-fix 一発、`black` 再整形 1 ファイル

### 4-30 朝 — 運用ドキュメントの二層化パターン

「初回セットアップ」と「運用中の参照」を **同じドキュメントに混ぜると 3〜6 ヶ月後に探すコストが高い** という気づきから、`docs/external-setup/`（時系列の手順書）と `docs/operations/`（所在マップ + ローテ手順 + トラブルシュート）の二層構造を確立。両層から相互リンク。

このパターンは **API キー / SMTP / OAuth / クラウドサービスの credentials 全般** に転用可能 — habi-bff の `docs/plans/` も同様の二層化が候補（現状は `HABI_DEVELOPMENT.md` 単一に集約済）。

## Links

- [[02_diary/2026-04-28]]
- [[02_diary/2026-04-29]] — §2-§4 + B1-B4 一気実装
- [[02_diary/2026-04-30]] — 運用ドキュメント二層化
- [[03_work/todobot]] — プロジェクトステータス
- [[05_learn/wiki-automation-pipeline]] — OpenSpec ワークフロー
- [[05_learn/specdrawing-material-presenter]] — 同じく OpenSpec 駆動の MVP 事例
