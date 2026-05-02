---
title: ThreadsPosts — 腸活スタジオ Threads 自動投稿パイプライン
category: 03_work
tags: [project:threadsposts, channel:threads, tech:nodejs, tech:openspec, stage:active, entity:chokatsu-studio]
sources: [088ab1c0-c2f2-4677-8201-1c6f9767bcfa, d7e16e9a-907a-4850-91af-9994070433bd]
updated: 2026-05-03
---

# ThreadsPosts

## Summary

腸活ジャンル（乳酸菌・免疫・アレルギー）で Threads アカウント
[@chokatsu_studio](https://www.threads.net/@chokatsu_studio)（表示名：超活スタジオ🌱）
を運用するための、ナレッジ→投稿生成→Threads Graph API 直接投稿の自動化パイプライン。
リポジトリは [tatoflam/ThreadsPosts](https://github.com/tatoflam/ThreadsPosts)（Private）。
2026-04-29 に **本番初投稿成功**（post_id `17978831033843102` = D011）。

## Details

### スタック
- **言語**: Node.js（GitHub Actions のコールドスタートが Python より速いため採用）
- **データ**: YAML frontmatter（投稿は MD ファイル単位、`drafts/D001…` → `Published/`）
- **配信**: Threads Graph API 直接呼出（`graph.threads.net/v1.0`）
- **アフィリエイト挿入**: products.yaml で商品マスター管理、frontmatter `affiliate_keys` 指定で本文末に固定挿入
- **スケジューラ**: GitHub Actions cron（実装は Section 6 以降）
- **設計手法**: OpenSpec ワークフロー — change `gut-health-affiliate-marketing` 配下に proposal / design / tasks / specs を生成

### コンテンツ生成フロー
1. `Knowledge/` — 文字起こし MD（K001–K005、Dr.石黒・わくたよしのぶ・PIVOT 系の腸活解説 5 本）
2. `Topics/` — `.claude/skills/PostCreation/` で要点を抽出
3. `Drafts/` — D001–D010 を生成（180–219 文字、すべて 500 文字制約 PASS）
4. `validate_frontmatter.js` → `lint` → `publish.js --live` → `Published/` 移動 + frontmatter `status: published` 遷移
5. publish 成功時に `metrics.post_id` を frontmatter に書き戻し

### 公開済み下書き（2026-04-29 時点）
| # | ファイル | 切り口 | キー数字 | 字数 |
|---|----------|--------|----------|------|
| 1 | D001_乳酸菌が逆効果になる人.md | 乳酸菌サプリは合わない人には逆効果 | 490 人研究 | 180 |
| 2 | D002_日本人の95%が食物繊維不足.md | 95% が食物繊維不足 | 95% | 168 |
| 3 | D003_免疫細胞の7割は腸にいる.md | 免疫の 7 割は腸 | 7 割・半年〜1 年 | 194 |
| 4 | D004_6割がつもり腸活.md | 腸活している人の 6 割が効果なし | 6 割・40 兆個・1000 種 | 188 |
| 5 | D005_大腸がん女性死因1位.md | 大腸がんは女性死因 1 位 | 1 位・2〜3 倍 | 203 |
| 6 | D006_ヨーグルトより善玉菌のエサ.md | ヨーグルト腸活の罠 | — | 205 |
| 7 | D007_腸内環境の回復に半年かかる.md | 1 週間では変わらない | 半年・1 年 | 193 |
| 8 | D008_食物繊維にも種類がある.md | 種類別摂取が必要 | トップ 1%・週 30 品目 | 219 |
| 9 | D009_内臓脂肪は毒素の塊.md | ぽっこりお腹は毒素の塊 | — | 193 |
| 10 | D010_SNS腸活を鵜呑みにするな.md | SNS 腸活は個人差大 | 40 兆個・1000 種 | 218 |
| 11 | **D011 = アカウント始動投稿** | 「腸活スタジオ、本日始動」 | 40 兆個・95% | 124 |

### アカウント周り（@chokatsu_studio）
- 候補名 `chokatsu.lab` / `chokatsulab` / `chokatsu_lab` は全て取得不可 → `chokatsu_studio` で確定
- 表示名：**超活スタジオ🌱**
- bio：エビデンスベース腸活発信
- 連携：本人の Instagram と紐付け
- **Threads プロフィール保護ロックアウト**：API 認証作業中に「異常なアクティビティ検出」でアクセス制限。Instagram 側に通知が出ず復旧が困難だったが、最終的に Meta Developer Console の **ユースケース → カスタマイズ → アクセストークン作成** ルートで突破

### 認証・トークン
- **THREADS_USER_ID**: `36075427142056546`
- **THREADS_ACCESS_TOKEN**: 60 日有効 → **2026 年 6 月下旬までに再発行必須**
- `.env` 構成：`THREADS_ACCESS_TOKEN` / `THREADS_USER_ID` / `THREADS_APP_ID=2128135774707190` / `THREADS_APP_SECRET`
- 疎通確認：`npm run check:threads`（`/me` を叩いて user id + username を返す）

### アフィリエイト戦略
- **楽天アフィリエイト**：腸活スタジオ専用に **新規楽天アカウント**（`tato.flam+chokatsu@gmail.com`）を起こし、個人の楽天ポイント・購買履歴と分離
  - 短縮 URL：`a.r10.to/...`（Threads 用）
  - 商品例（4/22 時点で抜き出し済）：ちょーぐると／腸活革命単／腸活革命 2 個セット ほか
- **Amazon アソシエイト**：審査中でも投稿でリンク使用可、ただし **登録後 180 日以内に売上 3 件**ないとアカウント停止 → 楽天で実績を作ってから本格運用
- 4 アンカー戦略：D003 を旗印にした「免疫 70%」など投稿テーマに `affiliate_key` を割当て

### 本セッションの主要決定 / 修正
- スタック迷走（Python or Node.js）→ **Node.js** で確定
- `docs/meta_developer_setup.md` の手順 3 を **3 回書き直し**：旧 docs と現行 Meta Developer Console UI が乖離（Threads → 利用開始メニューが消失、フォーム保存エラー連発）。最終的に redirect_uri を `https://www.threads.net/` に置換して通過 — 詳細は [[05_learn/threads-graph-api-setup]]
- バグ fix 2 件（YAML パーサが `scheduled_at` を Date 型に変換、`check:threads` が `.env` を自動 load していない）→ commit `2beb918` `3bc9317`
- テスト 54 pass

### 進捗
**25 / 35 タスク完了**（Section 5 までの検証パイプラインを完全に通したところ）

| Section | 状態 |
|---------|------|
| 1. リポジトリ + Drafts 10 本 + frontmatter | 完了 |
| 2. アフィリエイト商品マスター・短縮 URL | **2.2 楽天/Amazon 登録待ち** |
| 3. validate / lint / test 基盤 | 完了（54 tests） |
| 4. アフィリエイト挿入 | 2.x 完了後 |
| 5. publish.js + Threads API 連携 + Published 移動 | 完了（D011 で実証） |
| 6. Insights 同期・週次レポート | 未着手 |
| 7. ドキュメント | 進行中 |
| 8. 本番運用移行 | 残 |

### 次回セッション再開手順
```bash
cd /Users/tato/repo/github/tatoflam/ThreadsPosts
git pull
npm test                # 54 pass 確認
npm run check:threads   # トークン疎通確認（60 日以内）
```

判断材料：
- D011 のインプレッション・反応を見て、次の投稿戦略（アフィリエイト挿入のタイミング）を調整
- 楽天アフィリエイトの残り 9 商品を `products.yaml` に埋めるか
- Section 6（効果測定 / Insights 同期）に進むか

## 2026-04-30 update — Node 20 互換 fix（CI 緑化）+ 出典明記テンプレ確立

セッション d7e16e9a（4-29 11:48 JST → 4-30 08:17 JST）。CI を緑化して「出典つき事実 + 自分の解釈/体験」のハイブリッドテンプレで Drafts D001–D010 を rewrite。

### CI 緑化（Phase A、4-29 11:48 JST）

`pipeline/publish.js` で `import { glob } from 'node:fs/promises'` を使っていたが、これは **Node 22+ 専用 API**。GitHub Actions の Node 20 ランナーで `SyntaxError: ... does not provide an export named 'glob'` となり CI 失敗。`Drafts/*.md` はフラット 1 階層 glob なので `readdir` で同等置換可（`Drafts/` 不在 = ENOENT は空配列）。

- commit `dacde8c fix(publish): glob を readdir に置き換えて Node 20 互換に` を `main` に push
- `pipeline/validate_frontmatter.js` も同じ `glob` を使っていたので Phase B でついでに修正（commit `3fba767`）。git hook / CI で同エラーを誘発する前に予防

### 出典明記テンプレ確立（Phase B、4-30 07:42–08:17 JST）

「Drafts は出典つき事実を出すか、自分の経験を語るか」というユーザの問いに対する戦略決定。健康・サプリ系の Threads では **「出典つき事実 + 自分の解釈/体験」のハイブリッド**が最強と判断:

- **数字だけで出典なしは逆効果**: D001 の「490 人の研究」「95% が食物繊維不足」など具体数字が出典なしだと「コピペ垢」「煽り垢」見え、健康ジャンルは特に不信を招く。薬機法・景表法的にも出典明示は防御
- **純粋体験談は弱い**: N=1 で権威性ゼロ、フォロワー増えにくい
- **挟み込み型が強い**: 「○○大学の研究で△△と判明（出典）→ 実際にやってみた → だからこう考えるべき」

CLAUDE.md の「誰が言ったか明記」既存ルールと整合。テンプレ:

1. 結論断言（1 行目）
2. **出典明記つき事実**（誰が・どこで言ったか）
3. 自分なりの解釈/問いかけ
4. 行動喚起
5. frontmatter `source:` ブロック追加（`author` / `publisher` / `title` / `url` / `type` — JS validator は unknown field を弾かないので追加自由）

### D001–D010 一括 rewrite と訂正

- 全 10 本に `source:` frontmatter ブロック ＋ 本文に「医師・石黒成治氏の YouTube 解説より」「PIVOT『がんを防ぐ腸活』で〜」のように **人物名 + プラットフォーム/番組名** を主張の前に挿入
- **「石黒誠先生」→「石黒成治氏（医師）」** に名前修正（D003 / D005 / D007 / D009 / D010 の 5 本）— K001 transcript と YouTube チャンネル情報で正しい名前を確認
- **D010 の topic_id を K001 → K004 に修正** — 引用「やっぱりマーケティングなんですよね」が K004（PIVOT「がんを防ぐ腸活」）からの引用だったため
- **D009 の引用符号解除** — 「メタボを笑ってる人は…」が verbatim quote として確認できないので、書き手の解釈として地の文に
- **D008 から「30 品目」主張削除** — 福田慎司氏の発言ではなく石黒氏の発言だったため

### 2 commit に分けて push（レビューしやすさ優先）

1. `3fba767 fix(validate): glob を readdir に置き換えて Node 20 互換に`（4-30 08:17 JST）
2. `f64fe58 content(drafts): D001-D010 に出典明記を追加・著者名と topic_id を訂正`（4-30 08:17 JST）

範囲: `dacde8c..f64fe58 main -> main`

### 学び

- **Node 22+ 専用 API は CI runner 環境を確認**: `actions/setup-node` の version 指定とリポの `engines` の整合をチェック。`node:fs/promises` の `glob` は v22 追加で v20 に未バックポート
- **健康ジャンルの Threads は事実 + 体験/解釈のハイブリッドが最強**: 純粋数字＋出典なしは逆効果、純粋体験は弱い、挟み込み型が信頼と人格の両立に必要
- **frontmatter `source:` ブロックは JS validator が unknown field を弾かない**性質を利用して非破壊で追加可能（schema 拡張不要で出典追跡を始められる）

### 進捗（4-30 終了時点）

- D001–D010 の出典強化完了（**Section 7「ドキュメント」進行中** → 出典担保部分は完了）
- D011 = 本番初投稿成功（4-29、post_id `17978831033843102`）
- 次の投稿（D001–D010 のいずれか）は `status: scheduled` + `scheduled_at` 設定でローテ開始可能、ただしまだ実行されず

## Links

- [[02_diary/2026-04-29]]
- [[02_diary/2026-04-30]]
- [[05_learn/threads-graph-api-setup]]
- [[06_output/2026-04]]

## 2026-04-29 — CI Node 20 互換 fix ＋ Drafts 出典明記（session d7e16e9a）

### CI failure と修正
- GitHub Actions で `pipeline/publish.js` が `node 20.20.2` 環境で `SyntaxError: 'node:fs/promises' does not provide an export named 'glob'` を吐いて落ちる。`import { glob } from 'node:fs/promises'` は **Node 22+ 専用**だが `engines` は `>=20` 宣言
- 単一ディレクトリ glob (`Drafts/*.md`) なので `readdir` で代替。`Drafts/` 不在時は ENOENT を空配列に変換
- 同 glob を使っていた `pipeline/validate_frontmatter.js` も同時修正

### 出典明記の方針確立
- 健康・サプリ系で「出典なしの数字」は煽り垢に見え、薬機法・景表法的にも防御が弱い。**出典つき事実 + 自分の解釈/体験**のハイブリッドで 3 段構成（断言 → 出典つき事実 → 解釈/問いかけ → 行動喚起）に統一
- frontmatter に `source:` ブロック（`author` / `publisher` / `title` / `url` / `type`）を追加。本文に「医師・石黒成治氏のYouTube解説より」「PIVOT『がんを防ぐ腸活』で〜」のように **人物名 + プラットフォーム名**を主張前に挿入
- D001–D010 全 10 本に出典 frontmatter ＋ 本文 1 行を反映

### 付随訂正（出典確認で発見）
- **「石黒誠先生」→「石黒成治氏（医師）」**：D003 / D005 / D007 / D009 / D010（YouTube チャンネル名で正しい姓を確認）
- **D010 の `topic_id` を K001 → K004 に修正**：「やっぱりマーケティングなんですよね」が PIVOT K004 からの引用と判明
- **D009 の引用符号を解除**：「メタボを笑ってる人は…」が verbatim quote として確認できず → 書き手の解釈として地の文に
- **D008 の「30 品目」削除**：石黒氏の発言を福田氏に誤帰属していた

### 出力
- `3fba767 fix(validate): glob を readdir に置き換えて Node 20 互換に`
- `f64fe58 content(drafts): D001-D010 に出典明記 + 著者名/topic_id 訂正`
- 先行 `dacde8c` で `pipeline/publish.js` の Node 20 fix を単独 push 済
- 範囲: `dacde8c..f64fe58 main -> main`（`origin/main`）
- 検証: 11 ファイル validate / lint 通過、54 tests pass、ローカル `publish.js --dry-run` 動作

### 学び
- Node 20 ↔ 22 で `fs/promises` の `glob` export 有無が分かれる → engines バージョンと API 利用バージョンを揃える運用が必要
- ヘルスケア発信は **N=1 体験談だけでは弱く、出典つき事実だけでも冷たい** → 「事実 + 解釈/体験」の挟み込み型が CV/フォロー両方に効く（コンテンツマーケティング基本則）
