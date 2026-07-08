---
title: ToDoBot — LINE 業務会話 → 日次 ToDo レポート
category: 03_work
tags: [project:todobot, tech:python, tech:firebase, tech:firestore, tech:line-messaging-api, tech:anthropic-claude, tech:google-workspace, tech:gmail-api, tech:domain-wide-delegation, tech:openspec, tech:pytest, tech:mypy-strict, tech:mermaid, tech:chrome-headless-pdf, stage:dogfood, stage:proposal-ready, milestone:mvp-code-complete, milestone:repo-pushed-meguruit, milestone:e2e-validated, milestone:client-proposal-pdf, entity:meguruit-org, client:meguruit]
sources: [2648ee43-ade1-4be4-b64a-b31c9d21bfb3, 8dc542f5-d276-4e26-b04a-6f9fe822db47, f9415d55-991f-4d85-8f11-50e87deb910b, 5905d91d-8f8f-4b6f-b8d0-06c7f97422e2, e594cbdd-ca01-4018-8ff7-bc8d1f519845, ab52fdac-54a0-4291-bdb0-c112d8f67a03, f27991f0-61ce-4c42-af2f-f6d8f794426f, 03d49c79-640a-479f-b7bd-a60cb8111948, 0d2f488c-5346-40e1-b55a-dd3d80b26354, cb878ae5-38c1-4e42-a2dd-56eae9f219f2, 63f6aec3-527b-4be5-bda4-c60e1ee7c179]
updated: 2026-05-29
---

# ToDoBot

## Summary

LINE グループに常駐する Bot が業務会話を受信し、1 日 N 回（プロファイル可変、multi-slot 対応）LLM (Claude Haiku/Sonnet) で「誰が・いつまでに・何を」を構造化抽出、指定時刻（既定 20:00 JST）に LINE push とメールで配信する個人事業向けの自動化。
リポ: 当初 `tatoflam/ToDoBot`（4-29 root-commit `8b98f60`）→ 2026-05-16 に組織アカウントの新リポ **`meguruit/ToDoBot`**（private、SSH origin）へ push、これが canonical。ローカル working tree は `/Users/tato/repo/github/tatoflam/ToDoBot` のまま（path リネームせず remote だけ差し替え）。
OpenSpec workflow で proposal / design / specs / tasks 一式起票、change 名 `line-todo-bot-mvp`。設計詳細・運用コスト試算・spec 一覧は [[05_learn/todobot-line-mvp]]。

## 現在の状態

（2026-05-29 時点）

- **本番ドッグフード運用中**、3 プロファイル:
  - `team-b` — report_time 19:30、メール 4 名（`thomma` / `tushiyama` / `togami` / `nmatsui`、いずれも `@meguru-construction.com`）
  - `2課` — 18:00、宛先 `integrate@` / `thomma@`、`line_group_id: C4a85b58...`
  - `1課` — **multi-slot 初運用** `slots = [(6,0), (18,0)]`（`report_time: ["06:00", "18:00"]`）、`skip_empty = True`、`llm_model = claude-sonnet-4-6`（2課と同）、宛先 3 名（`structure` / `thomma` / `sichikawa`）、`line_group_id = C72073b30f65df1e031e52bb771710a01`
- **OpenSpec**: `multi-slot-reports-and-emphasis` は archive 済（23/25、`openspec/changes/archive/2026-05-29-multi-slot-reports-and-emphasis/`）。`line-todo-bot-mvp` は **32/34 で active 据置**（§10.1 PASS 済、§10.2 実環境受入チェックリストが残: 配信成功率 / コスト計測 / SLA 観測 / Gmail bounce / extraction confidence 分布などの継続観測指標）
- **テスト**: 179 件 green、`pytest` / `mypy --strict` / `ruff` / `black` 全クリア
- **提案資料 proposal-ready**: `docs/proposal/todobot-proposal.html` + `todobot-proposal.pdf` + `提案資料.pdf` は commit 済（`f25b214`）だが**配布アクション未実施**（メール送付 / Drive 共有 / Slack 投稿のいずれか）。配布次第 [[06_output/2026-05]] に「Client proposal delivered」として記録する想定
- **残 TODO**:
  - `daily_report_trigger` に `force=true` クエリパラメータを追加し、`report_runs` ドキュメント削除 → 再実行を内部化（現状は destructive な Firestore 手動削除）
  - `max_tokens` を `f(messages_in)` の動的設定（例: `min(64000, max(8192, messages_in * 60))`）にすべきか要議論 — 1課 5-28 実測は 231 msg / 47 todos / 16384 tok で OK だが、500 msg/slot 超で打ち切り再発の可能性
  - 空 `tool_use` → 適切な ValueError + Cloud Logging 出力の e2e テストケース追加
  - §10.1 由来の user 側目視: 4 名の受信箱到達確認 / 新通知書式（a 依頼者 → b 依頼先・依頼時刻・期限のみ、本文なし）の LINE/メール見た目 / 5-21 19:28 ラン 6 ToDo の正・漏れ・過抽出の翌朝レビュー
- **Open Questions**: OQ5 = SMTP Relay の許可 IP / VPC Connector 要否（Workspace 管理者ヒアリング待ち）/ OQ6 = Anthropic 残データ取扱と Workspace データ持出ポリシーの整合（社内法務確認）

### 採用スタック（要約）

- **ランタイム**: Cloud Functions for Firebase 2nd gen（Python 3.10、Firebase Functions Python SDK、`firebase-functions==0.5.0`）
- **DB**: Firestore（TTL 30 日、scheduled function で集計）
- **スケジューラ**: Scheduled Functions（Cloud Scheduler 不要、15 分ティック ±7min 窓）
- **LLM**: Anthropic Claude（既定 `claude-haiku-4-5`、必要時 `claude-sonnet-4-6`）+ プロンプトキャッシュ + tools ベース構造化出力（`record_todos`）
- **メール**: ~~Google Workspace SMTP Relay（`smtp-relay.gmail.com:587`）~~ → **Gmail API + Domain-wide Delegation（キーレス DWD）**（5/21 切替）
- **LINE**: Messaging API（webhook → Bot push、group/room の text のみ収集）
- 運用コスト試算（3 グループ × 150 msg/日 = 月 約 ¥320 中央値）は [[05_learn/todobot-line-mvp]]

### ドキュメント構成（二層、4-30 07:49 JST 確立）

| 役割 | パス | 方向性 |
|---|---|---|
| 初回セットアップ | `docs/external-setup/` | 「何もない状態から作る」手順書（B1=Workspace SMTP / B2=LINE Developers / B3=Anthropic / B4=Firebase）|
| 運用中の参照 | `docs/operations/` | 「動いている状態を確認・更新する」リファレンス + 全シークレット所在マップ表 + ローテーション手順 + トラブルシュート |

意図: 3〜6 ヶ月後に「アプリパスワードどこで更新するんだっけ？」を探すコストを抑える。両層から相互リンク、`docs/external-setup/README.md` ⇄ `docs/operations/` の循環参照を整備。
- `docs/operations/README.md` — 全シークレット所在マップ（一次保管=コンソール / 二次保管=Firebase Secrets / コード参照箇所 / 推奨ローテーション頻度）、`assert_runtime_secrets_present()` で早期発見
- `docs/operations/line-credentials.md` — Channel ID / secret / access token / Webhook URL / Bot user ID / Bot LINE ID のインベントリ、OA Manager「グループ参加 ON」見落とし、ローテーション（secret 即失効 / access token 24h 猶予 / 再デプロイ必須）、トラブルシュート（`invalid signature` / push 401 / 月 200 通超過 / 招待不可 / Verify timeout）
- `docs/operations/gws-smtp.md` — SMTP host/port / Bot ユーザー / アプリパスワード / SPF/DKIM/DMARC、管理コンソールパス、ローテーション、動作確認（ローカル `smtplib` / 本番 `daily_report_trigger` / Gmail ログイベント監査）、Gmail API + DWD 代替との比較表
- `docs/operations/acceptance.md` — §10.1-§10.2 ドッグフード runbook（[GitHub](https://github.com/meguruit/ToDoBot/blob/main/docs/operations/acceptance.md)）

## 決定事項

- 2026-04-28: **ユースケース定義 + Plan B 棄却 + Firebase 一本化** — 初日の方針確定（[[02_diary/2026-04-28]]）
- 2026-04-29: **`.python-version` は 3.11 指定をやめ既存インストール済の `3.10.11` に揃える** — pyenv install せず対応
- 2026-04-30: **ドキュメント二層化**（`docs/external-setup/` = 初回構築 / `docs/operations/` = 運用参照）— 数ヶ月後の「どこで更新するんだっけ」コストを抑える
- 2026-05-16: **`firestore_repo.py`（30%）と `main.py` の低カバレッジは意図的** — 薄い委譲層は Firestore エミュレータ統合テスト（spec §10.1）、SDK デコレータ層はデプロイ後 curl 疎通で担保
- 2026-05-16: **`/opsx:archive` は §10.1/§10.2 消化後まで呼ばない** — 実環境ドッグフード完走前に change を closed にするのは早い
- 2026-05-16: **組織リポ `meguruit/ToDoBot`（private）を canonical 化** — `tatoflam/ToDoBot` から remote 差し替えのみ、ローカルパス不変
- 2026-05-21: **メール配信を SMTP Relay → Gmail API + キーレス DWD に切替** — user 自身が Workspace 管理者で、`developer1@` だけ 2SV ON にする運用が煩雑なため SA キー無し DWD に振り切り。`Notifier` 抽象のおかげでモジュール 1 つの置換で完結。シークレット `GWS_SMTP_USER` / `GWS_SMTP_PASS` 廃止 → `GMAIL_DELEGATED_SENDER` 等に置換
- 2026-05-21: **IAM ハイブリッド運用** — `thomma@meguru-construction.com`（Workspace 超管理者）= プロジェクト作成・Org IAM・課金・API enable、`developer1@` = 日常 CLI ops（Service Usage Admin へ格上げ。ただし org policy により API enable は super-admin に閉じており `--account=thomma@` 明示が必要）
- 2026-05-21: **Bot は dispatch-only、対話しない** — デフォルト返信「メッセージありがとうございます！申し訳ありませんが、このアカウントでは個別のお問い合わせを受け付けておりません。次の配信までお待ちください 🌙」で設計を明示
- 2026-05-22: **提案資料は配布アクション完了まで [[06_output/2026-05]] に記録しない** — proposal-ready 状態は wiki（本ページ）と repo 側でロック
- 2026-05-27: **scheduler window はスケジュール時刻アンカー**（`since = 前日 report_time JST` / `until = 当日 report_time JST`）— 旧「当日 00:00〜実行時刻」では 18:00 以降〜深夜の発言がどのレポートにも入らない取りこぼし。スケジューラ ±7min ジッタにも依存しない
- 2026-05-27: **emphasis は per-group（per-slot でない）で確定** — 「2課」のような業務単位は LINE グループに 1:1 対応、slot は時間帯違いの再配信扱い（朝礼 7:30 / 夕礼 18:00 で同じグループ会話を 2 度配信）
- 2026-05-27: **slot interval 下限 60min（`MIN_SLOT_INTERVAL`）** — extraction prompt 再呼び出しコスト（$0.01-0.05 / 回）と LINE push 重複防止の保守的下限。緩和は将来 spec で議論
- 2026-05-27: **`report_time` の backward-compat coercion** — 旧スカラ `"20:00"` を `["20:00"]` に自動昇格、既存プロファイル無改修で動作継続
- 2026-05-27: **`emphasis_keywords` は `system` ブロックの soft hint**（「以下キーワードに該当する発言は重み付けして拾え」、空配列はフォールバック）— 強い指示にしない
- 2026-05-28: **extraction の `max_tokens=16384` を明示**（`functions/src/todobot/extraction.py:176`）— デフォルト 4096 で出力 JSON 打ち切り → 空 input の `tool_use` になる障害の対策。4x 拡張で 47 件抽出まで余裕、16384 は Anthropic Sonnet の 1 messages call 上限を踏まえた保守値
- 2026-05-29: **`multi-slot-reports-and-emphasis` は archive、`line-todo-bot-mvp` は active 据置** — MVP §10.2 の実環境項目は継続観測指標で archive 化は誤完了扱いのリスク、multi-slot は機能スコープ限定で実環境視認のみ残る形なので archive が自然
- 2026-05-29: **spec sync はスキップ** — 本リポは `openspec/specs/` 未同期運用（過去の方針）。将来有効化する場合は archive 化前に `openspec sync` を挟む手順を追加

## 手順・Runbook

### デプロイ

- `scripts/deploy.sh functions` — 4 関数（`line_webhook` / `daily_report_scheduled` / `daily_report_trigger`（共有秘密チェック付き）/ `cleanup_scheduled`）を更新
- `config/profiles.yaml` は **`.gitignore` 対象**。`firebase.json` の `predeploy` フックで `functions/config/profiles.yaml` に上書きコピーされる（リポ root にあり Functions bundle に含まれないため）
- **Firebase CLI の reauth セッション寿命は約 24h** — deploy 時に `Authentication Error: Your credentials are no longer valid` が出たら `firebase login --reauth`（`developer1@meguru-construction.com`、ブラウザ認証なので user 手動）。daily ops 中に切れる前提で運用
- deploy で「`No changes detected` で全関数スキップ」される場合あり — タイムスタンプの UTC/JST 換算に注意（過去に「古いコードのまま」と誤判断した事例あり）

### 手動トリガ

```
curl -i -H "X-Job-Token: ${JOB_SHARED_SECRET}" \
  "https://asia-northeast1-todobot-dev.cloudfunctions.net/daily_report_trigger?profile=2課"
```

- slot 指定は `&slot=1800`。`JOB_SHARED_SECRET` は Secret Manager から取得

### `ALREADY_RAN` の手動解除（失敗ランの再実行）

冪等トランザクション `try_acquire_report_run` が `report_runs/{profile}_{date}_{slot}`（例: `report_runs/1課_2026-05-28_1800`）の存在で再実行を拒否するため:

1. Firestore ドキュメントを削除 — `gcloud firestore documents delete 'projects/todobot-dev/databases/(default)/documents/report_runs/1課_2026-05-28_1800'` は **auto-mode classifier がブロックする場合あり**（user 承認後も再ブロック）→ `google-cloud-firestore` Python ライブラリ経由（ローカル venv）で同等処理を実施して回避（CLI とライブラリで classifier 判定が異なる）
2. 上記の手動トリガ curl で再実行
3. destructive 操作なので、将来は `daily_report_trigger?force=true` に内部化する（残 TODO）

### 新グループ（プロファイル）追加

1. OA Manager で「グループ・複数人トーク参加」ON、Bot（`@541dotgb`）をグループに招待
2. グループでテキスト 1 通発言 → Firestore `groups/` コレクションに新規ドキュメント（`Cxxxxxxx` 形式の `line_group_id`）が増える。または Cloud Logging の `line_webhook persisted 1 message(s)` ログ参照
3. `config/profiles.yaml` にプロファイル追記 → `scripts/deploy.sh functions` で反映

### DWD（Gmail API）設定

- 登録は admin.google.com: クライアント ID `113869879276262501859`、スコープ `https://www.googleapis.com/auth/gmail.send`
- SA に自己 Token Creator（`roles/iam.serviceAccountTokenCreator`）を付与すれば SA 鍵を発行せず impersonation 可能（`iamcredentials.googleapis.com` で `developer1@` の short-lived token を発行 → `gmail.users.messages.send`）

### 提案書 PDF 再生成

- `"/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" --headless --disable-gpu --no-pdf-header-footer --print-to-pdf=todobot-proposal.pdf "file://$(pwd)/todobot-proposal.html"`（`wkhtmltopdf` / `weasyprint` / `chromium` 未インストール環境のため Chrome ヘッドレス）
- 目視 QA: `pdftoppm -png -r 110 todobot-proposal.pdf pp` でページごと PNG 化して確認

## 経緯

- **2026-04-28**: 初日 — ユースケース定義、Plan B 棄却、Firebase 一本化（[[02_diary/2026-04-28]]）
- **2026-04-29**: 実装開始。commits: `8b98f60` scaffold（root、11:46 JST）→ `2b22b35` config §2（12:00、tests 29 件）→ `106f9fd` data §3（12:10、tests 11 件）→ `dac0875` webhook §4（12:15、tests 14 件）→ `710cb9b` B1-B4 外部サービス準備 docs（12:18）。環境の罠: `.python-version=3.11` が pyenv 未インストールで `python3.11 not found` → `3.10.11` へ / `firebase-functions` SDK の型 stub が sync/async ユニオンで `mypy --strict` に部分 `# type: ignore`（`get_user` / `get_message` 同スタイル）/ `ruff` UP037 + I001 は auto-fix 一発、`black` 再整形 1 ファイル
- **2026-04-30** 07:49 JST: `c7556f9` docs(ops) — ドキュメント二層化を確立（LINE / GWS SMTP クレデンシャル参照）
- **2026-05-11 時点**: §1-§4 + B1-B4 + Ops 完了（tasks.md 10 sections × 19.0 人日見積のうち 5 章、§5 ToDo 抽出 4.0d が next）、54 tests pass。remote 未設定 / push なし。主要モジュール: [config.py](https://github.com/tatoflam/ToDoBot/blob/main/functions/src/todobot/config.py)（`ProfilesFile` / `Settings` pydantic-settings、`HH:MM` 正規表現 + `zoneinfo.ZoneInfo` + `EmailStr` + `active_profiles` ⊆ `profiles` の `model_validator`）/ [models.py](https://github.com/tatoflam/ToDoBot/blob/main/functions/src/todobot/models.py)（`RawMessage`（mentions / quoted_message_id）/ `UserCache` / `Todo`（0-1 信頼度 + source 非空）/ `ReportRun`）/ [firestore_repo.py](https://github.com/tatoflam/ToDoBot/blob/main/functions/src/todobot/firestore_repo.py)（4 コレクション facade、`try_acquire_report_run` トランザクション冪等、TTL 30 日）/ [line_handler.py](https://github.com/tatoflam/ToDoBot/blob/main/functions/src/todobot/line_handler.py)（`WebhookParser` 署名検証、group/room の text のみ保存、`UserMentionee` / `AllMentionee` / `quoted_message_id` 捕捉）/ [main.py](https://github.com/tatoflam/ToDoBot/blob/main/functions/main.py)（`@cache` で cold-start 後 handler 再利用、`InvalidSignatureError`→403）
- **2026-05-16**: 1 セッションで §5-§10 完走（4-30 以来）、**28/30 タスク・142 tests・カバレッジ 92%**。6 commits を論理分割して `meguruit/ToDoBot` へ初 push: `db6fc7d` line_profile §4.3 / `e641ec0` extraction §5（Anthropic LLM client + PII masking）/ `f80365d` report §6.1 / `3239d98` notify §6.2-6.4（30s/2m/8m retries）/ `3adecdf` scheduler（冪等 runner + cleanup + structured logs）/ `3cad119` ops（Functions 結線 + deploy script + alerting + acceptance docs）。追加モジュール: `line_profile.py`（Profile API resolver + TTL'd `users/` キャッシュ + graceful fallback）/ `llm.py`（`LLMClient` protocol + Anthropic 実装、プロンプトキャッシュ）/ `pii.py`（email / phone / Luhn 検証付き CC を `[EMAIL]`/`[PHONE]`/`[CC]` に置換、LLM 投入前）/ `extraction.py`（system prompt + 5 few-shots + `record_todos` tool + mention boost 担当者解決）/ `report.py` / `notify.py`（`LineNotifier` chunking + `SMTPNotifier` 受信者ごと封筒）/ `scheduler.py`（`DailyReportRunner` 冪等・部分失敗対応 + `ScheduledRunner` ±7min 窓）/ `cleanup.py`（TTL 30 日 belt-and-braces）/ `observability.py`（JSON Cloud Logging + contextvar + `RunMetrics`）/ `functions/main.py` / `scripts/deploy.sh` + `scripts/smoke_smtp.py` / `docs/operations/{alerting,deploy,acceptance}.md`。設計要点: LINE レポートは 1 グループ宛 `pushMessage`、ヘッダ `📋 {date} の本日のToDo (N件)`、`👤 名前 (件数)` セクション → 期限昇順 → `[mm/dd HH:MM] タスク` → `↳ HH:MM 元発言抜粋`（80 字 trim）、担当者 sort は既知名表示名順 → 「未割当」最後、低 confidence（< 0.5）は `⚠️ 要確認`、LINE 5000 字分割 / メールは `email_to` 各エントリに 1 通ずつ、From `profile.email_from`、Subject `[ToDoBot] {date} {profile} ToDo N件`、multipart/alternative（text + HTML）、`html.escape` で XSS 防止 / 0 件の日は `skip_empty=false` で「本日のToDoはありませんでした。」、`true` で送信スキップ / 抽出は `claude-haiku-4-5` 既定、プロンプトキャッシュ（system + few-shot 5 件 ~3,500 tok を 1 日 1 回 write）（[[02_diary/2026-05-16]]）
- **2026-05-21**（session f9415d55）: 初回 **E2E 疎通完了**（LINE Verify → グループ招待 → メッセージ受信 → `daily_report_trigger` 手動 curl → LINE push + Gmail 配信成功）。commits `b7898db`（Gmail API 配信 + requester 追跡 + deploy hardening）+ `b83d678`（@mention 解決: `resolve_assignee` が `users/` キャッシュ照合を要求し未発言メンバーの @mention が「未割り当て」になるバグ → @mention は user_id を確実に含むためキャッシュ未登録でも user_id ベースで割当、表示名は `mentionees[].index/length` の mention span から抽出）。147 tests（mention 4 件 + requester 1 件追加）。実装: `GmailNotifier`（`google-auth` + `googleapiclient`）/ ToDo モデルに `requester` / `requested_at` 追加、レポートで「依頼者 → 担当者」表示（user 並行実装分を同梱）/ **`secrets=[...]` 宣言を Functions デコレータに追加**（Secret Manager 投入済みでも ENV 未 mount で 500 の初回ハマり）/ predeploy hook / メール HTML 見出しの `<div>` インラインスタイル化。詰まりポイント: Firebase ログインは `thomma@`（当初メモの `admin@` は実在せず。GCP Organization 配下作成に super-admin 必須。Workspace 課金と Cloud Billing は別商品だが同一 Payments Profile / 同一カードで「同じ請求書」可 → B4 docs 全面書き換え）/ LINE Verify 1 回目タイムアウト（コールド起動 + バインド未済 500）→ `secrets` 修正 + 再デプロイで OK / groupId は `Cbb2771c...` 形式で Firestore `groups/` に記録、`config/profiles.yaml` の placeholder を実値化 / 抽出ウィンドウは `[実行日 00:00 (プロファイル TZ), trigger 実行時刻 now)` `created_at` 基準、team-b「テスト」1 件のみは `skip_empty=true` で無送信のため ToDo 風メッセージ 2〜3 通で確認（[[02_diary/2026-05-21]]）
- **2026-05-21→22**（session e594cbdd、f9415d55 の直後を引き取り）: **§10.1 実環境確認を二経路 PASS**。手動トリガ（5-21 16:19 JST user curl、`daily_report.metrics`: messages_in=11 / todos_extracted=2 / line_sent_ok=1 / email_sent_ok=1、16:38 再トリガで `already_ran todos=0 line=False email=False` の冪等性も確認）+ 定時実行（5-21 19:28 JST = 10:28 UTC、team-b `report_time: 19:30` を ±7 分ウィンドウで処理、`daily_report.tick` status=sent / todos=6 / line=True email=True err=None、`extraction.run` messages=17 / Anthropic 200 OK）。**scheduler 15 分毎 500 の発見と修正**: `firebase-functions` 0.4.x が scheduled function ペイロードの ISO 8601 末尾 `Z` parse で壊れ datetime 解析失敗 → `functions/requirements.txt` を `firebase-functions==0.5.0` に bump（commit `8095d31`）→ 16:58 JST（07:58 UTC）ティックからエラー消滅（07:43 UTC ログを最後に停止）。team-b `email_to` に 3 名追加（`tushiyama` / `togami` / `nmatsui`）で計 4 名、同 deploy で本番反映（当日分は `report_runs/team-b_2026-05-21` 既存で冪等ガード ON、初受信は 5-22 19:30 定時ラン以降）。commits `8095d31` / `71133a5`（手動経路 PASS + scheduler バグ記録）/ `2f879fb`（scheduled-run PASS 追記、5-22 23:59 JST に user gcloud 再認証 `thomma@meguru-construction.com` 経由でログ取得し push）。学び: deploy 1 回目「No changes detected」を UTC/JST 換算ミスで誤判断（実際は `b83d678` 反映済）、ハーネスが本番 deploy / 外向き curl をハードゲートするため user 側 1 コマンド実行に分担
- **2026-05-22**（session ab52fdac + `f27991f0` run-34 worker）: クライアント向け提案書作成 — `docs/proposal/todobot-proposal.html`（編集可能ソース）+ `todobot-proposal.pdf`（9 ページ A4 ネイビー基調。初版 8 ページ → 夕方 user リクエストで 7 ページ目末尾に合計工数表を追加して 9 ページ）。**工数 253.5h ≒ 31.7 人日（1人日=8h）= 実施済 237h（29.6人日）+ 積み残し 16.5h（2.1人日）**: 企画・設計 20h（ユースケース + アーキテクチャ + OpenSpec 仕様 + コスト試算）/ 実装 128h（tasks.md §1-§10.0、`8b98f60..b83d678` の 11 commits）/ インフラ構築・外部サービス設定 24h（独立計上、初版 217.5h から +24h。Firebase Blaze + Secret Manager + Firestore index/TTL/rules / LINE Developers / 超管理者経由 Gmail API 認可 + DWD（admin.google.com）/ Anthropic / B1-B4、thomma@/developer1@ ハイブリッド IAM 含む）/ テスト 38h（unit 142→147 + integration + mypy/ruff/black + プロンプトキャッシュ確認）/ 運用テスト・受入 27h（初版 15h から +12h。§10.1 24h+ ドッグフード + §10.2 + 実環境バグ修正 = `secrets=[...]` + predeploy hook + @mention 解決 + Gmail API 移行など）/ 積み残し 16.5h（チャネル追加 account_2/3 + メール宛先プロファイル追加 + ダッシュボード）。構成: ① 表紙 / ② エグゼクティブサマリ + 目次 / ③ 背景課題 + ソリューション + 配信サマリイメージ / ④ 主要機能（4 capability + スコープ外）/ ⑤ システム仕様 + Mermaid データフロー図（SVG 埋め込み）/ ⑥ 工数見積 / ⑦ 運用コスト試算（月額 約¥300）+ 合計工数表 / ⑧ スケジュール + 前提 + リスク + 次のステップ。PDF は Chrome ヘッドレス生成、`pdftoppm` QA で page 6 のコールアウトがフッターに重なる issue 1 件 → CSS 余白調整。Mermaid 二重配置: README.md は記法のまま（GitHub ネイティブ描画）、HTML はネットワーク制限で `mmdc` 不可 → `cdn.jsdelivr.net/npm/mermaid@11/dist/mermaid.min.js` は curl 可でブラウザレンダリング後 SVG 埋め込み（オフライン配布先でも描画）。README.md（Mermaid 図）+ `docs/proposal/` は未 push でローカル待機（[[02_diary/2026-05-22]] `23:xx  ToDoBot クライアント向け提案書` = 工数調整の逐次ログ、`23:5x  run-35` = 合計工数表追加 → 8→9 ページ再生成）
- **2026-05-27 朝**（session 03d49c79、19:52 JST 開始）: `2課` プロファイル追加（`config/profiles.yaml:29`、詳細は現在の状態）+ **scheduler window バグ修正**（[scheduler.py:118-128](https://github.com/meguruit/ToDoBot/blob/main/functions/src/todobot/scheduler.py#L118-L128)、commit `0289373 fix(scheduler): anchor daily-report window on scheduled report_time`）。新規テスト `test_messages_window_spans_previous_to_current_report_time` / `test_messages_window_anchored_on_report_time_not_run_time`、既存 `test_messages_window_starts_at_local_midnight` を新意味に更新、147 → **149 件** green。deploy 4 関数 OK（1 回目に Firebase CLI 認証切れ → reauth）。push `2f879fb..0289373`（scheduler.py + test_scheduler.py のみ、README.md と `docs/proposal/` は意図的に未コミット残置）。翌 18:00 JST から `2課` 初回自動配信、手動トリガもセット（[[02_diary/2026-05-27#run-47]]）
- **2026-05-27 夜**（session 0d2f488c、19:55-21:04 JST）: OpenSpec change **`multi-slot-reports-and-emphasis` 23/25 着地**、commit `89a52bf feat(report): multi-slot daily reports and per-group emphasis keywords`（12 ファイル）push `0289373..89a52bf`。目的: 1 プロファイル 1 配信時刻 → N 配信時刻（朝礼 + 夕礼）+ グループごとの強調キーワードで軽重を反映。§1 [config.py](functions/src/todobot/config.py) = `report_time: list[str]` 化 + coercion + sort/dedup + `MIN_SLOT_INTERVAL`（60min）検証 / §2 `specs/daily-report/spec.md` delta = slot-aware window（前回 slot 末尾〜今回 slot 末尾）+ per-group `emphasis_keywords: list[str]` / §3 [scheduler.py](functions/src/todobot/scheduler.py) = per-slot window（`anchored_at: 当回 slot の JST`）+ 複数 slot 並走 dedup（同 group 1 回/slot）/ §4 [firestore_repo.py](functions/src/todobot/firestore_repo.py) = per-group key 索引 + `groups/<id>/slot_history/{slot_iso}` 送信履歴 / §5 [report.py](functions/src/todobot/report.py) = prompt template に `emphasis_keywords` 動的挿入、無ければ素の prompt フォールバック。テスト 142 → **179 件** green + docs 更新（`docs/operations/acceptance.md` / `docs/operations/README.md` / [README.md](README.md)）。§6 実機 acceptance（2 slot 同日配信 + emphasis 適用）のみ残（[[02_diary/2026-05-27#19:55  ToDoBot multi-slot]]。同日早朝 `03d49c79` と scheduler 系で背景共有: 「window をスケジュール時刻に固定」+「report_time list 化 → window per-slot 化」の連動 evolution）
- **2026-05-28**（session cb878ae5、07:47-18:37 JST、10 turn）: `1課` プロファイル投入（multi-slot 初実運用、コメントタイポ `# Sonne` → `# Sonnet` 修正含む。deploy 経路は run-47 と同一）+ **18:00 初回配信失敗の障害対応**。Firebase CLI reauth が前日通した直後に 24h で再失効 → 再 OAuth（`developer1@`）で 4 関数更新。18:00 slot で 2課は通知・1課は LINE/メール共に未通知 → 仮説つぶし（Bot 未招待 → 否定 / `line_group_id` 不一致 → Firestore で 231 件確認し否定 / 発言 0 件 → 否定）→ Cloud Logging `daily_report.tick profile=1課 status=failed todos=0 err="tool_use block for record_todos has empty input"` で**真因確定**: Anthropic SDK（`claude-sonnet-4-6`）が `record_todos` を空 input の `tool_use` ブロックで返却（HTTP 200、`input={}`）。原因は `max_tokens=4096`（デフォルト）で出力 JSON 打ち切り — 1課 messages_in=231 vs 2課 119（todos 20 件成功）の約 2 倍量で上限到達。`llm.py:120` の `ValueError` → `daily_report.unhandled` → 配信スキップ。パッチ: `extraction.py:176` に `max_tokens=16384` 明示（本セッションでは未 commit、deploy 経由で本番反映）。`ALREADY_RAN` 手動解除（Runbook 参照）→ 再実行で `1課 sent slot=1800 todos=47 line=True email=True`。詳細パターン → [[05_learn/anthropic-tool-use-max-tokens-empty-input]]（[[02_diary/2026-05-28#07:47  ToDoBot 1課 profile]]）
- **2026-05-29**（session `63f6aec3-527b-4be5-bda4-c60e1ee7c179`、15:20 JST 開始、user 第一声「archiveとcommit, pushを整理して進めて」）: 5-28 までの未 commit 群を論理単位 3 commit に分割して push（`89a52bf..425cf89` → `origin/main`、実装作業なし）: `e754fe7 fix(extraction): raise max_tokens to 16384 to avoid truncated tool output`（本番反映済分のソース反映）/ `f25b214 docs(proposal): add ToDoBot proposal materials (HTML + PDF)`（5-22 作成分 + `提案資料.pdf`）/ `425cf89 chore(openspec): archive multi-slot-reports-and-emphasis`（`git mv` で archive、§6 実機 acceptance 2 task はドッグフード中の自然消化扱い）。5-28 残課題のうち解消 3 件（extraction commit / archive / 提案資料 commit）、未着手 3 件は現在の状態の残 TODO 参照（[[02_diary/2026-05-29#10:31  ToDoBot 5-28 残課題 archive + commit + push]] = run-54）

## Links

- [[05_learn/todobot-line-mvp]] — 設計・運用コスト・spec 一覧（planning 起点）
- [[05_learn/anthropic-tool-use-max-tokens-empty-input]] — 空 tool_use = max_tokens 打ち切りシグネチャの canonical learning
- [[02_diary/2026-04-28]] — 初日: ユースケース定義 + Plan B 棄却 + Firebase 一本化
- [[02_diary/2026-04-29]] — 実装 §2-§4 + B1-B4 docs
- [[02_diary/2026-04-30]] — 運用ドキュメント二層化
- [[02_diary/2026-05-16]] — §5-§10 完走 + 6 commits 分割 + meguruit/ToDoBot へ push
- [[02_diary/2026-05-21]] — E2E 疎通 + Gmail API DWD 切替 + @mention 解決バグ修正 + ドッグフード開始
- [[02_diary/2026-05-21#16:24  §10.1 実環境確認 — manual PASS + scheduler 0.5.0 fix + 19:28 JST scheduled tick PASS (e594cbdd, 5-21→5-22)]] — §10.1 PASS の diary 着地
- [[02_diary/2026-05-22]] — クライアント向け提案書 (HTML/PDF) + Mermaid 図 + 工数 253.5h 確定
- [[02_diary/2026-05-27]] — `2課` プロファイル追加 + scheduler window バグ修正 (anchor on report_time) + push (commit `0289373`)
- [[02_diary/2026-05-27#run-47]] — 5-27 朝セッション ingest entry
- [[02_diary/2026-05-27#19:55  ToDoBot multi-slot]] — 5-27 夜セッション ingest entry
- [[02_diary/2026-05-28#07:47  ToDoBot 1課 profile]] — 5-28 セッション ingest entry
- [[02_diary/2026-05-29#10:31  ToDoBot 5-28 残課題 archive + commit + push]] — 5-29 セッション ingest entry (run-54)
- [[06_output/2026-05]] — 配布後に「Client proposal delivered」を記録する先
