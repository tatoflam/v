---
title: ToDoBot — LINE 業務会話 → 日次 ToDo レポート
category: 03_work
tags: [project:todobot, tech:python, tech:firebase, tech:firestore, tech:line-messaging-api, tech:anthropic-claude, tech:google-workspace, tech:openspec, stage:active]
sources: [2648ee43-ade1-4be4-b64a-b31c9d21bfb3]
updated: 2026-05-11
---

# ToDoBot

## Summary

LINE グループに常駐する Bot が業務会話を受信し、1 日 1 回 LLM (Claude Haiku/Sonnet) で「誰が・いつまでに・何を」を構造化抽出、指定時刻 (既定 20:00 JST、プロファイル可変) に LINE push とメールで配信する個人事業向けの自動化。リポ: [tatoflam/ToDoBot](https://github.com/tatoflam/ToDoBot) (private、2026-04-29 root-commit `8b98f60`)。

OpenSpec workflow で proposal / design / specs / tasks 一式起票、change 名 `line-todo-bot-mvp`。設計詳細・運用コスト試算・spec 一覧は [[05_learn/todobot-line-mvp]] を参照。

## ステータス (2026-05-11 時点)

### コミット履歴 (main 直 commit、push なし)

```
c7556f9 docs(ops): LINE and GWS SMTP credential references for maintenance   # 4-30 07:49 JST
710cb9b docs(setup): external service preparation checklists (B1-B4)         # 4-29 12:18 JST
dac0875 feat(webhook): LINE webhook handler with mention/reply capture (§4)  # 4-29 12:15 JST
106f9fd feat(data): models and Firestore repository (§3)                     # 4-29 12:10 JST
2b22b35 feat(config): implement profile loader and Settings (§2)             # 4-29 12:00 JST
8b98f60 chore: scaffold OpenSpec proposal and Firebase Functions skeleton    # 4-29 11:46 JST (root)
```

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
