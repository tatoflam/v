---
title: ToDoBot — LINE 業務会話 → 日次 ToDo レポート
category: 03_work
tags: [project:todobot, tech:python, tech:firebase, tech:firestore, tech:line-messaging-api, tech:anthropic-claude, tech:google-workspace, tech:openspec, tech:pytest, tech:mypy-strict, stage:implementation-complete, stage:pre-deploy, milestone:mvp-code-complete, milestone:repo-pushed-meguruit, entity:meguruit-org, client:meguruit]
sources: [2648ee43-ade1-4be4-b64a-b31c9d21bfb3, 8dc542f5-d276-4e26-b04a-6f9fe822db47]
updated: 2026-05-16
---

# ToDoBot

## Summary

LINE グループに常駐する Bot が業務会話を受信し、1 日 1 回 LLM (Claude Haiku/Sonnet) で「誰が・いつまでに・何を」を構造化抽出、指定時刻 (既定 20:00 JST、プロファイル可変) に LINE push とメールで配信する個人事業向けの自動化。

リポ: 当初 `tatoflam/ToDoBot` (4-29 root-commit `8b98f60`) で着手していたが、2026-05-16 に user が組織アカウント側で新リポ `meguruit/ToDoBot` (private、SSH origin) を切り、`main` を push 完了 → これが canonical となった。ローカルの working tree パスは `/Users/tato/repo/github/tatoflam/ToDoBot` のまま (path はリネームせず、remote だけ差し替え)。

OpenSpec workflow で proposal / design / specs / tasks 一式起票、change 名 `line-todo-bot-mvp`。設計詳細・運用コスト試算・spec 一覧は [[05_learn/todobot-line-mvp]] を参照。

## ステータス (2026-05-16 時点) — MVP コード完成 + push 完了

- **28/30 タスク完了** (`line-todo-bot-mvp` change、spec-driven)。残 §10.1 (24h ドッグフード) / §10.2 (受入チェックリスト消化) は実機デプロイ後の手動運用タスクで、コード作業は完了
- **テスト**: 54 → **142 件** green、カバレッジ **92%**、`mypy --strict` / `ruff` / `black --check` 全クリア (28 ソースファイル)
- **意図的に低カバレッジ**: `firestore_repo.py` (30%、薄い委譲層 → Firestore エミュレータで spec §10.1 統合テスト)、`main.py` (Cloud Functions SDK デコレータ層 → デプロイ後 curl 疎通)
- **追加コミット 6 本** (4-30 → 5-16 で 7 ヶ月ぶり、論理単位で分割):
  ```
  3cad119 chore(ops): wire Functions, deploy script, alerting & acceptance docs
  3adecdf feat(scheduler): idempotent daily-report runner + cleanup + structured logs
  3239d98 feat(notify): LINE/SMTP notifiers with 30s/2m/8m retries (§6.2-6.4)
  f80365d feat(report): assignee-grouped daily report builder (§6.1)
  e641ec0 feat(extraction): Anthropic LLM client, PII masking, ToDo extraction (§5)
  db6fc7d feat(line): LINE Profile API resolver with Firestore-backed cache (§4.3)
  ```
- **`/opsx:archive` はまだ呼ばない**: §10.1/§10.2 が未消化なので change を closed にするのは早い。実環境ドッグフード完走後

### 今回追加されたモジュール (5/16 セッション)

| ファイル | 役割 | spec § |
|---|---|---|
| `functions/src/todobot/line_profile.py` | LINE Profile API resolver + TTL'd `users/` キャッシュ + graceful fallback | §4.3 |
| `functions/src/todobot/llm.py` | `LLMClient` protocol + Anthropic 実装、プロンプトキャッシュ対応 | §5.1 |
| `functions/src/todobot/pii.py` | email / phone / Luhn 検証付き CC マスキング | §5.4 |
| `functions/src/todobot/extraction.py` | system prompt + 5 few-shots + `record_todos` tool + mention boost 付き担当者解決 | §5.2/§5.3 |
| `functions/src/todobot/report.py` | 担当者 group / due 昇順 / 「未割当」末尾 / 低 confidence ⚠️ バッジ / LINE 5000 字分割 / メール multipart text+HTML | §6.1 |
| `functions/src/todobot/notify.py` | `LineNotifier` chunking + `SMTPNotifier` 受信者ごと封筒 + 30s/2m/8m 指数バックオフ | §6.2-§6.4 |
| `functions/src/todobot/scheduler.py` | `DailyReportRunner` (冪等 / 部分失敗対応) + `ScheduledRunner` ±7min 窓 | §6.4-§6.5/§7.1 |
| `functions/src/todobot/cleanup.py` | TTL 30 日の belt-and-braces 削除 | §7.2 |
| `functions/src/todobot/observability.py` | JSON Cloud Logging + contextvar log fields + `RunMetrics` | §8.1 |
| `functions/main.py` | 4 Cloud Functions 結線 (`line_webhook` / `daily_report_scheduled` / `daily_report_trigger` 共有秘密チェック付き / `cleanup_scheduled`) | — |
| `scripts/deploy.sh`, `scripts/smoke_smtp.py` | デプロイスクリプト + SMTP 疎通スモーク | §9.1/§9.2 |
| `docs/operations/{alerting,deploy,acceptance}.md` | アラート設計 / デプロイ手順 / §10.1-§10.2 ドッグフード runbook | §8.2/§9.1/§10 |

### 設計判断の要点 (5/16 実装で固めた)

- **`build_report` 出力構造** (`report.py`): LINE は 1 グループ宛 `pushMessage`、ヘッダ `📋 {date} の本日のToDo (N件)`、担当者ごとに `👤 名前 (件数)` セクション → 期限昇順 → `[mm/dd HH:MM] タスク` → `↳ HH:MM 元発言抜粋` (80 字 trim)。担当者 sort は **既知名 表示名順 → 「未割当」最後**。低 confidence (< 0.5) は `⚠️ 要確認` + セクション見出しに `⚠️`
- **メール**: `email_to` の各エントリに 1 通ずつ、From は `profile.email_from`、Subject `[ToDoBot] {date} {profile} ToDo N件`、multipart/alternative (text + HTML 両出し)、HTML はユーザ入力を `html.escape` で XSS 防止
- **0 件の日**: `skip_empty=false` で「本日のToDoはありませんでした。」単行、`skip_empty=true` で送信丸ごとスキップ
- **§5 抽出方針**: Anthropic `claude-haiku-4-5` 既定、tools ベース構造化出力 (`record_todos` tool)、プロンプトキャッシュ (system + few-shot 5 件 ~3,500 tok を 1 日 1 回 write)、担当者解決は `@mentions` を最優先 (=mention boost)、PII マスキング (`pii.py`) は LLM 投入前に email/phone/CC を `[EMAIL]`/`[PHONE]`/`[CC]` に置換

### 次の動き

1. **§10.1 — 実機ドッグフード** (24h): 本番 LINE channel に Bot を招待 → 実会話 1 日分を流して `daily_report_trigger` を curl で叩いて結果検証 → runbook ([docs/operations/acceptance.md](https://github.com/meguruit/ToDoBot/blob/main/docs/operations/acceptance.md)) のチェックボックスを順次埋める
2. **§10.2 — 受入チェックリスト**: 同 runbook 内、コスト計測 (Anthropic / LINE push / SMTP / Firestore reads) と SLA 観測 (push success rate / mail bounce / extraction confidence 分布) を 24h 取得
3. **B1 — Workspace SMTP 管理者承認**: user 側継続 (1〜3 営業日)、承認後 `secrets:set SMTP_*` で本番投入

### コミット履歴 (2026-04-29 → 2026-05-16、main 直 commit)

```
3cad119 chore(ops): wire Functions, deploy script, alerting & acceptance docs   # 5-16 push to meguruit/ToDoBot
3adecdf feat(scheduler): idempotent daily-report runner + cleanup + structured logs
3239d98 feat(notify): LINE/SMTP notifiers with 30s/2m/8m retries (§6.2-6.4)
f80365d feat(report): assignee-grouped daily report builder (§6.1)
e641ec0 feat(extraction): Anthropic LLM client, PII masking, ToDo extraction (§5)
db6fc7d feat(line): LINE Profile API resolver with Firestore-backed cache (§4.3)
c7556f9 docs(ops): LINE and GWS SMTP credential references for maintenance   # 4-30 07:49 JST
710cb9b docs(setup): external service preparation checklists (B1-B4)         # 4-29 12:18 JST
dac0875 feat(webhook): LINE webhook handler with mention/reply capture (§4)  # 4-29 12:15 JST
106f9fd feat(data): models and Firestore repository (§3)                     # 4-29 12:10 JST
2b22b35 feat(config): implement profile loader and Settings (§2)             # 4-29 12:00 JST
8b98f60 chore: scaffold OpenSpec proposal and Firebase Functions skeleton    # 4-29 11:46 JST (root)
```

(5/11 時点で「次は §5」「remote 未設定 / push なし」だった状態から、5/16 1 セッションで §5-§10 を完走 + push まで到達。)

## ステータス (2026-05-11 時点) — §5 着手前 (履歴保存)

### コミット履歴 (main 直 commit、push なし)

### tasks.md 進捗 (10 sections × 19.0 人日見積、本稿時点で 5 章完了)

| § | 内容 | 状態 | 工数 |
|---|---|---|---|
| 1 | プロジェクト初期化 | ✅ done (`8b98f60`) | 1.5d |
| 2 | 設定／プロファイル | ✅ done (`2b22b35`、tests 29 件) | 1.5d |
| 3 | データ層 (Firestore) | ✅ done (`106f9fd`、tests 11 件) | 2.0d |
| 4 | LINE Webhook 受信 | ✅ done (`dac0875`、tests 14 件) | 2.5d |
| 5 | ToDo 抽出 (LLM) | ⬜ next | 4.0d |
| 6 | 日次レポート配信 | ⬜ | 3.0d |
| 7 | Scheduled Functions 起動口 | ⬜ | 1.0d |
| 8 | 観測・運用 | ⬜ | 1.0d |
| 9 | Firebase デプロイ | ⬜ | 1.5d |
| 10 | 動作確認 | ⬜ | 1.5d |
| B1-B4 | 外部サービス準備 | ✅ docs 揃え (`710cb9b`) | 並行 |
| Ops | 運用ドキュメント | ✅ done (`c7556f9`) | 並行 |

合計 54 tests pass (`pytest` / `ruff` / `black --check` / `mypy --strict` 全クリア)。

### 主要モジュール

- [functions/src/todobot/config.py](https://github.com/tatoflam/ToDoBot/blob/main/functions/src/todobot/config.py) — `ProfilesFile` / `Settings` (pydantic-settings)、`HH:MM` 正規表現 + `zoneinfo.ZoneInfo` + `EmailStr` + `active_profiles` ⊆ `profiles` の `model_validator`
- [functions/src/todobot/models.py](https://github.com/tatoflam/ToDoBot/blob/main/functions/src/todobot/models.py) — `RawMessage` (mentions / quoted_message_id) / `UserCache` / `Todo` (0-1 信頼度 + source 非空) / `ReportRun`
- [functions/src/todobot/firestore_repo.py](https://github.com/tatoflam/ToDoBot/blob/main/functions/src/todobot/firestore_repo.py) — 4 コレクション facade、`try_acquire_report_run` トランザクション冪等、TTL 30 日
- [functions/src/todobot/line_handler.py](https://github.com/tatoflam/ToDoBot/blob/main/functions/src/todobot/line_handler.py) — `WebhookParser` 署名検証、group/room の text のみ保存、`UserMentionee` / `AllMentionee` / `quoted_message_id` 捕捉
- [functions/main.py](https://github.com/tatoflam/ToDoBot/blob/main/functions/main.py) — `@cache` で cold-start 後 handler 再利用、`InvalidSignatureError`→403

## ドキュメント構成 (二層、4-30 07:49 JST 確立)

| 役割 | パス | 方向性 |
|---|---|---|
| 初回セットアップ | `docs/external-setup/` | 「何もない状態から作る」手順書 (B1=Workspace SMTP / B2=LINE Developers / B3=Anthropic / B4=Firebase) |
| 運用中の参照 | `docs/operations/` | 「動いている状態を確認・更新する」リファレンス + 全シークレット所在マップ表 + ローテーション手順 + トラブルシュート |

意図: 3〜6 ヶ月後に「アプリパスワードどこで更新するんだっけ？」を探すコストを抑える。両層から相互リンクを張り、`docs/external-setup/README.md` から `docs/operations/` への循環参照を整備。

### 運用ドキュメント要点

- **`docs/operations/README.md`** — 全シークレット所在マップ (一次保管=コンソール / 二次保管=Firebase Secrets / コード参照箇所 / 推奨ローテーション頻度)、`assert_runtime_secrets_present()` で早期発見
- **`docs/operations/line-credentials.md`** — Channel ID / secret / access token / Webhook URL / Bot user ID / Bot LINE ID のインベントリ、OA Manager「グループ参加 ON」見落としポイント、ローテーション (secret 即失効 / access token 24h 猶予 / 再デプロイ必須)、トラブルシュート (`invalid signature` / push 401 / 月 200 通超過 / 招待不可 / Verify timeout)
- **`docs/operations/gws-smtp.md`** — SMTP host/port / Bot ユーザー / アプリパスワード / SPF/DKIM/DMARC、管理コンソールパス、ローテーション (アプリパスワード差替 / Bot メアド変更 / テナント移行)、動作確認 (ローカル `smtplib` / 本番 `daily_report_trigger` / Gmail ログイベント監査)、Gmail API + Domain-wide Delegation 代替との比較表

## 採用スタック (要約)

- **ランタイム**: Cloud Functions for Firebase 2nd gen (Python 3.10、Firebase Functions Python SDK)
- **DB**: Firestore (TTL 30 日、scheduled function で集計)
- **スケジューラ**: Scheduled Functions (Cloud Scheduler 不要)
- **LLM**: Anthropic Claude (既定 `claude-haiku-4-5`、必要時 `claude-sonnet-4-6`) + プロンプトキャッシュ + tools ベース構造化出力
- **メール**: Google Workspace SMTP Relay (`smtp-relay.gmail.com:587`、Notifier 抽象で Gmail API 切替可)
- **LINE**: Messaging API (webhook → Bot push、group/room の text のみ収集)

詳細・運用コスト試算 (3 グループ × 150 msg/日 = 月 約 ¥320 中央値) は [[05_learn/todobot-line-mvp]]。

## 環境セットアップの罠 (4-29 ハマりポイント)

- **`.python-version=3.11` 指定 → pyenv に未インストール**で `python3.11 not found` → `.python-version` を `3.10.11` に書き換え (system に既にインストール済) で対応。pyenv install せず既存版に揃える判断
- **`firebase-functions` SDK の型 stub が `sync/async` ユニオン** → `mypy --strict` で部分的 `# type: ignore`。`get_user` / `get_message` 両方で同じスタイルに揃える
- **`ruff` UP037 + I001 → auto-fix 一発、`black` 再整形 1 ファイル**

## 残課題 (Open Questions)

- **OQ5**: SMTP Relay の許可 IP / VPC Connector 要否 (Workspace 管理者ヒアリング待ち)
- **OQ6**: Anthropic 残データ取扱と Workspace データ持出ポリシーの整合 (社内法務確認)

## 次の動き

- §5 ToDo 抽出 (LLM) 着手 — Claude Haiku 4.5 + tools/JSON schema、プロンプトキャッシュ (system + few-shot ~3,500 tok を 1 日 1 回 write)、PII マスキング
- 並行で B1 (Workspace 管理者承認、1〜3 営業日リードタイム) を user 側で進捗

## Links

- [[05_learn/todobot-line-mvp]] — 設計・運用コスト・spec 一覧 (planning 起点)
- [[02_diary/2026-04-28]] — 初日: ユースケース定義 + Plan B 棄却 + Firebase 一本化
- [[02_diary/2026-04-29]] — 実装 §2-§4 + B1-B4 docs
- [[02_diary/2026-04-30]] — 運用ドキュメント二層化
- [[02_diary/2026-05-16]] — §5-§10 完走 + 6 commits 分割 + meguruit/ToDoBot へ push
