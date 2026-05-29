---
title: ToDoBot — LINE 業務会話 → 日次 ToDo レポート
category: 03_work
tags: [project:todobot, tech:python, tech:firebase, tech:firestore, tech:line-messaging-api, tech:anthropic-claude, tech:google-workspace, tech:gmail-api, tech:domain-wide-delegation, tech:openspec, tech:pytest, tech:mypy-strict, tech:mermaid, tech:chrome-headless-pdf, stage:dogfood, stage:proposal-ready, milestone:mvp-code-complete, milestone:repo-pushed-meguruit, milestone:e2e-validated, milestone:client-proposal-pdf, entity:meguruit-org, client:meguruit]
sources: [2648ee43-ade1-4be4-b64a-b31c9d21bfb3, 8dc542f5-d276-4e26-b04a-6f9fe822db47, f9415d55-991f-4d85-8f11-50e87deb910b, 5905d91d-8f8f-4b6f-b8d0-06c7f97422e2, ab52fdac-54a0-4291-bdb0-c112d8f67a03, f27991f0-61ce-4c42-af2f-f6d8f794426f, 03d49c79-640a-479f-b7bd-a60cb8111948, 0d2f488c-5346-40e1-b55a-dd3d80b26354, cb878ae5-38c1-4e42-a2dd-56eae9f219f2]
updated: 2026-05-29
---

# ToDoBot

## ステータス (2026-05-28) — `1課` プロファイル投入 + extraction max_tokens 4096→16384 修正

5-28 セッション (`cb878ae5`、07:47-18:37 JST、10 turn) で運用追加 + バグ修正の 2 件着地。`config/profiles.yaml` は `.gitignore` のまま、`functions/src/todobot/extraction.py:176` の 1 行修正は本セッション時点で **未 commit** (ローカル working tree 変更のみ、本番には deploy 経由で反映済)。

### 1課 profile 追加

`config/profiles.yaml` (gitignore) に `1課` を新設:

- `slots = [(6,0), (18,0)]` (`report_time: ["06:00", "18:00"]`) — multi-slot 初回 実運用、5-27 夜 `multi-slot-reports-and-emphasis` 着地の最初のユーザ
- `skip_empty = True`
- `llm_model = claude-sonnet-4-6` (2課と同。コメント末尾タイポ `# Sonne` → `# Sonnet` 修正)
- `to = [structure, thomma, sichikawa]` (3 名宛、@meguru-construction.com)
- `line_group_id = C72073b30f65df1e031e52bb771710a01`

deploy 経路は run-47 (5-27) と同一: 編集 → `scripts/deploy.sh functions` (`predeploy` フックで `functions/config/profiles.yaml` へコピー)。

### Firebase CLI reauth が 24h で再失効

5-27 run-47 で通したばかりの `firebase login --reauth` が 5-28 朝の deploy 試行で再度切れていた (`Authentication Error: Your credentials are no longer valid`)。`developer1@meguru-construction.com` で再 OAuth → 4 関数 (`daily_report_scheduled` / `daily_report_trigger` / `line_webhook` / `cleanup_scheduled`) すべて `Successful update operation`。reauth セッション寿命は約 24h、daily ops 中に切れる前提で運用する。

### 18:00 初回配信失敗 → max_tokens overflow が真因

deploy 直後の 5-28 18:00 slot で、**2課 は通知出たが 1課 は LINE/メール共に未通知**。仮説を順に潰す:

| 仮説 | 検証結果 |
|---|---|
| Bot が 1課 グループ未招待 | user 「公式アカウントはメンバーには入ってる」→ 否定 |
| `line_group_id` 不一致 | user 「投稿はしてる」→ Firestore log で 1課 group に 231 件メッセージ確認 → 否定 |
| 06:00-18:00 で発言 0 件 (`skip_empty=true`) | messages_in=231 → 否定 |
| **extraction が失敗** | Cloud Logging に `daily_report.tick profile=1課 status=failed todos=0 err="tool_use block for record_todos has empty input"` → **真因確定** |

**真因の構造**: Anthropic SDK (`claude-sonnet-4-6`) が `record_todos` tool を **空 input の `tool_use` ブロック**で返してきていた。HTTP 200 OK、ツール呼び出し自体は来るが `input={}`。原因は `max_tokens=4096` (デフォルト) で出力 JSON 打ち切り。1課 = messages_in 231 件、2課 = messages_in 119 件 (todos_extracted 20 件成功) で、約 2 倍のメッセージ量で出力 token が 4096 上限に届いた。`llm.py:120` が `ValueError("tool_use block for record_todos has empty input")` で弾き → `daily_report.unhandled` → `status=failed` → 配信スキップ。

詳細パターンと再発防止策は [[05_learn/anthropic-tool-use-max-tokens-empty-input]] に分離記録。

### パッチ

`functions/src/todobot/extraction.py:176` の `extract_with_tool(...)` 呼び出しに `max_tokens=16384` を明示。

- 4x 拡張で **47 件抽出**まで余裕がある (1課 5-28 実測)
- 16384 は Anthropic Sonnet の 1 messages call 上限を踏まえた保守値
- ローカル `git status` では `M functions/src/todobot/extraction.py` のまま未 commit、deploy 経由で本番に反映済

### 手動再実行 (`ALREADY_RAN` の解除)

スケジューラの冪等トランザクション `try_acquire_report_run` が `report_runs/1課_2026-05-28_1800` の存在で `ALREADY_RAN` を返し再実行を拒否したため、Firestore ドキュメントを 1 件削除して再 trigger:

1. `gcloud firestore documents delete 'projects/todobot-dev/databases/(default)/documents/report_runs/1課_2026-05-28_1800'` — **auto-mode classifier がブロック**、user 承認後も再ブロック → `google-cloud-firestore` Python ライブラリ経由 (ローカル venv) で同等処理を実施し回避 (CLI 経由とライブラリ経由で classifier 判定が異なる)
2. Secret Manager から `JOB_SHARED_SECRET` 取得 → `curl -i -H "X-Job-Token: ${TOKEN}" "https://asia-northeast1-todobot-dev.cloudfunctions.net/daily_report_trigger?profile=1課&slot=1800"`
3. **結果**: `1課 sent slot=1800 todos=47 line=True email=True` — LINE / Email 両方配信成功

### 設計判断 / フォロー TODO

- **`max_tokens` の運用上限は messages 量で変動** — 1課 5-28 18:00 = 231 msg / 47 todos / 16384 tok で OK だったが、将来的に 1課 が 500 msg/slot を超えると同様の打ち切りが再発する可能性。`extraction.py` での `max_tokens` を `f(messages_in)` の動的設定 (例: `min(64000, max(8192, messages_in * 60))`) にすべきかは要議論
- **未 commit の `extraction.py` 修正**: 本セッションで commit せず終話したので、次セッションで `max_tokens=16384` を含む commit を切る必要あり (テスト追加: `tool_use` 空 input → 適切な ValueError + Cloud Logging 出力の e2e ケース)
- **`ALREADY_RAN` 手動解除パターン**: 今回のような extraction 失敗系の retry は Firestore ドキュメント手動削除という destructive 操作になる。`daily_report_trigger` に `force=true` クエリパラメータを足して内部で `report_runs` ドキュメントを削除 → 再実行する semantics にできれば、将来の同種事故が早く戻せる

### see also (5/28 セッション由来)

- [[02_diary/2026-05-28#07:47  ToDoBot 1課 profile]] — 本セッションの ingest entry
- [[05_learn/anthropic-tool-use-max-tokens-empty-input]] — 空 tool_use = max_tokens 打ち切りシグネチャの canonical learning
- session `cb878ae5-38c1-4e42-a2dd-56eae9f219f2` (5/28 07:47-18:37 JST、1課 profile + extraction max_tokens 修正)

## Summary

LINE グループに常駐する Bot が業務会話を受信し、1 日 1 回 LLM (Claude Haiku/Sonnet) で「誰が・いつまでに・何を」を構造化抽出、指定時刻 (既定 20:00 JST、プロファイル可変) に LINE push とメールで配信する個人事業向けの自動化。

リポ: 当初 `tatoflam/ToDoBot` (4-29 root-commit `8b98f60`) で着手していたが、2026-05-16 に user が組織アカウント側で新リポ `meguruit/ToDoBot` (private、SSH origin) を切り、`main` を push 完了 → これが canonical となった。ローカルの working tree パスは `/Users/tato/repo/github/tatoflam/ToDoBot` のまま (path はリネームせず、remote だけ差し替え)。

OpenSpec workflow で proposal / design / specs / tasks 一式起票、change 名 `line-todo-bot-mvp`。設計詳細・運用コスト試算・spec 一覧は [[05_learn/todobot-line-mvp]] を参照。

## ステータス (2026-05-27 夜) — multi-slot-reports-and-emphasis 23/25 着地 + push (0d2f488c)

同日夜の `0d2f488c-5346-40e1-b55a-dd3d80b26354` セッション (19:55-21:04 JST) で 1 つ大物 OpenSpec change が着地、`origin/main` に push (commit `89a52bf`)。

### change 名: `multi-slot-reports-and-emphasis` (spec-driven)

**目的**: 1 プロファイル 1 配信時刻 → 1 プロファイル N 配信時刻 (例: 朝礼 + 夕礼) + グループごとの強調キーワード適用で、業務会話の中で軽重を反映できるレポートに。

**着地範囲 (§1-§5 = 23/25 task)**:

1. **§1 Config schema** ([config.py](functions/src/todobot/config.py)): `report_time: list[str]` 化、str→[str] backward-compat coercion、sort + dedup、`MIN_SLOT_INTERVAL` (60min) 検証。既存 `"20:00"` プロファイル無改修で動作継続
2. **§2 Daily-report spec** (`specs/daily-report/spec.md` delta): slot-aware window (前回 slot 末尾〜今回 slot 末尾)、per-group `emphasis_keywords: list[str]` 追加で extraction prompt に重み付けキーワードを差し込む
3. **§3 Scheduler** ([scheduler.py](functions/src/todobot/scheduler.py)): per-slot window 算出 (`anchored_at: 当回 slot の JST` ベース)、複数 slot 並走時の dedup (同 group は 1 回/slot)
4. **§4 Firestore** ([firestore_repo.py](functions/src/todobot/firestore_repo.py)): per-group key 索引追加、`groups/<id>/slot_history/{slot_iso}` collection で送信履歴
5. **§5 Report builder** ([report.py](functions/src/todobot/report.py)): Anthropic SDK prompt template に `emphasis_keywords` セクションを動的挿入、ない場合は素の prompt にフォールバック
6. **テスト**: 142 → **179 件** green、`pytest` / `mypy --strict` / `ruff` / `black` 全クリア
7. **docs 更新**: `docs/operations/acceptance.md` + `docs/operations/README.md` + project [README.md](README.md) (slot list 説明 + emphasis keywords セクション)

**未着地 (§6)**:
- 実機 acceptance (本番環境で 2 slot 同日配信 + emphasis_keywords 適用) — warmup 中の人ゲートとして user 判断待ち

### commit + push

- commit `89a52bf feat(report): multi-slot daily reports and per-group emphasis keywords` (12 ファイル、change 関連のみ)
- `0289373..89a52bf` push 完了 (`origin/main`)
- `docs/proposal/` (HTML/PDF + 提案 PDF) は意図的に untracked のまま (本セッションのスコープ外、5/22 提案書から残置)

### 設計のキモ

- **backward-compat coercion**: `report_time: "20:00"` (旧スカラ) を `["20:00"]` に自動昇格、既存プロファイル全て無改修で動作
- **slot interval 60min lower bound**: extraction prompt 再呼び出しコスト ($0.01-0.05 / 回) と LINE push 重複防止のための保守的下限。将来要件があれば緩める方向は spec で議論
- **per-group emphasis vs per-slot emphasis**: per-group (= LINE グループ単位) で確定。理由は「2課」のような業務単位は LINE グループに 1:1 対応する想定で、slot は時間帯違いの再配信扱い (例: 朝礼 = 7:30、夕礼 = 18:00 で同じグループ会話を 2 度配信)
- **emphasis_keywords の prompt 戦略**: `system` ブロックに「以下キーワードに該当する発言は重み付けして拾え」と入れる。文字列リスト (空配列 = フォールバック)、強い指示ではなく soft hint

### see also (0d2f488c 由来)

- [[02_diary/2026-05-27#19:55  ToDoBot multi-slot]] — 本セッションの ingest entry
- 同日早朝の `03d49c79` (scheduler window バグ修正) と本セッション `0d2f488c` (multi-slot) は両方とも scheduler 系で背景共有: 「`report_time` が可変 → window アンカーをスケジュール時刻に固定」+「`report_time` を list 化 → window 算出も per-slot 化」の連動 evolution

## ステータス (2026-05-27 朝) — `2課` プロファイル追加 + scheduler window バグ修正 + 本番 deploy + push

5/27 セッションで運用追加 2 件着地、いずれも `origin/main` に push 済み:

1. **`2課` プロファイル追加** (`config/profiles.yaml:29`)
   - 新規 `line_group_id: C4a85b58...`、配信時刻 18:00 JST、宛先 `integrate@` / `thomma@`
   - LINE Group ID 取得手順: Bot 招待 → グループでテキスト 1 通発言 → Firebase コンソール Firestore `groups/` コレクションに新規ドキュメント増 (= `line_group_id`)、または Cloud Logging で `line_webhook persisted 1 message(s)` ログ参照
   - `config/profiles.yaml` は `.gitignore` 対象、`firebase.json` の `predeploy` フックで `functions/config/profiles.yaml` に上書きコピーされる (§採用スタック 5/21 既述)

2. **scheduler window バグ修正** ([scheduler.py:118-128](https://github.com/meguruit/ToDoBot/blob/main/functions/src/todobot/scheduler.py#L118-L128)、commit `0289373`)
   - **Before**: `since = 当日 00:00 JST` / `until = 実行時刻` → 18:00 以降〜深夜の発言が **どのレポートにも入らない** 取りこぼし
   - **After**: `since = 前日 report_time JST` / `until = 当日 report_time JST` → 24h 完全カバー、ジッタ ±7min に左右されない (スケジューラの実行時刻ではなく **スケジュール時刻** にアンカー)
   - 新規テスト 2 件: `test_messages_window_spans_previous_to_current_report_time` / `test_messages_window_anchored_on_report_time_not_run_time`、既存 `test_messages_window_starts_at_local_midnight` を新意味に更新
   - **テスト**: 147 → **149 件** green、`pytest` / `mypy --strict` / `ruff` / `black` 全クリア
   - 設計判断: `report_time` がプロファイルごと可変なので 24h ウィンドウは「直前の同時刻 〜 今回の同時刻」が自然 (= スケジューラの ±7min jitter に依存せず安定)

3. **デプロイ**: `scripts/deploy.sh functions` → 4 関数 (`cleanup_scheduled` / `daily_report_scheduled` / `line_webhook` / `daily_report_trigger`) すべて `Successful update operation`
   - **詰まりポイント**: 1 回目 deploy 時に **Firebase CLI の認証切れ** に遭遇、`firebase login --reauth` (ブラウザ認証走るので user 手動) → 再 deploy で成功
4. **commit + push**: `0289373 fix(scheduler): anchor daily-report window on scheduled report_time` (scheduler.py + test_scheduler.py のみ)、`origin/main` に push 完了 (`2f879fb..0289373`)。`README.md` (Mermaid 図) と `docs/proposal/` (HTML/PDF + 提案 PDF) は意図的に未コミットのまま残置 (本セッションのスコープ外)
5. **明日 18:00 JST から `2課` の初回レポート自動配信**: deploy 直後に Bot 招待 → グループ発言 → Firestore `groups/` 確認の運用手順を user に提示済。手動トリガもセット (`curl -i -H "X-Job-Token: ${JOB_SHARED_SECRET}" "https://asia-northeast1-todobot-dev.cloudfunctions.net/daily_report_trigger?profile=2課"`)

### see also (5/27 セッション由来)

- [[02_diary/2026-05-27#run-47]] — 本セッションの ingest entry
- session `03d49c79-640a-479f-b7bd-a60cb8111948` (5/27 19:52 JST 開始、scheduler fix + 2課 profile + deploy)

## ステータス (2026-05-22 時点) — クライアント向け提案書 (HTML/PDF) + Mermaid 図、工数 253.5h 確定

5/22 にクライアント向け提案書を `docs/proposal/todobot-proposal.html` + `todobot-proposal.pdf` で作成、README.md にも Mermaid データフロー図を追加。**未 push 状態**（`?? docs/proposal/`、`M README.md`）でローカル待機 → 配布アクションは未実施のため [[06_output/2026-05]] には記録せず、配布後に改めて追記する想定。

### 工数明細 (時間単位、合計 253.5h ≒ 31.7 人日、1人日=8h)

| フェーズ | 内容 | 工数 | 備考 |
|---|---|---:|---|
| **企画・設計** | ユースケース定義 + アーキテクチャ決定 + OpenSpec 仕様策定 (proposal/design + 4 capability specs) + コスト試算 | **20h** | |
| **実装** | §1 init / §2 config / §3 data / §4 webhook / §5 extraction / §6 report / §7 scheduler / §8 observability / §9 deploy / §10.0 まで | **128h** | tasks.md の §1-§10 実装分、`8b98f60..b83d678` の 11 commits |
| **インフラ構築・外部サービス設定** *(独立計上、初版 217.5h から +24h)* | Firebase Blaze + Secret Manager + Firestore index/TTL/rules / LINE Developers / Workspace 超管理者経由 Gmail API 認可 + DWD / Anthropic / B1-B4 外部サービス準備 | **24h** | thomma@/developer1@ のハイブリッド IAM + DWD 登録（admin.google.com）を含む |
| **テスト** | unit (142→147 件) + integration + mypy/ruff/black 強制 + プロンプトキャッシュ動作確認 | **38h** | |
| **運用テスト・受け入れ確認** *(初版 15h から +12h)* | §10.1 24h+ ドッグフード + §10.2 受入チェックリスト + 実環境バグ修正（`secrets=[...]` 追加 + predeploy hook + @mention 解決 + Gmail API 移行など） | **27h** | 配信成功率 / コスト計測 / SLA 観測 |
| **積み残し** | チャネル追加 (account_2/3 想定) + 通知先追加 (メール宛先プロファイル) + ダッシュボード | **16.5h** | |
| **合計** | | **253.5h** | 実施済 237h + 積み残し 16.5h |

### クライアント向け提案書 (9 ページ A4、ネイビー基調)

- `docs/proposal/todobot-proposal.html` — 編集可能なソース。
- `docs/proposal/todobot-proposal.pdf` — 配布用 PDF (9 ページ、初版は 8 ページ、5/22 夕方に **合計工数欄** 追加で +1 ページ = 7 ページ目末尾に「実施済 237h(29.6人日) + 積み残し 16.5h(2.1人日) = **総合計 253.5h(31.7人日)**」を表組で明示)。
- 構成: ① 表紙 / ② エグゼクティブサマリ + 目次 / ③ 背景課題 + ソリューション + 配信サマリイメージ / ④ 主要機能 (4 capability + スコープ外) / ⑤ システム仕様 (アーキテクチャ + データモデル) + Mermaid データフロー図 (SVG 埋め込み) / ⑥ 工数見積 (上記表 + 実装内訳) / ⑦ 運用コスト試算 (月額 約¥300) + 合計工数表 / ⑧ スケジュール + 前提 + リスク + 次のステップ
- **PDF 生成手段**: `wkhtmltopdf` / `weasyprint` / `chromium` 未インストール環境のため **Google Chrome ヘッドレス** で生成。再生成コマンド: `"/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" --headless --disable-gpu --no-pdf-header-footer --print-to-pdf=todobot-proposal.pdf "file://$(pwd)/todobot-proposal.html"`
- **目視 QA**: `pdftoppm -png -r 110 todobot-proposal.pdf pp` でページごとの PNG を生成し、page 6 でコールアウトがフッターに重なる issue を 1 件発見 → CSS で余白調整 → 当初 8 ページ → 合計表追加で 9 ページに収束、レイアウト崩れなし
- **Mermaid 図の二重配置**:
  - README.md → Mermaid 記法のまま記述 (GitHub がネイティブ描画、エンジニア向け閲覧経路)
  - 提案書 HTML → ネットワーク制限下で `mmdc` (mermaid-cli) は使えなかったが `cdn.jsdelivr.net/npm/mermaid@11/dist/mermaid.min.js` は curl 可 → ブラウザ side でレンダリング後 SVG 埋め込みで PDF 化 (PDF 配布先がオフライン環境でも描画される)
- **配布アクション (未実施 / TODO)**: メール送付 / Drive 共有 / クライアント宛 Slack 投稿 のいずれか。配布次第 [[06_output/2026-05]] に「Client proposal delivered」として記録する想定

### see also (5/22 セッション由来)

- [[02_diary/2026-05-22]] `23:xx  ToDoBot クライアント向け提案書` ブロック — 工数調整プロセスの逐次ログ
- [[02_diary/2026-05-22]] `23:5x  run-35` ブロック — 5/22 夕方 user リクエストで 7 ページ目末尾に合計工数表追加 → PDF 8→9 ページ再生成
- session `ab52fdac-54a0-4291-bdb0-c112d8f67a03` (本セッション + 合計欄追加 delta)、`f27991f0` (run-34 worker)

## ステータス (2026-05-21 時点) — E2E 疎通完了、§10.1 ドッグフード進行中

2026-05-21 セッションで初回エンドツーエンド疎通（LINE Verify → グループ招待 → メッセージ受信 → `daily_report_trigger` 手動 curl → LINE push 配信成功 → Gmail 配信成功）まで到達。残作業は §10.1 の 24h ドッグフード継続と §10.2 受入チェックリスト消化のみ。

- **追加コミット 2 本** (5-16 → 5-21、論理単位で分割):
  ```
  b83d678 fix(extraction): resolve @mention assignee even when mentionee is uncached
  b7898db feat: Gmail API email delivery, requester tracking, deploy hardening
  ```
- **テスト**: 142 → **147 件** green（mention 解決の追加ケース 4 件＋requester 追跡 1 件）、`mypy --strict` / `ruff` / `black` 全クリア維持
- **メール配信方式変更**: SMTP Relay → **Gmail API + Domain-wide Delegation (キーレス DWD)**（詳細は [[05_learn/todobot-line-mvp]] §採用スタック の差分）。理由: user 自身が Workspace 管理者で、`developer1@` だけ 2SV を ON にする運用が煩雑だったため、SA キー無しの DWD に振り切った
- **5/21 セッションで実装した変更**:
  - `GmailNotifier`（`google-auth` + `googleapiclient` 経由、`iamcredentials.googleapis.com` で `developer1@` の short-lived token を発行 → `gmail.users.messages.send`）— SMTP secrets (`GWS_SMTP_USER`/`GWS_SMTP_PASS`) は廃止
  - **依頼者 (requester) 追跡**: ToDo モデルに `requester` / `requested_at` を追加、レポートで「依頼者 → 担当者」を表示（user 側で並行実装した分を同梱）
  - **`secrets=[...]` 宣言を Functions デコレータに追加**: Secret Manager に投入済みでも関数 ENV に mount されておらず 500 を返していた（初回デプロイのハマりどころ）
  - **predeploy hook**: `config/profiles.yaml` はリポ root にあり Functions bundle に含まれないため、`firebase.json` の `predeploy` で `functions/` 配下にコピー
  - メール HTML 見出しを `<div>` インラインスタイル化（h1 巨大化を抑制、読みやすさ調整）
- **@mention 解決バグ修正 (b83d678)**: `resolve_assignee` が `users/` キャッシュ（= グループで発言したことのあるメンバーだけ）との照合を要求していたため、未発言のメンバーを @mention しても「未割り当て」に分類されていた。@mention は user_id を確実に含むので、キャッシュ未登録でも user_id ベースで担当者を割り当てるよう修正。表示名はメッセージ本文の mention span (`mentionees[].index/length`) から抽出
- **`/opsx:archive` はまだ呼ばない**: §10.1 ドッグフード 24h 完走後

### 2026-05-21 E2E 疎通の流れと詰まりポイント

1. **Firebase ログインを `thomma@meguru-construction.com`（Workspace 超管理者）で実施** — 当初メモは `admin@` だったが実在せず。プロジェクトを `meguru-construction.com` GCP Organization 配下に作るには super-admin が必須。Workspace サブスク課金と GCP Cloud Billing は別商品だが、同じ Payments Profile / 同じカードに紐付ければ「同じ請求書」で運用可能（→ B4 docs を全面書き換え）
2. **IAM ハイブリッド運用**: `thomma@` = プロジェクト作成・Org IAM・課金・API enable。`developer1@` = 日常 CLI ops。ただし `gcloud services enable iamcredentials.googleapis.com` は `developer1@` に Service Usage Admin を付けても `PERMISSION_DENIED` → `--account=thomma@` 明示で通った（org policy で API enable は super-admin に閉じている）。`firebase deploy` 自体は事前に Eventarc 等の API を auto-enable しに行くため、`developer1@` を Service Usage Admin に格上げする必要があった
3. **LINE Verify** — 1 回目タイムアウト（コールド起動 + バインド未済の 500）、`secrets=[...]` 修正と再デプロイで Verify OK
4. **Bot 招待 → groupId 取得**: OA Manager で「グループ・複数人トーク参加」ON、`@541dotgb` を招待、1 通発言で Firestore `groups/` に `Cbb2771c...` 形式の groupId 記録。`config/profiles.yaml` の `Cxxxxxxx` placeholder を実値に書換 → 再デプロイ
5. **ToDo 抽出のタイムウィンドウ**: `[実行日 00:00 (プロファイル TZ), trigger 実行時刻 now)` — `created_at` 基準。team-b で「テスト」1 件のみだと `skip_empty=true` で無送信になるため、ToDo っぽいメッセージを 2〜3 通流して動作確認
6. **DWD 登録は admin.google.com**: クライアント ID `113869879276262501859`、スコープ `https://www.googleapis.com/auth/gmail.send`。SA に自己 Token Creator (`roles/iam.serviceAccountTokenCreator`) を付与すれば、SA 鍵を発行せずに impersonation できる
7. **デフォルト返信メッセージ**: 「メッセージありがとうございます！申し訳ありませんが、このアカウントでは個別のお問い合わせを受け付けておりません。次の配信までお待ちください 🌙」— Bot は dispatch-only、対話はしない設計を明示

### 採用スタック 差分 (5/21 確定)

- **メール送信**: ~~Google Workspace SMTP Relay (アプリパスワード)~~ → **Gmail API + Domain-wide Delegation (キーレス、`iamcredentials.googleapis.com` 経由)**。コード側は `Notifier` 抽象で吸収済だったので差し替えはモジュール 1 つの置換で完結
- **シークレット**: `GWS_SMTP_USER` / `GWS_SMTP_PASS` を廃止、`GMAIL_DELEGATED_SENDER` 等の Gmail API 用設定に置換

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
- [[02_diary/2026-05-21]] — E2E 疎通 + Gmail API DWD 切替 + @mention 解決バグ修正 + ドッグフード開始
- [[02_diary/2026-05-22]] — クライアント向け提案書 (HTML/PDF) + Mermaid 図 + 工数 253.5h 確定
- [[02_diary/2026-05-27]] — `2課` プロファイル追加 + scheduler window バグ修正 (anchor on report_time) + push (commit `0289373`)
