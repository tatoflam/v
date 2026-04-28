---
title: ToDoBot — LINE グループ業務会話 → 日次 ToDo レポート MVP
category: 05_learn
tags: [topic:todobot, project:todobot, tech:openspec, tech:python, tech:firebase, tech:firestore, tech:line-messaging-api, tech:anthropic-claude, tech:google-workspace, stage:proposed]
sources: [2648ee43-ade1-4be4-b64a-b31c9d21bfb3]
updated: 2026-04-29
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
| メール送信 | **Google Workspace SMTP Relay**（`smtp-relay.gmail.com:587`、SMTP AUTH + アプリパスワード）。代替: Gmail API + Domain-wide Delegation。Notifier 抽象で吸収 |
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
- **OQ5**: SMTP Relay の許可 IP / VPC Connector 要否（Workspace 管理者ヒアリング待ち）
- **OQ6**: Anthropic 残データ取扱と Workspace データ持出ポリシーの整合（社内法務確認）

## Links

- [[02_diary/2026-04-28]]
- [[05_learn/wiki-automation-pipeline]] — OpenSpec ワークフロー
- [[05_learn/specdrawing-material-presenter]] — 同じく OpenSpec 駆動の MVP 事例
