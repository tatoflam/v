# Tasks: wiki-knowledge-refocus

## 1. スキーマとプラグイン基盤（Plugins-tatoflam/claude-wiki）

- [x] 1.1 schema.md を改訂: 2 層アーキテクチャ（_staging = 捕捉層 / curated = 知識層）、staging ダイジェストの frontmatter 規約（target / category / tags / confidence / session / captured）、curated ページ標準構造（Summary / 現在の状態 / 決定事項 / 手順・Runbook / 経緯 / Links）、diary 書式（ユーザー活動のみ・テレメトリ禁止）を定義
- [x] 1.2 wiki-ingest SKILL.md を改訂: 書き込み先を `_staging/<YYYY-MM-DD>-<session8>.md` 新規作成に変更、curated ページへの書き込みと dirty-target defer ロジックを削除、diary 追記をユーザー活動 1–3 行に変更、wiki メタセッションの diary スキップを追加、完了報告に staging 滞留数を追加
- [x] 1.3 wiki-distill SKILL.md を新設: staging 走査 → target 別グルーピング → 標準構造への統合、処理済みの `_staging/archive/` 移動、sources 追記、矛盾 callout、00_self 更新チェック、home.md 更新、index.md 再生成、commit までの手順を記述
- [x] 1.4 wiki-query SKILL.md を改訂: curated 層優先の検索順序（標準セクション ↔ 質問型の対応、00_self を人格質問の一次根拠）、staging / diary フォールバック時の「未整理情報」ラベル、未 distill 関連情報の開示と /wiki-distill 提案を追加
- [x] 1.5 wiki-status SKILL.md を改訂: staging 滞留数（未 distill 件数・最古の日付）の表示と閾値超過時の /wiki-distill 促しを追加
- [x] 1.6 プラグイン README.md を 2 層アーキテクチャの説明に更新し、プラグインリポジトリを commit

## 2. Vault 準備と移行前スナップショット

- [x] 2.1 vault に `_staging/` と `_staging/archive/` を作成（.gitkeep）し、Obsidian のグラフ・検索設定で archive を除外
- [x] 2.2 chronic dirty ページ（03_work/todobot.md、04_life/minami-gakudo-fubokai-2026.md ほか git status で dirty な curated ページ）のユーザー編集内容を commit
- [x] 2.3 git tag `pre-refocus` を作成して push
- [x] 2.4 queue.jsonl の defer 済み・missing_transcript セッションを棚卸し: transcript が残っているものは旧方式のまま最終 ingest で回収、missing はその旨を log.md に記録して processed 化

## 3. 既存ページの標準構造への移行

- [x] 3.1 03_work の 13 ページを標準構造へ移行（時系列 H2 を 現在の状態 / 決定事項 / 経緯 に振り分け。meguru-pm-report.md など大型ページから着手し、sources・外部リンクを保持）
- [x] 3.2 04_life の 6 ページを標準構造へ移行
- [x] 3.3 00_self を拡充: preferences.md を新設し、profile / skills / values / goals を既存 vault 内容（feedback 記録・決定事項）から最新化
- [x] 3.4 home.md を新規作成: active プロジェクト一覧、直近の主要決定事項、00_self への導線
- [x] 3.5 05_learn の時系列追記型ページ（セッション単発キャプチャ）を洗い出し、統合候補リストを作って主要なものから標準原則（安定見出し＝主題）に整理

## 4. 新パイプラインの検証

- [ ] 4.1 実セッション 2–3 件で ingest を実行し、staging ダイジェスト生成・diary のユーザー活動記録・curated ページ無変更・defer ゼロを確認
- [ ] 4.2 curated ページ編集中（dirty）状態で ingest を実行し、defer が発生せず staging に着地することを確認
- [ ] 4.3 /wiki-distill を実行し、staging → curated 統合・archive 移動・sources 追記・home.md / index.md 更新を確認
- [ ] 4.4 /wiki-query で 3 型の質問（今どうなってる / なぜ決めた / どうやる）+ 人格質問 1 件を実行し、citation 付き応答と鮮度開示を確認
- [ ] 4.5 /wiki-status で staging 滞留数が表示されることを確認

## 5. 運用定着

- [ ] 5.1 log.md / _schema.md ミラーの書式を新パイプラインに合わせて更新
- [ ] 5.2 1 週間の実運用（ingest 自動 + distill 手動）で staging 滞留の実態を観察し、log.md に所感を記録
- [ ] 5.3 滞留が恒常化する場合のみ: distill の定期起動（launchd / cron / schedule スキル）を検討して Open Question を解消
