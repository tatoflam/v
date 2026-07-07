# knowledge-capture

セッション捕捉層。SessionEnd hook で enqueue されたセッションと 01_inbox の投入物を、conflict-free な staging へ確実に着地させる。

## ADDED Requirements

### Requirement: セッションダイジェストの staging 書き込み
`/wiki-ingest` は、処理する各セッションについてダイジェストを `_staging/<YYYY-MM-DD>-<session8>.md` として 1 ファイル新規作成で書き込まなければならない（SHALL）。ダイジェストの frontmatter には分類結果（`target`: 統合先ページの提案パス、`category`、`tags` 候補、`confidence`、`session`、`captured`）を含めなければならない（MUST）。ingest は 00_self / 03_work / 04_life / 05_learn / 06_output 配下の curated ページを変更してはならない（MUST NOT）。

#### Scenario: 通常セッションの捕捉
- **WHEN** queue.jsonl に未処理セッションがあり `/wiki-ingest` が実行された
- **THEN** セッションごとに `_staging/` 配下へ新規ダイジェストファイルが作成され、curated ページへの変更は発生しない

#### Scenario: ユーザーが curated ページを編集中でも捕捉が完了する
- **WHEN** 分類先候補のページ（例: 03_work/todobot.md）が git 上 dirty な状態で `/wiki-ingest` が実行された
- **THEN** ダイジェストは staging に着地し、defer は発生せず、queue 上そのセッションは processed になる

### Requirement: transcript 喪失の防止
`/wiki-ingest` は enqueue されたセッションの transcript を初回処理時に読み取り、内容を staging に永続化しなければならない（SHALL）。retention による transcript 削除を待つ defer 状態を作ってはならない（MUST NOT）。

#### Scenario: 初回 ingest で内容が永続化される
- **WHEN** セッション終了後、最初の `/wiki-ingest` がそのセッションを処理した
- **THEN** transcript 由来の内容が staging ファイルとして vault にコミットされ、以後 transcript の `.jsonl` が retention で消えても知識は失われない

### Requirement: diary はユーザー活動のみを記録する
`/wiki-ingest` は 02_diary の当日ファイルに、各セッションで「ユーザー（と Claude）が何を成したか」を記述するエントリを追記しなければならない（SHALL）。run 番号・queue 統計・defer 内訳・meta-ack 等の ingest 運用テレメトリを diary に書いてはならない（MUST NOT）。テレメトリは log.md および ingest-log.jsonl のみに記録する。

#### Scenario: 作業セッションの diary エントリ
- **WHEN** ユーザーの作業セッション（例: MeguruPMReport の週次レポート publish）が ingest された
- **THEN** 当日 diary に成果内容（何を作った・決めた・公開したか）が 1–3 行で追記され、queue 統計や run 番号は含まれない

#### Scenario: wiki メタセッションは diary に書かない
- **WHEN** `/wiki-ingest` 自身の実行セッションや wiki 運用のみのセッションが queue から処理された
- **THEN** diary エントリは作成されず、log.md への記録のみが行われる

### Requirement: 手動 inbox の staging 取り込み
`/wiki-ingest` は 01_inbox 直下の `.md` ファイルを読み取り、セッションと同様に分類付きダイジェストとして staging へ取り込まなければならない（SHALL）。分類確信度が低い項目は現行どおり 01_inbox に `> [!question] Needs sorting` callout 付きで残さなければならない（SHALL）。

#### Scenario: inbox 投入物の取り込み
- **WHEN** ユーザーが 01_inbox にメモを置いて `/wiki-ingest` が実行された
- **THEN** 分類可能なメモは staging ダイジェストになり inbox から除去され、分類不能なメモは question callout 付きで inbox に残る

### Requirement: staging 滞留の可視化
`/wiki-status` および `/wiki-ingest` の完了報告は、staging 内の未 distill ダイジェスト数を表示しなければならない（SHALL）。

#### Scenario: 滞留数の表示
- **WHEN** staging に未 distill のダイジェストが 12 件ある状態で `/wiki-status` が実行された
- **THEN** 出力に staging 滞留 12 件と `/wiki-distill` 実行の提案が含まれる
