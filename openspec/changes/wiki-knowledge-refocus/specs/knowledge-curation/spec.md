# knowledge-curation

知識層のキュレーション。`/wiki-distill` が staging のダイジェストを curated ページの安定構造へ昇格し、分身モデル（00_self）とナビゲーションを維持する。

## ADDED Requirements

### Requirement: /wiki-distill による staging の昇格
`/wiki-distill` スキルは `_staging/` 直下の未処理ダイジェストを target ページごとにグルーピングし、curated ページの標準構造セクションへ統合しなければならない（SHALL）。frontmatter の `target` は提案として扱い、統合時に再判定してよい。処理済みダイジェストは `_staging/archive/` へ移動し（SHALL）、削除してはならない（MUST NOT）。統合先ページの frontmatter `sources` には元セッション ID を追記しなければならない（MUST）。

#### Scenario: 複数ダイジェストの統合
- **WHEN** 同一プロジェクトのダイジェストが staging に 3 件ある状態で `/wiki-distill` が実行された
- **THEN** 3 件の内容が対象ページの該当セクション（現在の状態・決定事項・経緯等）へ統合され、3 ファイルは `_staging/archive/` へ移動し、sources に 3 セッション ID が追記される

#### Scenario: 対応ページが存在しない
- **WHEN** staging ダイジェストの target に該当する curated ページが存在しない
- **THEN** 標準構造で新規ページが作成され、index.md 再生成対象になる

### Requirement: curated ページの標準構造
03_work / 04_life の curated ページは `## Summary`、`## 現在の状態`、`## 決定事項`、`## 手順・Runbook`、`## 経緯`、`## Links` のセクション構造を持たなければならない（SHALL）。`現在の状態` は最新スナップショットとして distill が更新し、置き換えられた旧状態は `経緯` に日付付きで移さなければならない（MUST）。セッション日付を H2 見出しとする時系列追記構造を新規に作ってはならない（MUST NOT）。

#### Scenario: 状態更新と経緯への退避
- **WHEN** distill が「dev 環境デプロイ完了」という新状態をページに統合する
- **THEN** `現在の状態` が新スナップショットに更新され、旧状態の要点が `経緯` に日付付きで残る

#### Scenario: 矛盾の検知
- **WHEN** staging の内容が curated ページの既存記述と矛盾し、どちらが正か判定できない
- **THEN** 新旧併記のうえ `> [!warning] Contradiction` callout が付与される

### Requirement: 経緯の圧縮と provenance 保持
`経緯` セクションは要点のみの圧縮タイムラインとして維持しなければならない（SHALL）。詳細は staging archive・02_diary・frontmatter sources への参照で辿れるようにしなければならない（SHALL）。

#### Scenario: 長大化した経緯の圧縮
- **WHEN** distill 対象ページの経緯が細粒度エントリで肥大化している
- **THEN** 同一トピックのエントリが要約統合され、元詳細への参照（staging archive / diary リンク）が残る

### Requirement: 分身モデル（00_self）の継続更新
`/wiki-distill` は毎回、staging 内容から self シグナル（嗜好・判断基準・スキル変化・目標進捗）を抽出し、00_self の profile / skills / values / goals / preferences に反映しなければならない（SHALL）。作業・コミュニケーションの好みを記録する `00_self/preferences.md` を設けなければならない（SHALL）。反映すべきシグナルがない場合は変更しない。

#### Scenario: 判断基準の学習
- **WHEN** staging に「700万円帯の節税案件は事業法人側で実行する」という判断が含まれる
- **THEN** distill が 00_self/values.md（判断基準）または該当ページへ日付付きで反映する

#### Scenario: シグナルなし
- **WHEN** staging が技術作業のみで self シグナルを含まない
- **THEN** 00_self 配下は変更されない

### Requirement: home.md によるナビゲーション維持
`/wiki-distill` は vault ルートの `home.md` を維持しなければならない（SHALL）。home.md は active な 03_work / 04_life プロジェクトへのリンク、直近の主要決定事項、00_self への導線を含まなければならない（MUST）。自動生成の index.md（機械カタログ）とは別に維持する。

#### Scenario: プロジェクト状態変化の反映
- **WHEN** distill によりあるプロジェクトが `stage:active` から完了（07_archive 移動または `archived:` タグ）に変わった
- **THEN** home.md の active 一覧から除去される

### Requirement: 既存ページの標準構造への移行
既存の 03_work（13 ページ）および 04_life（6 ページ）は標準構造へ移行されなければならない（SHALL）。移行前に vault の git tag スナップショットを取得しなければならない（MUST）。時系列 H2 の既存内容は 現在の状態 / 決定事項 / 経緯 へ振り分け、情報を削除せず圧縮・参照化で保持しなければならない（SHALL）。

#### Scenario: 時系列ページの移行
- **WHEN** meguru-pm-report.md（時系列 H2 追記、49 sources）を移行する
- **THEN** 標準構造に再編され、最新セッション群の内容が `現在の状態` に、過去の詳細が圧縮された `経緯` に配置され、sources と外部リンクは保持される

#### Scenario: chronic dirty ページの移行
- **WHEN** ユーザー編集で長期間 dirty なページ（例: todobot.md）を移行する
- **THEN** ユーザーの編集内容を先に commit してから移行し、編集内容は失われない
