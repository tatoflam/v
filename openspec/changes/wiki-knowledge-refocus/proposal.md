# Proposal: wiki-knowledge-refocus

## Why

現行の wiki システムは Claude Code セッションの捕捉率は高い（SessionEnd hook → queue → /wiki-ingest、125 run / 76 日）が、成果物は「AI 向けのログ取得システム」になっている。02_diary は ingest 運用テレメトリの時系列追記（run-N 節の羅列）、03_work はセッション日付見出しの追記サイロ（例: meguru-pm-report.md は 49 sources を時系列 H2 で積むだけ）、00_self は 2026-04-23 に 4 ページ作られたきり更新なし。さらに dirty-target gate による慢性 defer（最長 54 日）が transcript の 30 日 retention と衝突し、知識が恒久的に失われている。

目指す姿は「体系だった知識・記憶を元に、簡単な問い合わせに Vault が応答できる分身システム」。ログ捕捉（すでに機能している）と知識体系化（機能していない）を分離し、後者を作り込む。

## What Changes

- **2 層アーキテクチャの導入**: 「捕捉層（log layer: セッションダイジェストの staging）」と「知識層（knowledge layer: 安定した主題構造を持つ curated ページ）」を分離する。ingest はユーザーが編集しない staging 領域にのみ書き、dirty-target defer を構造的に解消する。**BREAKING**（ingest の書き込み先とページ構造の規約が変わる）
- **ページ構造の標準化**: 03_work / 04_life / 05_learn のページを時系列追記から安定セクション構造（Summary / 現在の状態 / 決定事項 / 手順・Runbook / 経緯）へ移行する。
- **新スキル /wiki-distill**: staging に溜まったダイジェストを curated ページの安定セクションへ昇格（要約・統合・矛盾解消・相互リンク）する定期キュレーション工程を追加する。
- **02_diary の再定義**: 日記には「ユーザーが何をしたか」だけを書き、ingest 運用テレメトリは log.md / ingest-log.jsonl に限定する。
- **00_self の分身化**: distill 時に profile / values / goals / preferences を蓄積知識から定期更新し、応答のペルソナ基盤にする。
- **/wiki-query の一次インターフェース化**: curated 知識層を優先参照し、citation 付きで応答。知識層に無ければ staging / diary へフォールバックし、その旨を明示する。
- **ナビゲーションの人間化**: index.md の機械カタログに加え、ドメイン別 MOC（Map of Content）を distill が維持する。
- **既存ページの一括移行**: 現 125 ページを新構造へ移行する（chronic defer 中の todobot.md 等の解消を含む）。

## Capabilities

### New Capabilities

- `knowledge-capture`: セッション捕捉層。ingest がセッションダイジェストを staging に書き、diary をユーザー活動記録に限定し、defer/transcript 喪失を構造的に防ぐ要件。
- `knowledge-curation`: 知識層のキュレーション。/wiki-distill による staging → curated ページへの昇格、ページ標準構造、MOC 維持、00_self（分身モデル）の定期更新の要件。
- `knowledge-query`: 問い合わせ応答。/wiki-query が curated 層を一次参照し、citation・鮮度・フォールバックを明示して応答する要件。

### Modified Capabilities

（既存 spec なし — openspec/specs/ は空のため、すべて新規）

## Impact

- **プラグイン**: `~/repo/github/tatoflam/Plugins-tatoflam/claude-wiki/` — schema.md、skills/wiki-ingest、skills/wiki-query の改訂、skills/wiki-distill の新設。
- **Vault**: `~/repo/github/tatoflam/v/` — staging 領域の新設、02_diary の書式変更、03_work / 04_life / 05_learn の 125 ページ移行、MOC 新設、_schema.md ミラー更新。
- **Hook / 運用**: SessionEnd hook（auto-ingest-push.sh）は原則維持。distill の起動トレイル（手動 or 定期）を追加。
- **非対象**: queue.jsonl の仕組み、git push 自動化、Claude Code 本体の retention 仕様（回避はするが変更しない）。
