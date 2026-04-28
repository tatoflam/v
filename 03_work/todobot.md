---
title: ToDoBot (line-todo-bot-mvp)
category: 03_work
tags: [project:todobot, tech:python, tech:firebase, tech:firestore, tech:line, tech:anthropic, tech:openspec, stage:planning]
sources: [2648ee43-ade1-4be4-b64a-b31c9d21bfb3]
updated: 2026-04-28
---

# ToDoBot (line-todo-bot-mvp)

## Summary

LINE グループに常駐する Bot が業務会話を収集し、1 日 1 回 LLM で「誰がいつまでに何を」抽出して毎日 20:00JST（プロファイル可変）に **LINE push と メール**で配信する MVP。OpenSpec ワークフローで `proposal / design / tasks / specs` を一括起票（`openspec validate` 通過）、`docs/line-todo-bot-mvp-report.md` にレポート化。リポジトリ: `~/repo/github/tatoflam/ToDoBot`（GitHub push はまだ）。

## 採用スタック（design.md）

| レイヤ | 採用 | 不採用と理由 |
|---|---|---|
| 言語 | Python 3.11 | LINE SDK / Anthropic SDK の親和性 |
| 実行基盤 | **Firebase Cloud Functions for Firebase 2nd gen** | Cloud Run + Cloud Scheduler（運用統合の薄さ） |
| データストア | **Firestore (Native mode)** | SQL/Alembic スタック（TTL 自動削除と複合インデックスで Firestore 優位） |
| LLM | **Anthropic Claude**（既定 `claude-haiku-4-5`、必要時 `claude-sonnet-4-6`） | OpenAI（Q001 の指定で Anthropic 固定） |
| メール送信 | **Google Workspace SMTP Relay** (`smtp-relay.gmail.com:587`、STARTTLS + SMTP AUTH) | Gmail API + Domain-wide Delegation（Notifier 抽象で差替え可能） |
| スケジューラ | Firebase Scheduled Functions（15 分間隔起動 → `report_time ±7 分`のプロファイルを処理） | Cloud Scheduler 単独 |
| 設定 | YAML (`config/profiles.yaml`) + `ACTIVE_PROFILES` 環境変数、シークレットは Firebase Secret Manager | dotenv only |

## Capabilities（4 本）

| Capability | 主要要件 |
|---|---|
| `line-bot-ingestion` | Webhook 受信（5 秒以内 200 応答）／署名検証必須／グループのテキスト発言のみ保存／非テキスト・1on1 は無視／displayName キャッシュ |
| `todo-extraction` | 日次バッチで構造化 ToDo（`assignee/task/due/confidence/source_message_ids`）抽出／担当者の名寄せ／PII マスキング／生メッセージ 30 日保持 |
| `daily-report` | プロファイル毎の定時配信／LINE push + メール／低 confidence 表示／指数バックオフ再送（30s/2m/8m）／`report_runs` で冪等／空日スキップ可 |
| `notification-profiles` | YAML 定義／`ACTIVE_PROFILES` で切替／シークレット分離／起動時バリデーション（HH:MM, IANA TZ, 空配列禁止） |

## 解決済 Q&A（design.md §D4-D7）

- **Q001 LLM**: Anthropic Claude（haiku-4-5 既定／sonnet-4-6 へプロファイル昇格可）。`tools` ベース構造化出力 + プロンプトキャッシュ前提
- **Q002 メール**: GWS SMTP Relay。Notifier 抽象で Gmail API へ差替え可能
- **Q003 Firebase**: 採用。Functions + Firestore + Scheduled Functions で運用統合
- **Q004 抽出範囲**: 全グループメッセージ＋Bot メンション付き発言は重み付けで優先

## 未解決 Open Questions（実装着手時に確認）

- **OQ5**: GWS SMTP Relay の許可 IP 制限と Cloud Functions の Egress IP 整合（Static IP / VPC Connector の要否） — Workspace 管理者確認
- **OQ6**: Anthropic API の残データ取扱と Workspace 側持出ポリシーの整合 — 法務／コンプラ確認

## 工数見積（≈ 23.0 人日）

旧スタック（Cloud Run + SQLAlchemy + Alembic + Cloud Scheduler）想定から **Firebase 寄せ**で約 -2 人日。不確実性ホットスポット: `todo-extraction` のプロンプト調整（confidence 安定化）、`line-bot-ingestion` の displayName 名寄せ。詳細内訳は `docs/line-todo-bot-mvp-report.md` §4。

## 運用コスト試算（3 グループ × 150 msg/日 × 90 抽出呼出/月）

- **Anthropic Claude Haiku 4.5 + プロンプトキャッシュ**: 入力 ~17,500 tok / 出力 ~1,500 tok / 1 抽出 → **≈ $2.10/月**
- **Firebase 無料枠** (Functions 200 万呼出 + Firestore 5 GB) で MVP 想定トラフィックは収まる見込み
- 詳細試算は `docs/line-todo-bot-mvp-report.md` §9

## 関連リポジトリ・OpenSpec 成果物

- リポジトリ: `~/repo/github/tatoflam/ToDoBot`（GitHub push 未実施）
- OpenSpec change: `openspec/changes/line-todo-bot-mvp/`
  - `proposal.md` / `design.md` / `tasks.md`
  - specs: `line-bot-ingestion` / `todo-extraction` / `daily-report` / `notification-profiles`
- レポート: `docs/line-todo-bot-mvp-report.md`

## Links

- [[05_learn/specdrawing-material-presenter]] — 同じ OpenSpec ワークフローを採用した先行プロジェクト
- [[02_diary/2026-04-28]]
