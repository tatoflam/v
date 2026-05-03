---
title: ThreadsPosts — 腸活スタジオ Threads 自動投稿パイプライン
category: 03_work
tags: [project:threadsposts, channel:threads, tech:nodejs, tech:openspec, stage:active, entity:chokatsu-studio, milestone:v2-launch, infra:claude-github-app, infra:remote-agent]
sources: [088ab1c0-c2f2-4677-8201-1c6f9767bcfa, d7e16e9a-907a-4850-91af-9994070433bd, ea7dfd5b-e2ac-4067-82b3-a2efde32bb29, 0d885baa-7e18-4eff-b6e2-d0671863bc92]
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

## 2026-05-03 — v2 文体ローンチ + 5/4-5/8 スケジュール配信 + Claude GitHub App + 5/22 routine（session ea7dfd5b）

D011 アカウント始動（4-29）以降、第 2 投稿を打てずにいたのは「**煽り感**」「**PIVOT/教授の権威借用**に見えるのではないか」「**確信が得られず継続できなさそう**」という根本的な迷いのせい。技術ではなく**文体とペルソナ**の問題と特定し、v2 で全面リライトした上で 5/4 から自動配信を開始する。

### v2 ペルソナ — 「いち実践者・キュレーター」

**医師でも販売者でもない、いち実践者・キュレーター**として固定。

- 一人称: **「私」**（「皆さん」「あなたたち」のような上から目線の主語は使わない）
- 出典の扱い: **権威付けではなく出発点として**使う。本文中で肩書を強調せず、末尾 1 行に脚注として添える
- 読者との距離: 同じ目線で考えている人。**教えに行かない、煽らない**
- 最後の 1 行: 命令ではなく、**読者が自分で検証できる問い・観察ポイント**

### 禁止表現（CLAUDE.md / SKILL.md / posting_policy.md / feedback_post_style.md に明記）

| 旧（v1 で混入） | 理由 | 言い換え |
|---|---|---|
| 「〜かもしれません」 | 曖昧だと信頼されない | 一人称で言い切る（「私はこう見ている」） |
| 「〜と言われています」 | 出所のない伝聞は弱い | 誰が言ったか明記 |
| 「〜していないか？」「〜していい？」 | 煽り感が出る | 問い詰め型は禁止 |
| 「〜は危険だ」「逆効果になる」単独 | 恐怖訴求のみで終わると健康インフルエンサーの定型と同化 | 体験/解釈で挟む |
| 「変える時だ」「今すぐ〜しよう」 | 上から目線の命令 | 観察ポイント・問いで締める |

### D001-D010 全面リライト

v2 文体で 10 本書き直し（v1 と並存させ、`scheduled_at` の有無で v2 が活きる構造）。**5/4-5/8 の朝 08:00 JST / 夜 19:00 JST スロット**に配分し、1 日 2 投稿のローテーションを開始:

- 5/4 08:00 D003「免疫細胞の 7 割は腸にいる」 ← **本番 2 投稿目（D011 以来）**
- 5/4 19:00 D001「乳酸菌が逆効果になる人」
- 5/5 08:00 D004「6 割がつもり腸活」
- 5/5 19:00 D002「日本人の 95% が食物繊維不足」
- 5/6 08:00 D006「ヨーグルトより善玉菌のエサ」
- 5/6 19:00 D005「大腸がん女性死因 1 位」
- 5/7 08:00 D007「腸内環境の回復に半年かかる」
- 5/7 19:00 D008「食物繊維にも種類がある」
- 5/8 08:00 D009「内臓脂肪は毒素の塊」
- 5/8 19:00 D010「SNS 腸活を鵜呑みにするな」

3 ヶ月で月 6-7 桁収益化（@chokatsu_studio）の事業目標と、1 日 2 投稿ペースが整合（[[memory: project_revenue_target]]）。

### インフラ — Claude GitHub App + RemoteTrigger routine

- **Claude GitHub App** を `tatoflam/ThreadsPosts` に install (https://github.com/apps/claude)、Repository Secrets を設定
- **`/schedule` で 2026-05-22 09:00 JST に 1 回だけ実行する remote agent (RemoteTrigger)** を作成、dry run 完了
- Threads User ID と Threads App ID は別物 → docs/meta_developer_setup.md 冒頭に **ID/トークン対応表**を追加（commit `f6691db`）

### 5 commits push（`origin/main`、5-3 朝 → 昼）

- `f6691db docs(setup): ID/トークン対応表を追加し User ID 取得手順を強調`
- `42ca57b content(drafts): v2 文体へ全面リライト・スケジュール設定`
- `f64fe58 content(drafts): D001-D010 に出典明記を追加・著者名と topic_id を訂正`（4-30 から）
- `3fba767 fix(validate): glob を readdir に置き換えて Node 20 互換に`
- `dacde8c fix(publish): glob を readdir に置き換えて Node 20 互換に`

### 学び（横展開可能）

- **「続けられない文体は致命的」**: 投稿パイプラインの工学が完成していても、書き手が確信を持てない文体だと第 2 投稿で詰まる。技術ではなくペルソナ設計が運用継続性の本体
- 健康ジャンルのコンテンツは **事実 + 体験/解釈のハイブリッド**が信頼と人格を両立させる。純粋数字＋出典なし=煽り垢、純粋体験=N=1 で弱い、挟み込み型が最強
- 詳細パターンは [[05_learn/persona-driven-content-rules]] に切り出し

## 2026-05-03 follow-up — gut-health-affiliate Spec Decision 7 ＋ アフィリ紐付け 4 本 ＋ D002⇄D003 順序入替（session 0d885baa）

ea7dfd5b（午前のローンチ）で「1 日 2 投稿で 5/4–5/8 自動配信開始」体制を組んだ後、午後の `/opsx:explore` で **6/10 ドラフトがアフィリ無し**で公開予定だったのを発見。`Affiliates/products.yaml` の `affiliate_urls` が埋まっていたのは inulin_powder と equol_test_kit の **2 商品だけ**で、K001 / K004 対応の 6 本は紐付け不可。とくに **K004 が 5 本（D003/D005/D007/D009/D010）と量産的**で、**5/4 08:00 JST の初投稿予定 D003 がアフィリ無し**という構造が露呈。

### 紐付け 4 本 — `inject_affiliate.js --write` を 4 ドラフトに当てる

```
Drafts/  topic_id  injectable?  product
─────────────────────────────────────────────────────────
D001     K001      ✗           なし(K001対応商品が登録ゼロ)
D002     K002      ✓           inulin_powder       404/500
D003     K004      ✗           K004対応商品はあるが全URL未登録
D004     K005      ✓           equol_test_kit      373/500
D005     K004      ✗           同上
D006     K003      ✓           inulin_powder       379/500
D007     K004      ✗           同上
D008     K005      ✓           inulin_powder       411/500
D009     K004      ✗           同上
D010     K004      ✗           同上
─────────────────────────────────────────────────────────
                    4/10 紐付け可能
```

D002 / D004 / D006 / D008 に PR ブロック挿入、`affiliate_tags: [inulin_powder]` 等が入り 4/4 紐付け成功。validate / lint 11/11 PASS、文字数全件 500 以内。

### Decision 7 — 短縮 URL 不採用に再スコープ

design.md の当初案では Bitly を被せて投稿単位のクリック計測を内製する予定。実装直前にレビューして却下:

- **楽天 r10.to が既にトラッカー層を兼ねる短縮 URL** なので、Bitly 重ね掛けは二重リダイレクト分の UX 劣化＋ Bitly Free 側のクリック上限リスクを背負うだけで価値は薄い
- 楽天以外（Amazon / iHerb 等）に展開した時点で再評価すれば良く、現状の楽天単一チャネルでは過剰投資
- クリック数も売上もまずは **楽天管理画面からの CSV 手動同期で運用 2 週間データ蓄積**、必要性を実データで判断

artifact 更新:
- `design.md` — Decision 7 追記、Decision 6（短縮 URL）に改訂注記
- `tasks.md` — §2.3 短縮 URL ジェネレータ / §2.4 `shorten_url.py` を `[~] DEFERRED` 化、§6.3 に「clicks も手動同期」明記
- `specs/performance-tracking/spec.md` — Manual revenue entry に clicks 追加、`No automated click tracking layer` シナリオ追加
- `openspec validate gut-health-affiliate-marketing` → valid
- 進捗: 21/35 → **21/33（deferred 2 件除外で 64%）**

### 公開順序入替 — D002 を初投稿に

D002 と D003 の `scheduled_at` を交換 → **5/4 08:00 JST の初投稿が D002（K002, inulin_powder, アフィリ付）**になる構造に。

```
入替後:
  5/4 08:00 JST  D002 (K002, inulin_powder)  ← 初投稿、アフィリ付
  5/4 19:00 JST  D005 (K004)  アフィリ無し
  5/5 08:00 JST  D003 (K004)  アフィリ無し
  5/5 19:00 JST  D004 (K005, equol_test_kit)
  5/6 08:00 JST  D007 (K004)  アフィリ無し
  5/6 19:00 JST  D006 (K003, inulin_powder)
  5/7 08:00 JST  D010 (K004)  アフィリ無し
  5/7 19:00 JST  D008 (K005, inulin_powder)
  5/8 08:00 JST  D009 (K004)  アフィリ無し
  5/8 19:00 JST  D001 (K001)  アフィリ無し
```

### 2 commit に分割して push

- `b8a0c9f content(drafts): アフィリ紐付け4本＋D002⇄D003順序入替`（5 ファイル: D002/D003/D004/D006/D008）
- `b14bf37 spec(gut-health-affiliate): Decision 7 追加・短縮URL不採用に再スコープ`（3 ファイル: design / tasks / spec）
- `git push origin main` は **client-side hook で拒否**（"Pushing directly to main bypasses pull request review"）→ ユーザー側で手作業 push 完了、`origin/main` 反映確認

### 疎通確認も並行実施

- `npm run check:threads` → `/me` が `@chokatsu_studio (id 36075427142056546)` を返却
- `gh workflow run publish.yml --field dry_run=true` → 12 秒で success、Secrets 注入確認 + `POSTING_MODE=staging` 既定動作 OK
- `gh secret list` → `THREADS_ACCESS_TOKEN` (5-3 05:13Z) / `THREADS_USER_ID` (5-3 05:15Z) 登録確認
- `THREADS_USER_ID` は `vars.POSTING_MODE` が空なら workflow.yml 側の `|| 'staging'` デフォルトが効く設計 — 本番化は variable 追加だけで切替可能

### 残宿題

- 🔴 **K004 商品 URL 楽天登録**（5 本のアフィリ機会回収、もずく系 / ミックスナッツ無塩 / 寒天 など）
- 🟡 §6 Performance Tracking 実装（楽天管理画面 CSV 手動同期フロー、運用 2 週間でデータ溜めてから設計）
- 🟢 K001 商品 URL（D001）/ 本番化時の `POSTING_MODE=production` 切替

### 学び（横展開可能）

- **既にトラッカー層を兼ねるベンダー短縮 URL（r10.to）には別系の短縮 URL を被せない**: 二重リダイレクトの UX 劣化 + ベンダー層からのトラッキング情報を分断するデメリットが、独立計測軸のメリットを上回りやすい。Amazon / iHerb など別チャネル展開で「統一計測軸が要る」と判明した時に再評価する
- **OpenSpec の `[~] DEFERRED` ステータス**: 削除でも完了でもない第三のステータスで、「タスクは生きているが今 cycle では着手しない」判断履歴を spec 上に保持できる。Decision 追加と組み合わせて使うと判断トレースが綺麗
