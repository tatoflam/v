# Design: wiki-knowledge-refocus

## Context

現行パイプラインは SessionEnd hook → `queue.jsonl` → `/wiki-ingest` → vault 直接書き込み → git push。捕捉は完全だが、書き込み先が curated ページそのものであるため、次の構造問題を生んでいる:

- **時系列追記サイロ**: 03_work のページはセッション日付 H2 の追記で成長し（meguru-pm-report.md は 49 sources）、安定した主題構造がない。問い合わせ時に「現在の状態」を読み取れない。
- **diary のテレメトリ化**: 02_diary の 59 ページは大半が `## HH:MM run-N /wiki-ingest` の運用記録。ユーザー活動の記録になっていない。
- **dirty-target defer → 知識喪失**: ユーザーが Obsidian で編集中のページに ingest が書けず defer が慢性化（todobot.md 系 54 日）。transcript は 30 日 retention で消え、7–8 セッションが恒久喪失済み。
- **00_self の停滞**: 4 ページが 2026-04-23 以来未更新。「分身」の核が育っていない。

制約: SessionEnd hook は非対話（`claude -p`）で走る。ユーザーは Obsidian で任意のページを随時編集する。transcript retention は 30 日で変更不可。

## Goals / Non-Goals

**Goals:**
- 捕捉（機械的・確実・conflict-free）と体系化（LLM による統合・要約）を別工程に分離する
- curated ページが「現在の状態」を常に語れる安定構造を持つ
- /wiki-query が curated 層 + 00_self を根拠に、citation 付きで簡単な問い合わせに答えられる
- defer による transcript 喪失をゼロにする

**Non-Goals:**
- queue.jsonl / SessionEnd hook / git push 自動化の仕組み変更（現行維持）
- ベクトル検索・embedding 基盤の導入（rg/grep ベースで足りる規模。将来検討）
- 過去 diary（59 ページ）の書き換え（履歴としてそのまま残す）
- Claude Code 本体の retention 仕様への対応要求

## Decisions

### D1. 2 層分離: ingest は `_staging/` にのみ書く

ingest はセッションごとのダイジェストを `_staging/<YYYY-MM-DD>-<session8>.md` に 1 ファイルとして書く。frontmatter に分類結果（`target: 03_work/todobot`、`category`、`tags` 候補、`confidence`）を持たせる。curated ページ（00/03/04/05/06）には一切触れない。

- **理由**: staging は新規ファイル append-only なので dirty-target 競合が構造的に消える。transcript は enqueue 後の初回 ingest で必ず読まれ、retention 喪失がなくなる。分類の知能は ingest に残す（distill は統合に専念）。
- **代替案**: (a) ページ隣接サイドカー（`todobot.log.md`）— curated 層とログ層が同居して汚染が続くため却下。(b) 01_inbox 流用 — inbox は「人間が置く場所」の意味を保つため却下。

### D2. 新スキル `/wiki-distill` が staging → curated ページへ昇格する

distill は staging を走査し、target ごとにグルーピングして curated ページの標準構造へ統合する。処理済み staging ファイルは `_staging/archive/` へ移動（provenance 保持、git 履歴もある）。あわせて 00_self の更新チェックと MOC/home 更新を行う。

- **起動**: MVP は手動（ユーザーが `/wiki-distill` 実行）。`/wiki-status` と ingest 完了ログが staging 滞留数を表示して促す。定期起動（launchd/cron）は滞留が問題になってから追加。
- **理由**: distill は要約・矛盾解消・構造化という失敗しうる LLM 作業なので、非対話 hook でなく attended で回し品質を確認しながら育てる。捕捉が別工程なので distill を数日サボっても知識喪失はない。
- **代替案**: ingest に統合統合機能を持たせる（現行の延長）— 非対話実行での品質担保と dirty 競合が解決しないため却下。

### D3. curated ページの標準構造

03_work / 04_life のページは次のセクションを持つ: `## Summary`（3–5 行）、`## 現在の状態`（最新スナップショット。distill が毎回上書き更新）、`## 決定事項`（累積、日付付き）、`## 手順・Runbook`（再現可能な操作）、`## 経緯`（圧縮タイムライン。詳細は sources / staging archive へのリンクで代替）、`## Links`。05_learn は既存の Summary/Details 型を維持しつつ「安定見出し＝主題、時系列は経緯に隔離」の原則を適用。

- **理由**: 問い合わせの大半は「今どうなってる？」「なぜそう決めた？」「どうやるんだっけ？」の 3 型。それぞれ 現在の状態 / 決定事項 / Runbook に一対一対応させる。
- **代替案**: 自由構造のまま distill の裁量に任せる — ページ間で構造が発散し query の参照信頼性が下がるため却下。

### D4. 02_diary はユーザー活動のみ、テレメトリは log.md へ

diary エントリは「そのセッションでユーザー（と Claude）が何を成したか」を 1–3 行で書く。run 番号・queue 統計・defer 内訳・meta-ack は log.md / ingest-log.jsonl のみに記録する。wiki メタセッション（ingest 自身の run）は diary エントリを作らない。diary への書き込みは ingest が staging 書き込みと同時に行う（daily ファイルは追記競合リスクが低く、当日中の即時性に価値があるため distill を待たない）。

### D5. 00_self を分身モデルとして distill が育てる

distill は毎回、staging 内容から self シグナル（好み・判断基準・スキル変化・目標進捗）を抽出し、00_self の profile / skills / values / goals に反映する。`preferences.md`（作業の進め方・コミュニケーションの好み）を新設。query は人格・嗜好に関わる質問で 00_self を一次根拠にする。

### D6. ナビゲーション: `home.md` + カテゴリ MOC

自動生成 index.md は現状維持（機械カタログ）。人間と query の入口として `home.md`（active な仕事・生活プロジェクト、直近の decisions、self へのリンク）を distill が維持する。カテゴリ規模が要求したら（>20 ページ）ドメイン別 MOC を追加。

### D7. 移行は distill の初回大規模実行として行う

既存 03_work 13 ページ + 04_life 6 ページを D3 構造へ書き直す（時系列 H2 の内容を 現在の状態/決定事項/経緯 に振り分け）。chronic dirty ページ（todobot.md、minami-gakudo-fubokai-2026.md）はユーザーの編集内容を先に commit してから移行する。05_learn は構造が近いので優先度低・逐次。移行前に git tag でスナップショットを取る。

## Risks / Trade-offs

- [distill を実行し忘れて staging が滞留する] → 知識喪失はない（捕捉済み）。wiki-status / ingest ログで滞留数を常時表示し、閾値超で通知文言を強調。恒常化したら定期起動を追加。
- [distill の要約で詳細が失われる] → staging ファイルは削除せず `_staging/archive/` に残す。経緯セクションから provenance リンクを張る。
- [ユーザー編集と distill の衝突] → distill は attended 実行なので dirty ページはその場でユーザーに確認して解決できる。非対話の ingest と異なり defer 慢性化しない。
- [「現在の状態」の上書き更新で誤情報が固定化する] → 上書き時に旧内容を経緯へ移し、矛盾検知時は `> [!warning] Contradiction` callout を残す（現行 ingest ルールを distill に移植）。
- [ingest の分類精度が staging の target ヒントに乗る] → distill は target を提案として扱い、統合時に再判定できる。低確信は現行どおり 01_inbox 送り。

## Migration Plan

1. プラグイン側: schema.md 改訂 → wiki-ingest SKILL.md 改訂（staging 書き込み化） → wiki-distill SKILL.md 新設 → wiki-query / wiki-status SKILL.md 改訂
2. Vault 側: `_staging/` 新設 → git tag `pre-refocus` → chronic dirty ページの commit → 既存ページ移行（03_work → 04_life → home.md → 00_self 拡充）
3. 検証: 新規セッション数件を ingest → distill → query の一巡で通し、defer ゼロ・citation 付き応答を確認
4. ロールバック: vault は git tag へ revert、プラグインは git revert。queue.jsonl 形式は不変なので捕捉は途切れない

## Open Questions

- distill の定期起動をいつ・どの方式（launchd / cron / Claude Code schedule）で入れるか — MVP 運用で滞留実態を見て判断
- 06_output（月次カタログ）を distill 管轄に含めるか — 現行書式で問題が出ていないため当面 ingest 由来の staging から distill が従来書式で追記
- embedding / ベクトル検索の導入基準 — vault が rg で応答 5 秒を超える規模になったら再検討
