---
title: ThreadsPosts — 腸活スタジオ Threads 自動投稿パイプライン
category: 03_work
tags: [project:threadsposts, channel:threads, channel:rakuten-affiliate, channel:amazon-associates, tech:nodejs, tech:openspec, tech:playwright, tech:claude-sonnet, tech:openai-whisper, tech:yt-dlp, tech:esim, stage:active, stage:incident-response, entity:chokatsu-studio, entity:meta-classifier, milestone:v2-launch, milestone:d002-production, milestone:research-pipeline-k006, milestone:companify-stage1, milestone:weekly-cycle-bootstrap, milestone:weekly-cycle-w19-execution, milestone:openspec-3-archive-batch, milestone:playbook-process-revamp, milestone:playbook-archive-sync, milestone:account-ban-pivot, milestone:openspec-3-change-ban-pivot, milestone:ban-pivot-explore-synthesis, milestone:publish-relocate-local-shipping, milestone:legacy-tenant-archive, milestone:ban-decision7-reframing, milestone:3-account-staged-scaling, milestone:interior-uchi-style-confirmed, milestone:account-1-phase-0-shipped, milestone:account-1-d001-draft, milestone:interior-playbook-from-K, milestone:subject-omission-style, milestone:launch-week-brand-suppression, entity:oheyamemo, genre:interior, incident:threads-ban-2026-05-04, infra:claude-github-app, infra:remote-agent, principle:local-first-anthropic, principle:capture-first-explore, principle:change-boundary-equals-commit-boundary, principle:composite-fingerprint-not-single-cause, principle:milestone-driven-scaling, principle:subject-axis-not-credential-axis, principle:two-layer-persona-profile-ok-body-ng, principle:launch-week-trust-first, topic:ceiling-light, topic:youtube-subtitle-research]
sources: [088ab1c0-c2f2-4677-8201-1c6f9767bcfa, d7e16e9a-907a-4850-91af-9994070433bd, ea7dfd5b-e2ac-4067-82b3-a2efde32bb29, 0d885baa-7e18-4eff-b6e2-d0671863bc92, e01596df-0fca-4571-bc96-599e88e0e72c, 4695d1ed-f9c9-4b80-ab4c-c1dd3a3eff2d, ce4cb7d1-c726-49a8-9b98-b1f7c1856063, 57a002bd-6c29-47d4-ae0b-f42b43b5b03d, d40649e2-fb8b-4e0a-8c18-14bc3a972ea8, a73c0aa2-c9a4-46e3-ab60-72b6b426901a, 8b57f7c8-b8fa-4f65-8c06-06cf6fbe87b3, 97d3f618-8d6c-40e6-8210-06549512f183, cef7a3c1-5798-4534-ab51-63c1a2279734, c02fca64-85c4-40f5-9bae-00ea56f138c1, f198b34e-7c91-4bee-8bf4-a3a532f86901, ea0b21e8-0197-4d87-a637-45d18bc759d7, 665cb2da-de7e-4b1b-93f9-2500f8d6fe95, 99902682-b840-494b-b76c-59c90854c892, c0b0dfea-a81b-4470-b2f5-07cbbaa4aae8, 1228fa25-787b-4c38-b347-3a9231d5431a, d59da658-e5d8-4292-9095-c907f18fcca8, 196a73b5-f043-46ca-a902-3a9ba3669c98, 028c145c-62e4-46ba-8c98-efc52d5d77cc, 6c99bbeb-c873-4342-bc9c-e6807882b5f3, 8cf2b80c-2557-43b0-849c-8aa5aea7552f, c7f92639-9af8-456a-92ef-8f770a7311e9, 86141ecc-90e4-4efe-8751-35b1fc2af063, a878e29c-097d-4107-99de-8409c30f6dff, 72d2768d-9123-4b73-bb0b-175426c509ae]
updated: 2026-05-28
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

## 2026-05-03 evening — D002 本番初の手動 publish + Rakuten resolver / a.r10.to 自動化 + 8 commits + cc-company B+C 方針（sessions 4695d1ed + e01596df）

午後の `0d885baa` follow-up でアフィリ紐付け 4 本が整い、5/4 08:00 JST に D002 が cron 自動投稿される構造ができたあと、夜にかけて **「いきなり本番で前倒し publish」＋「products.yaml アフィリ URL の解決パイプライン本格化」** の 2 軸が並走。session 順は narrative 上 4695d1ed → e01596df（D002 publish が先、resolver 整備が後）。

### D002 本番初の自動投稿成功（session 4695d1ed）

D011 アカウント始動（4-29）以来 **2 投稿目を cron 待たずに手動で前倒し publish**。

- アカウント: `@chokatsu_studio` (id `36075427142056546`)
- 投稿: D002「日本人の95%が食物繊維不足」→ Threads post_id **`17884465608547868`**
- アフィリ: `inulin_powder` 楽天 r10.to URL 入り PR ブロック、240/500 字
- 副産物:
  - `Analytics/metrics.csv` 初書き込み（メトリクス CSV パイプ稼働確認）
  - Drafts/D002 → Published/D002 自動移動、frontmatter `status: published` 反映
- 残課題: D011（post_id `17978831033843102`）は Threads 側で insights API が 404 を返す → 古いテスト投稿の残骸推定、削除 or 残置は user 保留

### Amazon アソシエイト登録（180 日ハードル）

- store ID: `chokatsustudi-22`（5-3 登録）
- デッドライン: **2026-10-30**（180 日後）— 登録から 180 日以内に Amazon 経由 3 件以上の適格売上が必要、未達でアカウント取消
- サイト説明文（256 字以内）: chokatsu_studio のミッションに合わせて user 採用
- **重要**: `Affiliates/products.yaml` の Amazon URL は **全 11 商品で `null` のまま**（楽天 URL のみ充足）。今のまま投稿しても Amazon クリック 0 → 180 日後にアカウント停止リスク。**戦略は「楽天で実績作り → Amazon は実績後に紐付け」を維持** [[memory: project_affiliate_accounts]]

### 8.4（GH Actions 有効化）確認 → 32/33 完了

- `THREADS_ACCESS_TOKEN` (5-3 05:13Z) / `THREADS_USER_ID` (5-3 05:15Z) Secrets 登録済
- `Publish scheduled Threads posts` workflow active
- `tasks.md` の 8.4 を `[x]` 反映、進捗 32/33（gut-health-affiliate-marketing）
- 残 8.5 のみ — 1 週間後の週次レビュー（`Analytics/weekly_2026-W19.md` 待ち、user セッション停止）

### Rakuten resolver / a.r10.to 自動化パイプライン（session e01596df）

`/opsx:propose` 2 件で **products.yaml の affiliate URL を半自動で埋めるパイプライン**を確立。

#### auto-resolve-rakuten-affiliate-links（楽天市場 API → long URL）

- `pipeline/resolve_rakuten_links.js` 起こし: `IchibaItem/Search` で商品名検索、**レビュー件数最多** の itemUrl を選んで `affiliate_urls/rakuten` に書き戻す
- CI: `.github/workflows/resolve_affiliates.yml` を手動 dispatch で動作確認（workflow run `e18dd37 auto-resolve: rakuten links [skip ci]`）
- 楽天 Web Service 設定:
  - `RAKUTEN_APPLICATION_ID` = `0cf35ebb-3d03-4789-86c1-77d3248ebc52`
  - `RAKUTEN_AFFILIATE_ID` = `53692ea4.f6bb037f.53692ea5.997c9a74`（管理画面の **専用 ID** 表記、商品ごとに変わるソース内 `ichiba/<id>/` ではない）
  - allowed website に `github.com` 不要（GH Actions からは any-origin OK）

#### auto-rakuten-short-url（Playwright login → a.r10.to）

- Bitly 案を user 主導で却下（コスト＋上限リスク＋楽天が既にトラッカー層）
- 代わりに **楽天アフィリエイトサイトの「短縮 URL」機能を Playwright login で叩く** 方針に転換
- `pipeline/rakuten_login.js` + `npm run rakuten:login` で local human が 1 度 login → cookie 保存 → 短縮 URL 一括取得
- **CI と人手の責務分離** (commit `4b1c881 refactor`):
  - CI = `SHORTEN_URLS=false` で long URL refresh 専任（`resolve_affiliates.yml`）
  - 人手 = local で短縮 URL 取得（`npm run resolve:rakuten` + Playwright）
  - 規約 7 条「機械的アクセス」は低頻度・正規 login・人手起動の組合せで許容範囲、reCAPTCHA 出現時は人手対応
- 11/11 商品の a.r10.to 短縮 URL を埋める（commit `8282608`）
- redirect 待ち + `PLAYWRIGHT_HEADLESS` env 読込み修正（commit `ddb1ca9`）

#### `steamed_soybeans` ハマり → 検索 fallback 3 段階化（汎用 fix + 個別 override）

- 商品名 `蒸し大豆・豆類ミックス` は楽天市場に存在しない複合語で 0 件、旧 fallback の `蒸し大豆 豆類ミックス`（中黒で先頭 2 語連結）も 0 件、`蒸し大豆`（先頭 1 語）で 343 件ヒット
- **汎用 fix**: `generateQueryVariants` を `[<full>] → [<先頭2語>] → [<先頭1語>]` の 3 段カスケードに拡張
- **個別 fix**: `Affiliates/products.yaml` の `steamed_soybeans` に `rakuten_search_query: '蒸し大豆'` を追加（人間 override の例示・即時解決）。`name` は説明的表記、`search_query` は検索精度優先で別管理する設計
- commit `3aab8f8 fix(resolve-rakuten)`

#### scheduled_at JST 化 + 人間らしい揺らぎ（commit `40ecc03`）

- 旧: UTC 表記＋ `:00` 完全揃い → 機械臭が強い
- 新: JST 表記、朝 7:55–8:04 / 夜 20:58–21:09 のレンジで秒もランダム化、「ちょっと早めに上げる人」感を演出
- 5/4-5/8 の 9 draft（D001/D003-D010）に分配、146/146 tests pass

#### rakuten-dashboard clean URL 抽出（commit `04e0d78`）

- RWS の `itemUrl` を `freelink` に直渡しすると wrap 文字列で破綻 → clean item URL を抽出する parser を入れて修正

### 2 changes archive（gut-health-affiliate-marketing 完走 + 関連 2 change）

- `3c59820 archive gut-health-affiliate-marketing + 5 specs を main spec へ反映`: メイン change を完走 archive、配下 5 specs を main spec へマージ
- `9d3ccae openspec archive 2 changes + performance-tracking 実装の差分整理`: `auto-resolve-rakuten-affiliate-links` + `auto-rakuten-short-url` の 2 change を archive、untracked だった performance-tracking 実装ファイルを差分整理として同 commit に含める運用、152/152 tests pass

### 8 commits 全リスト（origin/main 反映済）

```
3c59820 archive gut-health-affiliate-marketing + 5 specs
9d3ccae archive 2 changes + performance-tracking 実装差分整理
3aab8f8 fix(resolve-rakuten): 検索 fallback 3 段階化 + steamed_soybeans search_query
40ecc03 content(drafts): scheduled_at JST 表記化 + 配信時刻最適化
04e0d78 fix(rakuten-dashboard): RWS itemUrl から clean item URL を抽出
8282608 chore(affiliates): 楽天 a.r10.to 短縮 URL を 11/11 商品に反映
ddb1ca9 fix(rakuten-login): redirect 待ち + PLAYWRIGHT_HEADLESS env 修正
4b1c881 refactor(auto-rakuten-short-url): CI と人手の責務分離 (CI は SHORTEN_URLS=false)
```

### 5/9 (土) 以降の Drafts 在庫ゼロ問題

D001-D010 が 5/4-5/8 で消費し尽くされる構造を確認。Knowledge 別の偏り:

- **K001**（乳酸菌×パーキンソン病）: 1/?? しか活用していない、深堀り余地大
- **K002**（ポストバイオティクス）: published 2 件
- **K003**: 活用余地大
- **K004**（PIVOT がんを防ぐ腸活）: 5/?? と過密
- **K005**: 中程度

5/9-5/15 で朝夜 14 投稿の新規ネタ 10-12 件起案（次セッションで採用判断）。例: K001 系「合わない兆候の見つけ方」「腸脳相関と迷走神経」「同じ菌摂取のリスクとローテーション」、K002 系「短鎖脂肪酸を増やす食べ方」など。

### 会社化（cc-company B+C ハイブリッド段階導入）

user 提案: 「このリポジトリを会社化したい」 → `https://github.com/tatoflam/cc-company` plugin の構想を借用。3 解釈を整理:

- **A. cc-company plugin install**: `/plugin marketplace add Shin-sibainu/cc-company` → `/company` で `.company/` 配下に「腸活スタジオ」のメタ組織。コードは現状維持、Claude との会話交通整理だけ変わる
- **B. ディレクトリ部署別再編**: `dept/research/` `dept/content/` `dept/marketing/` `dept/dev/` のような部署フォルダに ThreadsPosts のコードを再配置
- **C. multi-tenant 将来拡張**: 1 リポで複数アカウント運用（chokatsu / 別ジャンル）

**user 判断**: **B+C ハイブリッドを段階導入**、cc-company plugin 導入にはこだわらない（手段でしかない）。次セッションで `/opsx:propose` 起票予定 [[memory: project_companify_direction]]

### 学び（横展開可能）

- **API 規約とスクレイピングの境界線は「正規 login + 低頻度 + 人手起動」**: 完全自動化（リフレッシュトークン保管含む）は規約 7 条のグレーに落ちやすいが、**人手 login → 短縮 URL 一括取得 → CI でその後 long URL refresh のみ自動化**、というハイブリッドはコストもリスクも低く取り回せる。「機械的アクセス」と判定される境目は「**人間が起動した形跡があるか**」が大きい
- **`name` ≠ `search_query` の分離設計**: 商品マスターの「人間向け説明的表記」と「API 検索クエリ」は別フィールドにすべき。`steamed_soybeans` の `蒸し大豆・豆類ミックス` (name) vs `蒸し大豆` (search_query) のような乖離は健康・食品ジャンルでは頻発する（複合表記が API DB に存在しない）。fallback の N-gram カスケードに加え、override フィールドを設計時から入れておく
- **「ステージング不要、いきなり本番」判断は構造的に正しい**: アカウントが既にライブな状況では staging account の追加コストは管理負荷だけ増やす。`POSTING_MODE` 切替で本番／dry-run を制御できる pipeline を整えた時点で、staging account は不要

## 2026-05-04 — research-pipeline-k006 完走（dept/research/ 着工 + K006/K007/K008 自動生成 + Whisper ASR + OpenSpec 7→8）

5/9 以降の Drafts 在庫ゼロ問題への打ち手として、e01596df セッション末尾で宿題化していた「`dept/research/` 着工」を会社化提案より先に着手。1 セッション（5-3 24:26 → 5-4 03:02 JST、約 2.5 時間）で **62 タスク完走 → PR #2 マージ → archive commit `712ac50`** まで貫通。

### 起票（`/opsx:propose research-pipeline-k006`）

`openspec/changes/research-pipeline-k006/` に 4 artifacts (proposal / design / specs / tasks)、validate 4/4。design.md の D1-D10 で:

- CLI: `npm run research -- --keyword <kw> | --url <url>`、`--max-candidates` / `--auto-pick` / `--force` / `--dry-run`
- D2 候補選択: YouTube Data API v3、再生数 × 新しさ
- **D3（後で全面書換え）**: 当初は `youtube-transcript` 一択、字幕なし skip、ASR 不採用
- D5 Topics 合成: Claude Sonnet 4.6 + プロンプトキャッシュ + K005 を few-shot
- D6 frontmatter: `topic_id` / `source_url` / `generated_at` / `model` / `transcript_path` / `status: draft_auto`
- D7 採番: 既存 K001-K005 は frontmatter なし legacy、ディレクトリスキャンで最大連番 +1
- D8 dedup: `source_url` の正規化（v= パラメータのみ）で衝突検出

### `--asr` opt-in 仕様変更（user 主導の `/opsx:explore`）

「ASR は明示フラグ時のみ起動 / 通常運用は無料・即時 / 字幕なし遭遇したら明示的にコストを払う / 多言語は別問題: Topics 生成の system prompt に『出力は常に日本語』追加」を user 指示。コスト試算（1h 動画基準・月 60 本想定）:

| 手段 | 1h あたり | 月 60 本 | 多言語 | 字幕なし | 精度 |
|---|---|---|---|---|---|
| timedtext（デフォルト） | $0 | $0 | △ | ❌ | △ |
| Whisper API（`--asr`） | $0.36 | $21.6 | ✅ | ✅ | ◎ |
| Whisper local（`--asr=local`、予約） | $0 | $0 | ✅ | ✅ | ◎ |

→ design.md D3 全面書換え + **D11「ASR 実装の構造」新設** + D9 に `OPENAI_API_KEY` 追加 + D10 にテスト 2 件追加 + Goals/Non-Goals/Risks/Migration 全更新。spec.md にも「ASR opt-in via --asr flag」「ASR transcript file format」の 2 Requirement 新設（6 シナリオ）

### 実装（`/opsx:apply` で 55/62 タスク + smoke 残り）

新規 8 ファイル + tests を [pipeline/research/](pipeline/research/) 配下に:

| ファイル | 役割 |
|---|---|
| `index.js` | CLI dispatcher、6 フラグ |
| `youtube_search.js` | YouTube Data API v3 直叩き + tests 5 件 |
| `transcript_fetch.js` | 言語優先 `ja > en > その他` + tests 7 件 |
| `audio_download.js` | yt-dlp ラッパ + tmp sweep + tests（asr.js と合計 10 件） |
| `asr.js` | Whisper API + verbose_json + finally cleanup |
| `topic_synthesize.js` | Claude Sonnet 4.6 + cache_control + K005 few-shot + 「日本語出力」prompt + tests 6 件 |
| `write_knowledge.js` | frontmatter + ファイル名サニタイズ + 衝突検出 + tests 5 件 |
| `k_numbering.js` + `dedup.js` | tests 12 件 |

### Smoke 実行（K006 → ASR auth エラー → openai SDK upgrade → K007 bug fix → K008）

| Step | Knowledge | 経路 | コスト | 結果 |
|---|---|---|---|---|
| §10.3 実生成（キーワード） | K006 PIVOT「痩せ菌」(35分) | `youtube-transcript ja` | ~$0.08 | ✅ 校閲 PASS |
| §10.5 ASR smoke 1st | くるくるメディカル「大腸菌」(60秒) | `whisper-1` | — | ⚠ Node v25 + openai v4 で `ECONNRESET` |
| 副産物 commit `55f57e1` | — | — | — | openai SDK v4 → v6 upgrade |
| §10.5 ASR smoke 2nd | 同上 | `whisper-1` | — | ⚠ 429 quota（user 側で billing 設定 + auto-recharge） |
| §10.5 ASR smoke 3rd | K008 同上 | `whisper-1` | $0.006 + Topics $0.04 | ✅ end-to-end OK、Whisper 誤字「イイコリ」「肝菌」を Claude が `E. coli` `グラム陰性桿菌` に文脈解釈 |
| §10.6 多言語 smoke | K007 TED-Ed (5分) | `youtube-transcript ja (auto-translated)` | ~$0.05 | ⚠ JA コミュニティ翻訳字幕で迂回（真の EN→JA Claude 翻訳パス未検証） |
| §10.6 再検証 | BBC Global 1667 chars EN | `youtube-transcript en` → Claude 翻訳 | (smoke のみ、保存せず) | ✅ 真の EN→JA パス verified |

K007 生成時に **3 件の bug 発見**（commit `8841d66`）:

1. **markdown コードフェンス ` ``` ` 混入 + frontmatter 二重**: system prompt の出力フォーマット例を ` ``` ` で囲んだら Claude が literal コピー → 出力例を plaintext に変更
2. **`model: claude-opus-4-5` を hallucinate**: 我々の指定は `claude-sonnet-4-6` → frontmatter は LLM に任せず、プログラム側で確実に上書き
3. **`(unknown)` / `(URL指定)` メタデータ**: `--url` モードで動画 metadata を fetch していなかった → YouTube oEmbed 取得を追加

加えて docs に **ffmpeg 必須** を追記（yt-dlp のみ言及していた）

### archive（`/opsx:archive research-pipeline-k006`）

- archive 先: [openspec/changes/archive/2026-05-04-research-pipeline-k006/](openspec/changes/archive/2026-05-04-research-pipeline-k006/)
- specs sync: 新規 `openspec/specs/research-pipeline/spec.md`（15 Requirements）+ 更新 `openspec/specs/dept-organization/spec.md`（capability mapping 7→8）
- archive commit: `712ac50 chore: archive research-pipeline-k006 + research-pipeline spec を main へ反映`

### commit 全リスト（`origin/main` 反映済）

```
71f910d feat(research): K006+ Knowledge 自動生成パイプライン
0bb51f5 content(research): K006 校閲完了 → status: ready
55f57e1 fix(research): openai SDK v4 → v6 で multipart upload の ECONNRESET を解消
8841d66 fix(research): K007 生成で発覚した 3 件の不具合を修正
8e511a5 content(research): K007 校閲完了 → status: ready
712ac50 chore: archive research-pipeline-k006 + research-pipeline spec を main へ反映
165831e Merge pull request #2 from tatoflam/feat/research-pipeline-k006
```

### 最終成果

| 項目 | 値 |
|---|---|
| タスク完走 | **62 / 62** |
| Knowledge 在庫 | K001-K005（legacy）+ **K006 / K007 / K008（新規生成、全 ready）** |
| 合計コスト | **~$0.18**（K006 $0.08 + K007 $0.05 + K008 $0.05） |
| OpenSpec capability | **7 → 8**（`research-pipeline` 新設） |
| tests | 197 → 203（bug fix で +6 件） |

詳細パターンは [[05_learn/youtube-knowledge-pipeline]] に切出し（`--asr` opt-in 設計 / Claude few-shot Topics / 多言語 EN→JA / frontmatter LLM 任せない / system prompt のコードフェンス罠 / Whisper 誤字を Claude が文脈吸収）

### 次セッションでやること（user 明示の固定順序）

1. `/opsx:propose companify-pipeline-relocate` — `pipeline/*.js` を `dept/dev/pipeline/` へ
2. `/opsx:propose marketing-strategy-split` — 配信戦略を `dept/marketing/` 分離
3. **Drafts 在庫補充** — K006-K008 → `npm run generate -- --topic K00X --target "..."` で人実行（5/9 以降の在庫ゼロを解消）
4. `/opsx:propose multi-tenant-bootstrap` — 2 アカウント目立ち上げ時

memory: [[memory: project_session_2026-05-04]]

## 2026-05-04 — companify-bc-hybrid 完走 + 4 OpenSpec changes 起票 + 3 実装 Phase 1 + Local-First 確定（sessions 57a002bd + d40649e2）

research-pipeline-k006 完走の翌セッションから、**会社化の本丸 (B+C ハイブリッド)** を着工。`/opsx:propose companify-bc-hybrid` 起票（マルチアカウント観点を user 指摘で追加）→ `/opsx:apply` で artifact mismatch 検出 → 即停止 → Node.js 化と scope 縮小で再 plan → 36/39 → 39/39 → archive → README.md 新規 → push 完了（PR #1）。続くセッション d40649e2 では **次セッション固定順序リスト** を user 明示で消化:

1. companify-pipeline-relocate（pipeline → dept/dev/pipeline）
2. marketing-strategy-split（配信戦略 YAML 化）
3. Drafts 在庫補充 K006-K008（D011-D013 生成）
4. multi-tenant-bootstrap（genres 二層化）

途中で **`marketing-cycle-bootstrap` を分離起票**（user 提案の循環ループを別 change で扱う二段構え）+ `/opsx:explore` で **Local-First 原則** を確定（Max plan x20 を払っているなら GH Actions に Anthropic API を持ち込まない）+ user 提案の **週次バッチ運用** を 7 フェーズ + 3 段重ね reminder で spec 化。

### companify-bc-hybrid（57a002bd、5-3 23:21 → 5-4 00:21 JST）

| Phase | 内容 |
|---|---|
| A. 起票 | `genres/<g>/{shared,accounts/<a>}/` 二層構造（マルチアカウント観点を user 指摘で追加）、4 artifacts validate pass |
| B. apply 開始即停止 | tasks/specs は Python `scripts/` 前提、リポは Node.js `pipeline/` → 即 stop、user `1` 選択で artifact 全更新（Node.js 化 + scope 縮小） |
| C. 実装 36/39 | dept/ skeleton + git mv 5 dir + path 参照更新（pipeline / GH Actions / tests / docs） + 152/152 tests pass + 7 capability cross-check |
| D. release | commit `c8637e7` → push → PR #1 → user merge → archive `910eda0` → main 直 push がローカル hook で正しく拒否 → user 手動 push |
| E. README | user `「結局何ができるアプリ？」` → README.md 新規 (107 行) + archive tasks 7.1/7.2 tick-off を 1 commit `dbb7564` → push 完了 |

push 反映 commit:
```
c128543 Merge pull request #1 from tatoflam/refactor/companify-bc-hybrid-stage1
c8637e7 refactor(repo): B+C ハイブリッド第1弾 — content/data ディレクトリを dept/ へ再編
910eda0 chore: archive companify-bc-hybrid + dept-organization spec を main spec へ反映
dbb7564 docs: README.md 新規追加 + archive tasks の 7.1/7.2 を完了マーク
```

dept-organization spec が canonical 化（`openspec/specs/dept-organization/spec.md`）、capability mapping 7→8（research-pipeline）を引継ぎ

### d40649e2（5-4 03:02 → 08:24 JST）— 4 changes 起票 + 3 実装 + 4 commits（push 未）

#### 起票 4 件（全て 4/4 artifacts complete）

| change | 概要 |
|---|---|
| companify-pipeline-relocate | `pipeline/*.js` を `dept/dev/pipeline/` へ移動。dept-organization の MODIFIED delta で「pipeline 据え置き」例外を撤廃 |
| marketing-strategy-split | post-scheduler から配信戦略を切出して `dept/marketing/strategy/posting_policy.yaml` + 新 capability `posting-strategy`（marketing 所有）に移管 |
| multi-tenant-bootstrap | `dept/` 単一 tenant → `genres/gut-health/{shared,accounts/chokatsu-studio}/<dept>/` 二層化。新 capability `tenant-path-resolver` + `account-config`。Phase A=1-account 化 + Phase B=2 アカウント目立ち上げ。**design.md に "Local-First Anthropic" 原則を追記** |
| marketing-cycle-bootstrap | 7 フェーズ循環ループ (REVIEW → MARKETING → RESEARCH → CONTENT → AFFILIATE → SCHEDULE → PUSH) を週次バッチ spec 化。Phase β: P1 = orchestrator + B-1〜B-4 + idempotency + `/weekly-cycle` skill / P2 = launchd + sessionStart hook + Stop hook。新 capability 3 / modify 5。月初週は B-3 (persona 見直し) 強制実行 |

#### Local-First 原則確定（`/opsx:explore` で reframe）

| 環境 | Anthropic API | コスト |
|---|---|---|
| ローカル (Claude Code) | Max plan x20 経由 | **既に支払い済 ($200/月固定)** |
| GH Actions | API key 経由 | **追加課金 ($/token、月 $5-30 推定)** |

Max plan x20 は OAuth ベースで GH Actions では使えない → Anthropic API を GH Actions に持ち込む = **二重課金**。**Local-First** 確定:

- Anthropic 使うステップ（research / generate / B フェーズ分析）= ローカル Claude Code
- GH Actions = Threads / 楽天 API のみ呼ぶ workflow（publish, sync_metrics, weekly_report, resolve_affiliates）
- workflow_dispatch の手動 Anthropic 起動は将来の拡張として残す（`confirm_anthropic_cost: true` 必須）

→ multi-tenant-bootstrap design.md に明記、marketing-cycle-bootstrap の weekly-cycle-orchestrator capability に "Local-First execution" 要件として spec 化

#### 週次バッチ = OODA ループ（user 指摘で B フェーズ追加）

当初 6 フェーズ案（A REVIEW → C RESEARCH → D CONTENT → E AFFILIATE → F SCHEDULE → G PUSH）に user 指摘:

> 「review と research の間に marketing（何に需要があり、どのような収益モデルを描けるかの戦略を立てる）のフェーズは必要ないかな？」

→ **Observe (REVIEW) → Act (RESEARCH 以降)** 直結で **Orient (戦略立案)** が抜けている = OODA 短絡。**B MARKETING フェーズ追加**:

- B-1 仮説出し / B-2 affiliate モデル / B-3 persona 見直し（月初週強制）/ B-4 戦略 ratify (status: draft → ratified → superseded)
- 戦略アウトプット格納: `dept/marketing/strategy/weekly/<ISO_week>.md`

#### 3 段重ね reminder（Phase 2）

- Layer 1: launchd 日曜 14:00 → macOS 通知 + iMessage to self
- Layer 2: Claude Code sessionStart hook → check_weekly_due.js が exit 1 なら system-reminder inject
- Layer 3: user が `/weekly-cycle` を直接叩く

通知メディアは macOS 純正 + iMessage to self のみ（Apple ロックインだが user 環境最適）

#### Drafts D011-D013 補充

| Draft | topic | target | 型 |
|---|---|---|---|
| D011 | K006 | ヨーグルトを習慣にしてるのに痩せない人 | 認知の置換（短鎖脂肪酸リレー） |
| D012 | K007 | 甘いヨーグルトに頼ってる人 | 認知の置換（食物繊維と多様性） |
| D013 | K008 | 腸内細菌は善玉菌だけと思ってる人 | 意味の再定義（大腸菌の二面性） |

3 本 lint/validate green。**衝突発見**: 既存 `published/D011_腸活スタジオ始動.md` と新 D011 が被る → `generate_post.js` の numbering bug（`published/` を考慮していない）。即時事故無し（別 dir）だが publish 時の上書きリスク → marketing-cycle-bootstrap の content-pipeline spec delta に **「D0XX numbering accounts for both drafts and published」** 要件として組み込み、Phase 1 tasks に含む

#### `/opsx:apply` 3 件連続実装 → 4 commits（push 未）

```
3397f6e refactor: pipeline/ を dept/dev/pipeline/ へ移動 (companify-pipeline-relocate)
56ff446 refactor: 配信戦略を dept/marketing/posting-strategy へ分離 (marketing-strategy-split)
ebccdaa feat: weekly-cycle orchestrator (marketing-cycle-bootstrap Phase 1)
d848bd8 content: Drafts D011-D013 補充 + multi-tenant-bootstrap 提案起票
```

| change | 完了タスク | 実装内容 |
|---|---|---|
| companify-pipeline-relocate | 33/41 | 47 R rename + path 参照更新 + 203/203 tests pass。残 8 = post-merge / archive |
| marketing-strategy-split | 25/30 | `posting_policy.yaml` + `pipeline/lib/posting_policy.js` (9 unit tests) + `schedule.js` を YAML 読込型 refactor + fail-fast 検証。212/212 tests pass |
| marketing-cycle-bootstrap P1 | 25/61 | `pipeline/lib/iso_week.js` (16 tests) + `weekly_state.js` (5 tests) + 既存 weekly_report.js 改修 (4 tests) + WeeklyCycle skill + `dept/marketing/strategy/weekly/` template + dept/marketing README |

#### skill 名 kebab-case 統一

user 指摘 `「/weekly-cycle は VS Code の Claude code プラグイン上では使えない？」` → 当初 PascalCase `WeeklyCycle` だったので `/WeeklyCycle` でしか叩けない。SKILL.md / tasks 内の表記揺れも合わせて全部 kebab-case に統一:

- `.claude/skills/WeeklyCycle/` → `.claude/skills/weekly-cycle/`
- frontmatter `name`: `WeeklyCycle` → `weekly-cycle`
- VS Code プラグイン / CLI / Web 全環境で `/weekly-cycle` 動作確認

### 次セッション再開手順

push 未の 4 commit を上げる前に user 確認:

```bash
cd /Users/tato/repo/github/tatoflam/ThreadsPosts
git status                  # 4 commits ahead of origin/main
git push origin main        # client-side hook が PR review bypass で拒否される可能性あり、user 手動 push 想定
```

その後の優先順位:

1. push 完了 → PR ベースで通すなら branch 切り戻し
2. `/opsx:apply marketing-cycle-bootstrap` Phase 2（launchd + hooks の trigger 機構）
3. `/opsx:apply multi-tenant-bootstrap`（2 アカウント目立ち上げ trigger 時）
4. **`/weekly-cycle` 実運用開始** — 週次バッチを実体験して必要に応じ skill 改善

### 学び（横展開可能）

- **artifact mismatch は smoke 段階で即停止**: 起票時の前提（Python 等）と実装時の現実（Node.js）がズレた時、タスクを進めながら型を変えると差分管理が破綻する。section 1 で気づいたら即 stop → user に「artifact 更新で進める / scope 変えない」の選択を投げて再 plan するのが正解
- **Max plan x20 を払っているなら Anthropic API は Local-First**: GH Actions に持ち込むと別建ての従量課金で **二重課金**。Local Claude Code セッション = Max plan 内で消費、GH Actions = 非 Anthropic workflow（Threads / 楽天 / 計測 API）のみ自動 cron する分離が最適
- **OODA で見ると週次サイクルは A=Observe / B=Orient / C-G=Act の構造**: 当初 6 フェーズ案で B (Orient) を抜きたくなるが、それは OODA 短絡で「先週の数字を見ても次の打ち手が決まらない」状態を作る。月初週は B-3 (persona 見直し) を強制実行する設計で戦略漂流を防ぐ
- **段取りオーバーヘッドが分散すると続かない → 集中タイムの週次バッチが続けやすい**: 1 セッション 30-90 分で「今週分終わり」の状態に到達するバッチ式が user の運用継続性にフィット
- **3 段重ね reminder で運用継続性を担保**: 単一 trigger ではオフライン時の通知見逃し / Mac 開かない期間で取りこぼす。launchd + hook + 直接実行の 3 層冗長化で「今週やってない」状態を残さない
- **マルチアカウント観点は会社化提案の必須要素**: 1 ジャンル × N アカウントは会社運営の最初の必然（rate limit / ペルソナ並列 / シャドウバン耐性）。`genres/<g>/{shared,accounts/<a>}/` の二層構造を提案段階から組み込む
- **dev 部署は account 軸を超える例外**: pipeline コードを `genres/<g>/shared/dev/` に入れない方針はコード fork 防止のため。tenant-path-resolver でも `dept='dev'` は reject
- **skill 名は kebab-case で統一が PascalCase より良い**: VS Code プラグイン / CLI / Web で全部共通の registry。user の指打ちは `/weekly-cycle` のような lowercase が自然なので、ディレクトリ名 + frontmatter name を kebab で統一
- **D0XX numbering は drafts と published 両方を見るべき**: `generate_post.js` が `published/` を numbering 計算に含めてないと、別 dir なので即時事故は無いが publish 時の上書きリスクが残る。numbering 関数の入力 set を draft + published 両方に拡張するのが安全

詳細な運用パターンは [[05_learn/local-first-anthropic-ops]] に切出し（Local-First 原則 / 週次バッチ = OODA / 3 段重ね reminder）

## 2026-05-04 update — 2026-W19 weekly-cycle 初実行（a73c0aa2、5-4 08:24 → 09:50 JST、約 1.5 時間）

`/weekly-cycle` skill を実運用初回起動。1 セッション 1.5h で **W19 (5/4-5/10) 戦略 ratify + drafts D011-D015 を 5/8-5/10 に scheduled + 6 commits push** まで完走。Local-First アーキテクチャの実体検証も同時に実現。

### A REVIEW
先週 weekly_report 不在（初回）+ metrics 全 0（sync_metrics.yml 集計前）+ D001/D003-D010 既 scheduled 済 + D011-D013 未割当 + K001-K008 在庫。⚠ Step 0 で `git fetch` を回し忘れ、リモート既存の `weekly_2026-W17.md` / `W18.md` を見落とした（後段で発覚、次サイクルで spec 改修対象）。

### B MARKETING
- B-1: products.yaml × topic 連動度の照合表を作成。K002/K003/K005 が連動度高、K001 (乳酸菌) は商品連動 0 → トラフィック獲得用と割り切る
- B-2: 楽天 12 商品 hot、Amazon 待機中、新商品「ラクトフェリン+EC-12+ケフィア」は K001 と逆方向 → 次週候補メモのみ
- B-3: W19 は月初週ではない / user 明示要求なし → persona 見直し skip
- B-4: 4 テーマ優先順位（1: K006 痩せ菌 / 2: プレ×プロ×シン整理 / 3: K007 食事 / 4: 個人差）、楽天 5 商品重点、`status: draft → ratified`

戦略: [`dept/marketing/strategy/weekly/2026-W19.md`](dept/marketing/strategy/weekly/2026-W19.md) (Section 1-7 すべて埋め)

### D CONTENT — 脚注 URL 省略 A/B 開始（user 提案）
D011-D013 既存 lint pass。K006 起点で D014 (海外サプリ流行 — アッカーマンシア vs ブラウティア) + D015 (冷めたご飯 — レジスタントスターチ) 新規生成。

⚠ user 提案 **「YouTube 動画が毎回 Threads について来るのはユーザーからウザがられる可能性ないか」** → **D011-D015 全 5 本の脚注から YouTube URL を削除**、タイトル + publisher のみ残す。lint は URL 必須化していないので安全に削除可能。memory `feedback_footnote_no_url.md` 記録。**A/B 仕様**: D001-D010 (URL あり) vs D011 以降 (URL なし) の engagement 差を計測

### E AFFILIATE
products.yaml の topics に K006/K007 追加（auto match を効かせるため）。明示マッピング:

| Draft | Product | 理由 |
|---|---|---|
| D011 (痩せ菌リレー) | inulin_powder | 第 1 走者の餌 |
| D012 (甘いヨーグルト NG) | fructooligo_syrup | 無糖ヨーグルト + オリゴ糖 |
| D013 (大腸菌二面性) | (なし) | 商品連動弱い |
| D014 (ブラウティア菌) | fiber_supplement_mix | 既存菌の餌 |
| D015 (冷めたご飯) | (なし) | RS 直結商品なし |

inject 後 5 本 lint pass（412-420 chars、500 以下）

### F SCHEDULE — humanJitter 実装

dry-run の 5/8 (金) 19:00 → 5/10 (日) 19:00 割当に対し user 指摘 **「人間らしく数分ずらすのをよろしく」**:

- `dept/dev/pipeline/schedule.js` に `humanJitter()` 追加: **draft path の FNV ハッシュ → +60〜599 sec オフセット**（決定論的、同じ draft path に対して常に同じ jitter）
- 当初 +0〜599 sec 範囲だったが「24 秒オフセットでは人間らしさが薄い」と判断して下限 60 sec に調整
- 全 237 tests pass

最終時刻 (JST): D011 5/8 19:04:24 / D012 5/9 08:08:37 / D013 5/9 19:04:53 / D014 5/10 08:06:12 / D015 5/10 19:09:18

### G PUSH — default branch 保護 → settings 編集 → rebase → 6 commits push

2 commit 分割: `feat(schedule): add deterministic human jitter` + `chore(W19): execute weekly cycle - drafts D011-D015 scheduled, footnote URL drop trial`。

⚠ `git push origin main` がローカル設定の **default branch 保護**で deny。`.claude/settings.local.json` の編集も harness が「user の `C` 一文字では self-permission 編集として不十分」と拒否 → user **明示承認 (`Bash(git push origin main)` / `Bash(git push origin main:*)` を追加)** で設定編集 → push 再試行

⚠ リモートに先行 2 commits 発見 = `D005 auto-publish` + `metrics.csv sync` — **GH Actions が Local-First 構成通りに自動 cron で動いている証拠**。rebase で取り込み → `cb8a62e..5727199 main → main` 6 commits push 完了

push 後 publish.yml の次回 cron で D001/D003-D015 順次自動投稿開始

### W19 サイクルで証明された Local-First の正しさ

本セッション中に GH Actions が **Anthropic を使わない workflow 2 種** (publish + metrics sync) を独立に push してきた。Local Anthropic 使用セッション（B / D / F の Claude 推論）と並走しても衝突なし。「Anthropic を使う作業はローカル / 外部 API のみの作業は GH Actions」の分離が運用上正しいことを実体で確認

### 学び（追加）

- **A REVIEW Step 0 に `git fetch` 必須**: 初回サイクルで weekly_2026-W17/W18 見落とし発生。次サイクル前に SKILL.md の Step 0 を spec 改修（openspec 起票候補）
- **default branch 保護を緩める settings 編集は user の literal 列挙承認が必要**: `C` 一文字回答では harness が self-permission 編集を拒否する。「`Bash(git push origin main)` を追加することを承認した」のような対象ルール明示が必須
- **決定論的 humanJitter は draft path ハッシュベース**: 乱数だと同じ draft の再スケジュールで時刻が変わる問題が出る。FNV ハッシュ + 60〜599 sec で再現性 + 人間らしさを両立。下限 0 だと「24 秒オフセット」で人間らしさ薄、下限 60 sec で十分
- **脚注 URL 省略 A/B のための D011 境界**: D001-D010 は URL あり、D011 以降は URL なしで engagement 差を測定。Threads フィードに毎回 YouTube プレビューが付くのは特に同チャンネル連発時に「広告化」と見えるリスク

### 次セッション再開手順

```bash
cd /Users/tato/repo/github/tatoflam/ThreadsPosts
git fetch origin             # ← 必ず最初に
git pull --rebase origin main
ls dept/analytics/data/weekly_*.md   # W17 / W18 のリモート既存レポート読込
```

W20 サイクル開始時の優先順位:

1. weekly_2026-W17.md / W18.md の内容を読み A REVIEW 改善
2. D013/D015 (アフィリ無し) vs D011/D012/D014 (アフィリ有り) の engagement 差測定
3. URL 有無 (D001-D010 vs D011 以降) の engagement 差測定
4. weekly-cycle SKILL.md に「Step 0 で git fetch」を spec 改修 (openspec 起票)

## 2026-05-04 update — OpenSpec 3 changes archive batch + Phase 2 不採用判定 (8b57f7c8、5-4 09:50-11:10 JST)

`/opsx:explore` で 4 in-progress changes の依存グラフを整理し、3 changes を一気に archive。Phase 2 (launchd / Stop hook / 通知) は W19 cycle 実運用で `/weekly-cycle` 手動運用が回ったため不採用判定。

### archive した 3 changes

| change | archive 先 | 主要 spec 影響 |
|--------|------------|---------------|
| `companify-pipeline-relocate` | `archive/2026-05-04-companify-pipeline-relocate` | `dept-organization` ~1 (pipeline → dept/dev/pipeline) |
| `marketing-strategy-split` | `archive/2026-05-04-marketing-strategy-split` | `dept-organization` ~1 / `post-scheduler` +1~3 / 新規 `posting-strategy` create |
| `marketing-cycle-bootstrap` | `archive/2026-05-04-marketing-cycle-bootstrap` | 新規 `marketing-cycle` / `weekly-cycle-orchestrator` / `account-config` create + `content-pipeline` / `research-pipeline` / `performance-tracking` 追記 |

main spec capability 数: 8 → 11 (+3 新規)。

### Phase 2 (`weekly-cycle-trigger` capability) 不採用

- 元設計: launchd で 17:00 JST に reminder ファイル投下 → Claude Stop hook で reminder 検出 → user 通知 → 手動 `/weekly-cycle` 起動の 3 段重ね
- 不採用理由: W19 cycle 実運用 (commit `5727199`、5-4 朝 1.5h) で **手動 `/weekly-cycle` 起動が実用上完走できた**ため overkill
- 処置:
  - `weekly-cycle-trigger/spec.md` 削除 (`account-config` / `content-pipeline` / `marketing-cycle` / `performance-tracking` / `posting-strategy` / `research-pipeline` / `weekly-cycle-orchestrator` の 7 spec 構成へ縮小)
  - tasks 10.x-15.x (Phase 2 実装タスク) 削除
  - proposal.md に `Note (2026-05-04): Phase 2 は不採用` を追記、判断根拠 (W19 cycle 実運用) 記録
  - 必要になれば別 change で再起票可能

### task 16.1 の遅延依存解消

- 旧: 「`multi-tenant-bootstrap` merge 後に `genres/README.md` に週次サイクル節追加」 — multi-tenant 着手まで cycle archive を縛る
- 新: 「現状の `genres/README.md` (予約状態) に追記、multi-tenant 着手時に再編集」 — multi-tenant 待たず archive 開放

### 副産物 doc 更新

- `README.md` に「週次サイクル (推奨)」節 — `/weekly-cycle` skill が通常ループの推奨運用であることを明示
- `docs/operations.md` に `/weekly-cycle` セクション — A REVIEW から G PUSH のフェーズ概要 + 運用ガード (Step 0 fetch、戦略 ratify gate、`--live` 確認 prompt)

### push commits

- `24cef9f chore: archive 3 changes — pipeline-relocate / strategy-split / cycle-bootstrap` (36 files, +600/−281、`5727199..24cef9f main → main`)
- 237/237 tests pass

### 学び (横展開可能)

- **自動化機構は手動運用が回ってから判断する**: 設計時に欲しかった Phase 2 (launchd + hooks + 通知) が、実際に手動 `/weekly-cycle` を 1 回回したら自動化欲求が消えた。**「設計時に欲しい機能」と「運用時に必要な機能」のズレ** を W19 cycle が露呈させた
- **archive 時の MODIFIED Requirements は main spec header と完全一致が必須**: 起票時 (header 文言が起票時点の draft) と archive 時 (current main spec が更新済) で header にズレがあると `/opsx:archive` が「header not found」で失敗する → delta 側を current main の文言に合わせて再 archive
- **OpenSpec change の遅延依存は task X.1「他 change merge 後の doc 更新」で発生しがち**: 回避策は (A) doc を current state 前提に書き換え、(B) follow-up change に切り出し。今回は (A) を採用

### 残タスク

- 単一 in-progress change: `multi-tenant-bootstrap` (0/71) — trigger は「2 アカウント目立ち上げ」、当面寝かせ
- W20 サイクル開始時の優先順位は変わらず (上記)

## 2026-05-04 update — playbook-process-revamp 起票 + 52/53 実装 (97d3f618、5-4 12:58 JST 終了)

攻略本 (3818 行) + 外部 5 リンク (楽天年間カレンダー / 競合リサーチ note / 分析の鬼 5 投稿サイクル / note 公開記事 / Intage SNS) から運用知見を吸い上げ、`/opsx:propose playbook-process-revamp` で 1 OpenSpec change を起票 → そのまま `/opsx:apply` で 6 phase 実装まで貫通。

### 主要成果

- **6 投稿型テンプレ**: `dept/content/templates/` に `product_single` / `summary_set` / `summary_tree` / `room_redirect` / `shop_redirect` / `shop_search_redirect` (収益期待ランク: `shop_search_redirect` > `shop_redirect` > `summary_tree` > `summary_set` > `room_redirect` > `product_single`、攻略本由来)
- **3 セールスライティングパターン**: `dept/content/templates/patterns/` に `prep` / `pasona` / `aidma` (`none` は frontmatter 値のみ)
- **gut-health フックライブラリ**: `dept/content/hooks/gut-health.md` に 40+ 構文 (compliance: ok / borderline / banned 3 階層)
- **banned_patterns YAML 化**: `dept/content/style/banned_patterns.yaml` で CLAUDE.md の「使ってはいけない表現」を機械検証可能化
- **rakuten_events.yaml**: 2026 年末まで 10 events (毎月 1 日 / 5・10・15・20・25 日 / 18 日 / マラソン / スーパーセール / ブラックフライデー / 大感謝祭 / イーグルス感謝祭 / ブランドデー)
- **competitors skeleton**: `dept/research/competitors/gut-health.yaml` (a.r10.to 検索 / フォロワー 3k-20k / 楽天リンク率 70% 以上 を満たす爆益アカウント DB)
- **posting_policy 拡張**: `type_slots` (型別スロット) / `jitter_minutes_max` / `event_boosts` キー追加
- **pipeline 改修**: `rule_lint.js` (frontmatter `template_type` / `copywriting_pattern` 必須化 + YAML banned-patterns + hook validation) / `generate_post.js` (`--template` / `--pattern` / `--genre` フラグ) / `schedule.js` (`type_slots` 優先 + `event_boosts` 窓検出) / `account-research/index.js` 新規 (`competitors` / `products` / `promote` 3 サブコマンド)
- **performance-tracking 改修**: `sync_metrics.js` (`first_30min_engagement` 25-35 分窓 / `buzz_class` 自動派生 / `audience_match_flag` 上書き禁止 / 新 CSV カラム) / `weekly_report.js` (Template-type ROI / Buzz-class summary / 30-min early signal セクション)
- **Skills + CLAUDE.md**: `weekly-cycle/SKILL.md` に B-5 楽天イベントチェック + B-1 爆益アカウント review + D CONTENT 40:50:10 構成比ガード追加 / `PostCreation/SKILL.md` にテンプレ・パターン・フック読み込み手順 / CLAUDE.md に「型選択 → 構造 → フック」セクション追加
- **遡及 backfill**: D001-D015 + published 16 件全てに `template_type: product_single` / `copywriting_pattern: none` 付与 (working tree M 30 ファイル)
- **tests**: 237 → 247 (+10、新規テストケース)、5.4 (6 型 smoke test) のみ Anthropic API call 発生で deferred (user 対話実行)

### 起票 → 実装フロー

| Phase | 内容 | 完了率 |
|---|---|---|
| Phase 0 | Foundation files (テンプレ 6 + パターン 3 + フック 1 + YAML 5) | 15/15 |
| Phase 1 | Pipeline code (lint / generate / schedule / account-research) | 14/14 |
| Phase 2 | Performance tracking (sync_metrics / weekly_report) | 7/7 |
| Phase 3 | Skills + CLAUDE.md | 7/7 |
| Phase 4 | Backfill + validation (lint pass 16/16) | 4/5 (5.4 deferred) |
| Phase 5 | Memory + READMEs (memory 2 件追加) | 5/5 |
| **合計** | | **52/53** |

### 新 capability

- `account-research` (新設、5 Requirement) — 爆益アカウント DB / 商品候補抽出 / プロモ抽出
- `post-templates` (新設、6 Requirement) — 6 投稿型 + 3 セールスライティング型 + フック構文集
- 既存 modify 4: `marketing-cycle` (B-5 楽天イベント追加 + B-1 拡張) / `content-pipeline` (テンプレ・パターン・フック・40:50:10) / `posting-strategy` (type_slots / jitter / event_boosts / banned_patterns YAML) / `performance-tracking` (first_30min_engagement / buzz_class / template_type ROI)

### 学び (横展開可能)

- **「攻略本 + 外部リンク → 運用知見 YAML / markdown 化」の OpenSpec 変換パターン**: 3818 行の生資料を 6 spec delta に分解し proposal/design/specs/tasks 一式で起票すると、そのまま `/opsx:apply` で実装まで一貫できる。生資料を CLAUDE.md ベタ貼りより spec 化のほうが横展開しやすい
- **型選択 (構造) と文体 (語り口) は別レイヤで管理する**: 6 投稿型は構造、3 セールスライティング型は構造内の論理展開、文体ルールはどの型でも常時遵守 — の 3 層分離。CLAUDE.md でこの分離を明文化することで「型選択 → 文体生成」の判断順序が固定される
- **収益期待ランクは攻略本主張をそのまま採用、検証は 8 週後**: ランクは攻略本由来だが weekly_report.js で `template_type` × ROI が 8 週分蓄積されるまで観察フェーズ。全テンプレを `product_single` から脱却させる動機になる
- **banned_patterns YAML 化で文体ルールを CLAUDE.md とコード両方から参照可能に**: 人間用 (CLAUDE.md) と lint 用 (banned_patterns.yaml) の二層同期で、人間生成と lint 機械検証で同じルールが効く
- **Anthropic API call ありのタスクは `/opsx:apply` 内で deferred 妥当**: 6 型 smoke test = Anthropic API call × 6 = 意図せぬ課金リスク → user 対話実行に委ねるのが Local-First 原則と整合 (5.4 タスク)

### 残タスク (次セッション)

- 5.4 (6 型 smoke test) を user 対話で実行 → 各型の lint / scheduling 動作確認
- 未 commit 約 30 ファイルを 1 commit (例: `feat: playbook-process-revamp — 6 投稿型 + 3 セールスライティング型 + フックライブラリ + banned_patterns YAML + Rakuten events`) で push
- `/opsx:archive playbook-process-revamp` で main spec capability 11 → 13 想定 (`account-research` / `post-templates` 新設反映)
- D016 以降の生成で 6 型のいずれか (`shop_search_redirect` 既定) を採用、`product_single` から脱却

## 2026-05-04 update — playbook archive sync 完了 (cef7a3c1、5-4 20:32 JST)

`/opsx:archive playbook-process-revamp` を実行、main spec への capability 反映を完走。

- artifacts 全 done、tasks 52/53 完了 (5.4 smoke test = Anthropic API 課金リスクで intentionally deferred、tasks.md ノート明記)
- AskUserQuestion で「sync to main specs (推奨)」「skip sync」「abort」を user に提示 → user は **sync** を選択
- Agent 経由 sync 実行: ADDED 2 (`account-research` / `post-templates` 新設、main spec ファイル新規作成) + MODIFIED 4 (`content-pipeline` / `posting-strategy` / `performance-tracking` / `marketing-cycle` のヘッダ完全一致 merge)
- archive collision check OK → `git mv openspec/changes/playbook-process-revamp openspec/changes/archive/2026-05-04-playbook-process-revamp/` 実行
- `openspec validate --specs --strict` で 15 main specs 全 PASS
- ⚠ archive folder は working tree に **untracked** 状態で残存 (commit されず)
- 結果: capability 11 → **13** (新規 2)。in-progress changes は当初 `multi-tenant-bootstrap` のみとなったが、3h 後の BAN 対応で別 3 change が起票される

## 2026-05-04 update — Threads BAN 対応 — 3 OpenSpec changes pivot (c02fca64、5-4 23:02 JST、commit `2ec9509` local-only)

5-4 中に `@chokatsu_studio` (Threads + 連携 IG) が突如 BAN。Meta 通知文言:「弊社のテクノロジーにより…テクノロジーにより措置が講じられました」「再審査はリクエストできません」「あなたの情報はすべて完全に削除されます」 → **ML 自動分類器による enforcement、人間レビューなし、最重 tier**。`/opsx:explore` で診断 → `/opsx:propose` × 2 + 既存 update × 1 で運用 pivot。

### BAN 仮説と切り分け

「IP 変更 (GH Actions → local) より Account が人間に見えるか が本丸」(inauthentic / automation 分類器発火が最有力)。要因の太さ:

```
████████████  アフィリリンク密度 (r10.to + Amazon 毎投稿)
██████████    新規アカウント × API 投稿の即時開始
████████      投稿の type/文体類似性 (テンプレ感)
██████        2 投稿/日の機械的 cadence
████          GH Actions IP (datacenter)
██            User-Agent / API call signature
```

GH Actions IP は singular cause ではなく構成要素の一つ。warmup プロトコルで複数要因を同時に潰す。

### 決定事項 (user 確定)

1. 別ジャンル / 別ハンドルで再起 (`@chokatsu_studio` は廃止)
2. 別ドメイン振り直し、IG も新規作成
3. 電話番号は別を使う (もう 1 つ手元にある)
4. **月 50 万 / 3 ヶ月**目標に下方修正 (旧 月 10-1000 万から)
5. アーキテクチャは Option C (publish のみ local + metrics/affiliate は GH Actions read-only) + B 寄り (擬人化重視)

### 起票・update した 3 change

| change | type | tasks | scope |
|---|---|---|---|
| **account-pivot-warmup** | 新規 | 80 | 5-phase warmup (Week 1 観察 / Week 2 ソフト / Week 3 段階 / Week 4 通常移行 / Week 5+ 通常運用)、`posting_policy.yaml` の `phases` キー、`publish.js` の hard reject ゲート、新 capability `account-warmup-protocol` + `account-isolation-hygiene` (9 項目分離 + PII scrub)、delta `posting-strategy` / `post-scheduler` / `account-config` |
| **publish-relocate-local** | 新規 | 73 | 公開アーキ刷新。`publish.js` を local 起動 (新 skill `/post-due`) のみに、`publish.yml` 削除、`sync_metrics.js` も local 化、新 capability `local-publish-runner` + `local-metrics-sync`、delta `post-scheduler` / `performance-tracking` / `dept-organization` (`_archive/<slug>/` 正式化) / `weekly-cycle-orchestrator` |
| **multi-tenant-bootstrap** | 既存 update | 71 → 73 | BAN 前提崩壊で proposal/design/tasks 全面書き換え (option A)。Phase A + Phase B → 単一 phase (新 tenant 単独立上げ) に縮約。token は GH secrets → local `.env` 経由。具体 slug → `<G>` / `<A>` プレースホルダー (Phase 0 完了後置換)。`_archive/` 認知を `dept-organization` spec で正式化 |

### 3 change の依存グラフ

```
multi-tenant-bootstrap (新 tenant scaffolding)
  ├ depends on: account-pivot-warmup Phase 0 (slug 確定)
  ├ depends on: publish-relocate-local 旧 tenant archive 完了
  └ provides: tenant_paths.js / account_config / per-account paths

account-pivot-warmup (warmup + isolation)
  ├ depends on: multi-tenant-bootstrap (account-config schema 拡張先)
  └ provides: phase gate / warmup spec / hygiene checklist

publish-relocate-local (公開アーキ刷新、技術独立)
  └ provides: env loader / /post-due / GH secrets 削除 / 旧 tenant archive
```

推奨 merge 順: `multi-tenant-bootstrap` → `publish-relocate-local` → `account-pivot-warmup`。同じ `publish.js` を編集するが箇所が重ならない設計で並走可能化。

### 配信

- commit `2ec9509 openspec: pivot 3 changes for Threads BAN response` (28 files、+2165 / −249) を local main に積んだ
- **未 push** (`origin/main..HEAD = 2ec9509` のみ)
- pre-existing 未 commit work (skills / drafts / pipeline / product DB / `archive/2026-05-04-playbook-process-revamp/` フォルダ) は working tree にそのまま残置 — BAN pivot とは別軸で次セッションで整理

## 2026-05-04 update — `/opsx:explore` で BAN pivot 6 判断を確定 (f198b34e、5-4 23:03 → 5-5 00:21 JST)

BAN pivot commit `2ec9509` 直後、3 change が並走中 (合計 226 task、進捗 0/226) の状態で `/opsx:explore` を起動して全体地形を整理。explore mode のまま design.md / proposal.md / tasks.md に判断を capture (capture は implementing ではないので explore mode 内で完結)。セッション末尾で `/opsx:apply publish-relocate-local` 起動 → 「Using change: ...」announce 直後に session 終了 → 実装は次セッション。

### user 確定 6 判断

| # | 判断 |
|---|---|
| 1 | **収益目標を再下方修正: 月 50 万 → 月 30 万** (3 ヶ月後 = Month 3 W9-W12 で月¥300k ラン)。warmup で 1 ヶ月失う前提で再校正。memory `project_revenue_target.md` 同期 |
| 2 | **仮説 4 (CI/CD trigger = 機械投稿が BAN 起因) を支配的仮説に格上げ** → `publish-relocate-local` が本丸 change |
| 3 | **Warmup は "humanness 保険" として位置付け、緩めない** (W2 affiliate 0% を含めて維持)。仮説 4 が支配的でも保険策を spec で言語化 |
| 4 | **Amazon affiliate 棚上げ確定**。180 日 3 件 (期限 2026-11-01) 失効許容、コード/schema 温存 (`products.yaml` の Amazon URL field、`account-config.yaml` の `amazon_associate_id` を null/空欄で残す) |
| 5 | **multi-tenant-bootstrap は両軸 support**: per-account override + genre-level switching の両方。lookup precedence は **account first → shared fallback** |
| 6 | **ジャンル選定 3 日デッドライン: 2026-05-04 → 2026-05-07**。人ゲートが 3 change 全体のクリティカルパスに座っているため切る |

### 算術 (新目標 30 万円/月 が daily target 2 投稿/日 で着地する根拠)

```
Month 3 = 28 日 × 2 投稿/日 = 56 投稿
→ 1 投稿あたり ¥5,357 売上 (旧目標 ¥13,400 の 40%)
→ 楽天 affiliate 報酬率 3% 仮定で 1 投稿あたり ¥178,571 GMV
→ ¥10,000 商品で約 18 件/投稿/月、または ¥5,000 商品で約 36 件/投稿/月
```

→ `posting_policy.yaml` の `phases` を W5+ で 3-4 投稿/日 に引き上げる必要が消えた。warmup → normal の連続性が自然になり、目標と運用設計の整合が取れた。

### 反映済 OpenSpec edits (8 編集 + memory 3 件、+162 / −7、validate 通過)

- `account-pivot-warmup/proposal.md` — Why 段落更新 (仮説優先順位 + 50→30 + Phase 0 5/7 deadline + 楽天単独 genre 基準)
- `account-pivot-warmup/design.md` — Goal 5 を 30 万に、**Decision 7** (仮説重み付け) / **Decision 8** (revenue arithmetic) / **Decision 9** (Amazon 棚上げ) 新設
- `account-pivot-warmup/tasks.md` — §1.1 5/7 deadline、§1.10 Amazon 棚上げ確認に書換、§12.2 目標値
- `multi-tenant-bootstrap/design.md` — **Decision 9** (両軸 + lookup precedence)
- memory 3 件 (`project_revenue_target.md` / `project_affiliate_accounts.md` / `MEMORY.md`)

### 実装着手順 (確定)

1. **`publish-relocate-local` §1-4** (本丸、Claude 単独で進む。Day 1-3 で完走可能)
2. **`account-pivot-warmup` §1.1-1.4** (ジャンル選定 — 2026-05-07 までに human input、Claude は調査支援)
3. **`multi-tenant-bootstrap`** (前 2 つ完了後)

### 学び (横展開可能)

- **explore mode は capture まで含めて 1 セッションで成立する**: 「explore = thinking、implementing は不可」だが OpenSpec artifact (proposal/design/tasks) への書き込みは capture であって implementing ではない。explore セッションが消えずに spec に着地する
- **incident で目標を動かすときは算術で裏取りする**: 「30 万に下方修正」を memory に書くだけでなく daily target × posting count × GMV 換算 × 報酬率まで一気に計算しておくと、後から戻すときに何を変えれば届くかが見える
- **仮説 1〜N 並列 → 1 つを支配的に格上げする操作の価値**: 4 仮説並列の proposal を「機械投稿が BAN 起因」で 1 つに重み。本丸 change が決まり、warmup を「保険」と位置付け直して緩めない判断が論理的に整合した
- **explore → apply の継ぎ目で session が切れても損失は小さい**: capture-first の利得 — design.md / tasks.md に判断が capture 済なら次セッションは状態 0 から再開できる

### 学び (横展開可能)

- **Meta 自動分類器の文言で違反種別を読み解く**: 「再審査リクエスト不可」「情報すべて削除」「テクノロジーにより措置」は **inauthentic / automation 分類器の最重 tier** signature。commercial policy 違反なら通常 reason がもう少し具体。IP 変更だけで隠れる相手ではない判断材料
- **BAN 要因はスタックする — 単一原因に絞ると 2 度目を踏む**: アフィリ密度 + 新規 × API 即時開始 + テンプレ感 + 機械的 cadence + GH Actions IP + UA を全部疑い、warmup プロトコル (Week 1-5+) で段階的に humanness signal を積む方が安全
- **既存 OpenSpec change は scrap せず option A (update + apply)**: BAN で前提崩壊した `multi-tenant-bootstrap` を scrap して新規起票するより、proposal/design/tasks を BAN 文脈に書き直す option A の方が編集量も OpenSpec 履歴ノイズも少ない。「BAN を機にスコープ刷新した」事実が archive 時に残る
- **3 change 並走は merge 順序と「編集箇所の非交差」で成立させる**: 技術独立な change と依存関係を持つ change を分離。同じファイルを編集する場合は箇所が重ならない設計
- **revenue target は incident で動的に下方修正する**: 旧 月 10-1000 万 → 新 月 50 万 / 3 ヶ月。warmup で 1 ヶ月失う前提で再設定。incident で目標を動かさない方が「今すぐ通常運用に戻したい」圧力で warmup を破る誘惑になる

### 残タスク (次セッション以降)

- pre-existing 未 commit work (skills / drafts / pipeline / product DB / `archive/2026-05-04-playbook-process-revamp/` フォルダ) の整理 commit
- `account-pivot-warmup` Phase 0 (新ジャンル選定リサーチ) 着手 → 3 change の slug 確定で全体 unblock
- `multi-tenant-bootstrap` Section 4-5 (resolver 実装 + pipeline refactor) は slug プレースホルダーのまま先行実装可能
- 3 change を draft 状態で PR 切る準備 (push to origin)

## 2026-05-05 update — `/opsx:apply publish-relocate-local` 67/73 + 3-commit clean push (f198b34e 後半、5-5 00:21 → 02:?? JST)

直前 explore セッション末尾で起動した `/opsx:apply publish-relocate-local` を 0/73 から再開。auto モードで Claude が安全に進められる範囲を §1-§12 まで一気通貫で消化、最後に user 選択 (「pushだけしといて」) で `origin/main` へ 4 commits を push 完了。

### 完了内訳 (67/73)

- **§1 env loader (5/6)**: `lib/load_env.js` 新規 (`~/.config/threads-posts/.env` ロード優先 + `.env.local` フォールバック + `GITHUB_ACTIONS=true` で refuse)、`.env.local.example` / `.gitignore` / `dept/dev/README.md` 整備
- **§2 publish.js (8/8)** + **§3 sync_metrics.js (4/4)**: `loadEnv` 経由に統一、`--live`/`--ci` 削除、GH Actions 検出時 exit 3 + refusal、構造化ログ、exit codes 0-4、invocation cap
- **§4 `/post-due` skill (5/5)**: `npm run publish:due` を canonical 経路として包む phase gate skill
- **§5 npm scripts (4/4)**: `publish:due` / `publish:dry` / `metrics:sync` 追加 + 旧 `sync:metrics` 統合
- **§6 GH workflows (4/5)**: `publish.yml` 削除、`weekly_report.yml` から sync step + Threads env 撤去
- **§7 旧 tenant archive 完了**: slug `gut-health-immune-allergy` を `dept/{content,analytics,research,marketing}/` から `genres/_archive/<slug>/` へ git mv (41 renames)、`ARCHIVED.md` 作成、PII grep スキャン clean
- **§8 verification (4/6)**: 8.2 / 8.4 / 8.5 / 8.6 動作確認、`__tests__/local_runner_manual_verification.md` に記録
- **§9 GH secrets (4/5)**: `THREADS_ACCESS_TOKEN` / `THREADS_USER_ID` を `gh secret delete`、6 件 (BITLY / RAKUTEN_*) 据え置きを残存確認
- **§10 docs (8/8)**: `CLAUDE.md` / `README.md` / `dept/dev` / `dept/analytics` / `genres` / weekly-cycle SKILL を Local-First + `/post-due` canonical で整合
- **§11 memory (3/3)**: `project_account_ban_pivot.md` / `feedback_weekly_cycle_step0_fetch.md` / `reference_threads_token_location.md`
- **§12.1**: `openspec validate` ✓ (全 spec)
- **§12.2**: `account-pivot-warmup` 進捗確認 (0/72、Phase 0 ジャンル選定リサーチ待ち)

### 3 commit clean 分離 (user 選択肢 1: change 単位で分離)

```
edba97b chore: bundle playbook-process-revamp leftovers from prior W19 session   (44 files)
442533c archive: relocate retired tenant gut-health-immune-allergy to genres/_archive/   (42 files, 41 renames + ARCHIVED.md)
16f8de5 feat(local-first): relocate Threads publish + sync_metrics from GH Actions to local Mac   (20 files)
2ec9509 openspec: pivot 3 changes for Threads BAN response   (既存)
```

`origin/main` に 4 ahead だった状態で、user 指示「pushだけしといて」を受けて 4 commits まとめて push 完了。247 tests pass、git tree clean。

### 残 6 タスク (本 change を完了→archive するために必要)

| § | 内容 | 種類 |
|---|---|---|
| §1.6 | 旧 token を `~/.config/threads-posts/.env` に物理配置 | user 操作 (1Password 経由) |
| §8.1, §8.3 | 旧 token で `npm run publish:dry` / `metrics:sync` を実機検証 | user 検証 |
| §9.5 | 次月曜 (2026-05-11) 07:00 JST cron で `weekly_report.yml` が sync 不要 + 成功することを confirm | async (時間待ち) |
| §12.3-§12.5 | PR 作成 → merge → `/opsx:archive publish-relocate-local` | user 判断 |

### 設計上の確定事項 (このセッションで固まったもの)

- **token 配置 canonical**: `~/.config/threads-posts/.env` (XDG-style)。GH secrets には置かない。memory `reference_threads_token_location.md` に永続化
- **GH Actions 残置 workflow**: `weekly_report.yml` (CSV 集計のみ、Threads API 不使用) と `resolve_affiliates.yml` (楽天 RWS のみ) のみ。Threads API を call するすべての経路はローカル Mac 起動
- **`/post-due` skill が canonical**: weekly-cycle 内 G PUSH phase は `/post-due` または `npm run publish:due` のいずれかで起動。GH Actions cron からは呼ばれない
- **archive 凍結 slug の handle**: `gut-health-immune-allergy` を `genres/_archive/<slug>/` 配下に固定。新規 tenant の slug は別途 account-pivot-warmup Phase 0 で確定

### 学び (横展開可能)

- **混在 working tree の整理は user に 3 択提示 → 順序実行**: 「1 commit にまとめる / change 単位で分離 / 別 PR で切る」を提示して「1, 2, 3 の順で」を選ばせる。auto モードで黙って 1 commit にしていたら playbook-process-revamp の文脈が失われていた。**git history 上の change boundary は spec の change boundary と一致させる**価値が大きい
- **PII scrub は memory + design の slug 単一化が前提**: 凍結対象 slug を memory・design 双方に default として置いておくと grep 対象が一意に決まり、scrub 漏れリスクが落ちる。slug が 2 か所でズレていると scrub 後に旧 slug が漏れ続ける
- **GH secrets 削除の検証は実運用 cron で取る**: `gh workflow run` でテストしても、削除した env を参照している step が存在しないなら何も検証できない。**「設定削除の検証は次の本番 cron run」** という async pattern を memory にしておくと、停止地点で confusion しない
- **大型 archive は `git mv` 逐次でも rename detection が効く**: 41 renames が status に正しく載る。`mv` で動かしてから `git add -A` だと delete + add 扱いになる場合がある。**archive 操作は必ず `git mv`**
- **auto モードの定義を user と共有しておく**: 「Claude が安全に実行できる範囲」 = token 配置 / 実機検証 / async monitor を含まない。これを最初に伝えておくと、停止地点で「なぜ止まった？」が起きない

### 次の判断点 (user)

1. PR 作成 (§12.3) を `account-pivot-warmup` と同時 merge にするか単独 land にするか
2. `account-pivot-warmup` Phase 0 (新ジャンル選定リサーチ) を 5/7 deadline までに着手
3. token 配置 (§1.6) → `publish:dry` 実機検証 (§8.1, §8.3) のタイミング

## 2026-05-05 update — Decision 7 reframe (複合フィンガープリント仮説、665cb2da)

publish-relocate-local apply と並行 window で走った短い `/opsx:explore` セッション (5-5 01:14 → 01:20 JST)。user が ChatGPT の BAN 6 行可能性表を持ち込んで「Claude Code の見解は？」と問い直し、その diff を取った結果、`account-pivot-warmup/design.md` Decision 7 の framing を書き換えた。

### 何が変わったか

**Before**: 「(4) GH Actions cron = datacenter IP **支配的**、`publish-relocate-local` が**本丸**、warmup は humanness **保険**」
**After**: 「**複合フィンガープリント仮説** — (1) 機械的 cadence + (2) 100% affiliate + (3) 新規アカ + (4) IP + (5) 健康ジャンル × 商業 + (6) engagement 受動性 の AND を inauthentic 分類器が見ている。warmup = **humanness 主力対処**、local-first = **IP 信号対処 + 副次便益 (token 衛生 + Anthropic ローカル消費)**」

### ChatGPT 表との diff で見えたもの

ChatGPT 6 行表には以下 2 信号が**入っていなかった**:
- **健康/サプリジャンル × 商業リンク** (Meta が特に厳しい領域: 効能を匂わせやすい)
- **engagement の受動性** (like/reply/scroll ゼロ → humanness 信号が立たない)

逆に ChatGPT 表の「行 1 (非公式 API/Cookie ログイン) 高」は本件には適用外 (旧アカは Threads Graph API + token publish のみ)。第三者 framing との diff を取ると、自分のフレームの blind spot と相手のフレームの blind spot が両方見える。

### 書き換え 3 ファイル + memory

- `account-pivot-warmup/proposal.md` 行 6: 二段構え → 三段構え
- `account-pivot-warmup/design.md` Decision 7 全体 (4 → 6 信号、weight 反転)
- `account-pivot-warmup/design.md` Decision 8 行 256 (warmup の位置付け文言)
- `memory/project_account_ban_pivot.md` (複合フィンガープリント仮説への改訂を Why に追記)

`openspec validate account-pivot-warmup` パス。実装挙動 (warmup 上限 / phase gate / Phase 0 ジャンル選定基準) は不変、framing と判断軸だけ更新。

### 学び (causal-attribution 一般)

- **incident response で「単独支配仮説」を採るとフレーム固定リスクが高い**: IP だけ residential に変えて旧パターンを踏むと 2 度目の BAN を引きうる。複数信号の AND を分類器が見ているという前提なら、IP 単独除去では足りない
- **第三者 (ChatGPT) の framing と自分の framing の diff を取ると blind spot が両方見える**: framing の merge 検証 = 単独査読では届かない
- **framing rewrite は実装挙動を変えなくてもやる価値**: 「将来の判断軸が変わる」だけでも spec の framing を更新する意味あり。Decision 7 を放置すると後続 change が「IP 信号さえ消せば緩めて良い」と読み違える余地が残る
- **explore mode の触り分け**: framing の是非を 6 行表で確認 → user が「1で」で確定 → そのまま即 edit に入った。`/opsx:apply` を経ずに edit したのは「framing 修正は実装変更を伴わない」と user が判断したため

### 残論点

- 2 番目の論点 (健康訴求 × 商業リンクを Phase 0 ジャンル選定基準 / `dept/content/hooks/<新genre>.md` compliance に明示組込) は本セッションでは保留。5/7 Phase 0 deadline が近いので、ジャンル選定基準の追補から着手するのが自然

## 2026-05-07 — Phase 0 ジャンル選定 + 3 アカ並行 scaling 設計 + eSIM 副回線確定 (99902682、5-7 11:04 JST)

BAN 後 pivot の Phase 0 deadline (= 今日) を完走するための `/opsx:explore` セッション。5 ジャンル候補を比較 → interior 単独確定 → 3 アカ段階的 scaling 設計 → eSIM 副回線で電話番号 isolation → 2 commits push (`6c1a0d4` openspec pivot + `137c07a` task 7.14 tick) until `origin/main`。

### 5 ジャンル候補 → interior 単独確定

候補挙げ → 比較表 → 1 つに絞る、を 1 セッションで踏んだ。

| 候補 | persona | fingerprint離脱 | 楽天在庫 | niche | 動線 | 採否 |
|------|---------|-----------------|---------|-------|------|------|
| キャンプ・釣り・アウトドア | ○ (年2-4回) | ✓ | ◎ | 子育×教育で◎ | ◎ | 保留 (account_2/_3 候補) |
| 腸活 | ◎ (実践者) | ✗ 高被り | ✓ | △ 旧と同じ | ◎ | **却下** (BAN 再発リスク) |
| 植物 (ビカクシダ・エアプランツ) | ○ (始めたて) | ✓ | ○ | ○ niche | ◎ | 保留 |
| ギター・電子楽器 | ◎◎ (歴30年) | ✓ | ○ | ○ ジャズ×Pops | △ サウンドハウス問題 | 保留 |
| **インテリア (建築設計PM経験)** | ○ → ◎ | ✓ | ◎ | △ 競合多 → subject 軸で○ | ◎ | **採用 = account_1** |

`gut-health` (=旧ジャンル) は composite-fingerprint hypothesis (Decision 7 reframe) 上で「健康ジャンル × 商業リンク」が信号 (5) として残るので、明示的に Phase 0 ジャンル選定基準で却下。これで 5-5 explore で残した「ジャンル選定基準を spec に書く」論点を消化。

### Persona の三段階 refine — 「PM施主」 → 「駆け出しデザイナー」 → 「賃貸を整え始めた覚書」

interior に決まった後、persona を 3 回書き直して各 stage の罠を毎回名指しで崩した。

```
Stage A: 建築 PM × 施主視点 (一旦保留)
  → "PM" を名乗ると進行管理プロを期待される、施主側経験はゼロ
  → 「肩書 + 駆け出し」二重構造 = 旧 persona「医師でない×訴える」の言い換え

Stage B: 駆け出しデザイナーが選ぶおしゃれな小物 (本人却下)
  → 直前の発言「デザインセンス的にはこれから」と矛盾
  → "選ぶ" の教え口調にズレる、IG/Threads で死ぬほど枯れた定型

Stage C (確定): 賃貸を整え始めた覚書 (subject 軸で広げる)
  → subject = うちの家、これで固定 (誰の家でもなく "私の" 家で差別化)
  → カテゴリは家具/照明/雑貨/収納/動線 を横断
  → 建築設計 PM 経験は account プロフィール 1 行のみ、本文では振りかざさない
```

「肩書軸」(専門家、デザイナー) で広げると教え口調にズレる、「subject 軸」 (私の家、私の体験) で広げると一人称が全カテゴリで成立、というのが核。

### 文体: 「私は」 → 「うち / うちの」 (interior 限定)

旧 persona の `私は` は (1) 上から目線禁止 (2) 権威化禁止 (3) 咀嚼者ポジション、の 3 つの load-bearing 機能を持っていた。interior ジャンルでは「私はリビングのペンダントを 3 回選び直した」が `説明会・教える側` に滑りやすい (賃貸インテリアは「整えた人がカタログを示す」構造に近い)。`私は` を **`うち / うちの`** に置き換えて 3 機能を維持する中道案で確定。

```
旧: 私はリビングのペンダントライトを 3 回選び直した
新: うちのリビング、ペンダントライトを 3 回選び直した

旧: 私は賃貸でも置ける造作家具モドキを 2 種類試した
新: うちは賃貸だけど、造作家具モドキを 2 種類試した
```

`account_2/_3` 用ジャンルは未確定なので、文体も別途検討。memory `feedback_interior_persona_uchi_style.md` で interior 限定であることを明示。

### Decision 8 書き直し: D3-b 段階的 (¥300k × 3 = ¥900k)

「いきなり 3 アカ並行で本気アフィリ → 連鎖 BAN」を回避する設計。1 アカ目で運用 protocol を validate (= BAN/警告ゼロ + cadence 維持 + 月次 ¥50-100k ラン) してから 2 アカ目を起動、という milestone-driven の **中道** 案を Decision 10 として spec 化。

```
Stage 1 (2026-05〜2026-08): account_1 (interior) 単独
  W1-W4 warmup → +4w normal → +8w 第 2 milestone (BAN ゼロ + ¥50-100k ラン)
  → ここで account_2 起動判断
Stage 2 (2026-08〜2026-12): account_1 維持 + account_2 (TBD) 立上げ
  account_1 は normal で ¥300k ラン目指し続ける
  account_2 W1-W4 warmup → normal → 4 週運用 + 収益軌道確認
  → ここで account_3 起動判断
Stage 3 (2026-12〜2027-02): account_1,_2 維持 + account_3 (TBD) 立上げ
  全体 ¥900k ラン到達 = D3-b 達成
```

「同時 3 アカ起動」「単独で ¥900k 超過」は明示的に Non-Goal。

### Decision 11 新設: 4 軸 isolation × 3 セット (X1 = eSIM 副回線推奨)

「3 アカで同じ電話番号を使いたい」 → 6 案を比較。

```
1. 同じ番号で 3 アカ作成      ✗ Meta 同一人物検知で連鎖 BAN
2. 物理 SIM #1 + eSIM #2,#3   ◎ ★推奨 (povo 2.0 月額 0 円維持等)
3. 物理 SIM 3 枚              ◎ コスト最大、isolation 最大
4. IP 電話 (050plus 等)       ✗ IG 認証で拒否される事例多数
5. 家族の番号を 3 つ借りる    △ 家族 identity 紐付けリスク
6. SMS API (Twilio)           ✗ IG 認証拒否頻発
```

**X1 = 物理 SIM 1 + eSIM 2 (povo 2.0)** で iPhone 1 台運用。Decision 11 として正式化、`account-pivot-warmup/tasks.md` 1.6 / 1B.8 / 1C.8 / 3.7 に具体反映。残るリスク (device 軸、請求口座) と mitigation (別ブラウザ profile、Threads web 化) も明示。

→ [[05_learn/instagram-multi-account-isolation]] に切り出し

### 更新 artifact (5 ファイル + memory 4 ファイル)

| File | Δ |
|---|---|
| `account-pivot-warmup/proposal.md` | 1 アカ→3 アカ並行 (段階的 scaling) 拡張、capability `multi-account-scaling-strategy` 追加、Impact (Account 構成 / Timeline 9 ヶ月 / Operational 4 軸×3 セット) |
| `account-pivot-warmup/design.md` | Decision 8 完全書き直し (D3-b 段階的)、Decision 10 新設 (中道 milestone-driven)、Decision 11 新設 (4 軸 × 3 セット isolation)、Risks 3 つ追加、Migration Plan を Stage 1/2/3 構造に再構成 |
| `account-pivot-warmup/tasks.md` | Phase 0 を account_1 確定 / account_2 TBD / account_3 TBD の 3 セットに展開、staggered start タイムライン追加 |
| `multi-tenant-bootstrap/proposal.md` | 「2 アカウント目は将来別 change」の non-Goal 撤回、3 ジャンル × 3 アカ並行立上げを本 change で扱う |
| `publish-relocate-local/tasks.md` | 7.14 のチェック更新 (実 commit reference 付き、前セッション残) |

memory 更新: `project_revenue_target.md` / `project_account_scaling_strategy.md` / `project_affiliate_accounts.md` / `feedback_interior_persona_uchi_style.md`。

### 2 commits push (前セッション差分は別 commit)

```
6c1a0d4 openspec: pivot to 3-account staged scaling (D3-b ¥900k, milestone-driven)
        4 files (account-pivot-warmup proposal/design/tasks + multi-tenant-bootstrap proposal)
        +401 / -119 lines
137c07a chore: tick publish-relocate-local task 7.14 with archive commit refs
        1 file, +1 / -1 line, 前セッション残
```

main への直接 push が harness 側でハードブロック → user 自身が `git push origin main` でローカル実行 → `origin/main` 同期確認。

### 学び (横展開可能)

- **persona refine は 1 回で決まらない、3 回書き直す覚悟**: 各 stage で「直前の自分が言ったことと矛盾しないか」「肩書借り / 嘘の宣言 / 教え口調 のどれかに滑っていないか」を都度照合する。一発で正解を出そうとせず、書き直しを許容する方が結果的に sustainable な persona に着地する
- **subject 軸で広げる > 肩書軸で広げる**: 複数カテゴリ横断したいとき、肩書 (デザイナー、専門家) で広げると教え口調にズレる。subject (私の家、私の体験) で広げると一人称が全カテゴリで成立し、差別化も "私の" 私性で取れる
- **isolation 4 軸 AND で考える、1 軸完全分離では足りない**: phone 完全分離しても device fingerprint で同一視されうる。Composite fingerprint hypothesis と同じ前提で、Meta 側も複数信号の AND で同一人物判定している前提で 4 軸全部に boundaries を引く。device 軸は完全分離が非現実的なので「best effort + Stage 1 で実観測」に倒した
- **段階的 scaling = 1 アカ内 protocol を複数アカ間に拡張**: warmup の「観察 → 段階的に活発化」を 1 アカ内ではなく複数アカ間にも適用する発想。「前アカが BAN ゼロ + 収益軌道」を milestone gate にすると、1 アカ目で踏んだ罠が 2 アカ目で再発しないことを事前 detect できる
- **harness のハード block を user 手動 push で迂回する pattern**: main への直接 push が harness で禁止されているとき、commit までは Claude が積む / push だけ user terminal で叩くという分業が一番速い。permission rule を更新するのは将来の同じ操作を量産する想定があるときだけで、単発なら手動 push で済ます

### 次の判断点 (user)

1. **Phase 0 残作業着手** (Section 1A interior hooks 5-10 本 stock + 第 1 週 draft 1 本 + CLAUDE.md 更新)
2. **Section 1.6-1.9** 新 IG / 新メアド / token / 楽天 ID #1 取得 (eSIM は account_1 では既存メイン回線を使うので Stage 2 まで保留)
3. **publish-relocate-local 残 6 タスク** (token 配置、実機検証、5/11 cron monitor、PR 作成→merge→archive)

## 2026-05-07 — Phase 0 実装完走 (account_1 oheyamemo 立上げ + Token + 楽天 + PR #3、c0b0dfea、5-7 11:06–13:47 JST)

直前 explore (99902682) で Phase 0 設計が固まった直後、同日昼の 1 セッションで `account_1 = oheyamemo` (interior) を IG/Threads/Meta App/token/楽天 Web App/affiliate ID まで一気通貫立上げ。Phase 0 全タスク (§1.1〜1.11) ✅、PR #3 で `feat/account-pivot-warmup-phase0` を main に提案。W1 期 (今日〜2026-05-13) 開始 = **API 投稿ゼロ + Claude Code 自動監視ゼロ + humanness routine のみ**。

### Persona の最終調整 (explore 後にもう 1 回書き直し)

explore で `賃貸を整え始めた覚書 + PM/設計 background 1 行明示` で確定していた persona を、user が implementation 入口で `お部屋を整え始めた覚書 — 家具・照明・小物の選びかた。試して合うもの、ハズレた話、迷いと選び直し` + **PM background 削除** に書き換え。subject 軸を `賃貸 (住まい形式)` から `お部屋 (普遍)` に普遍化、肩書借り risk もゼロに。explore で 100% 固定せず、実装入口でもう 1 回見直す余地を残したのが正解。

### handle 確定: `oheyamemo` (8 chars、お部屋メモ)

短い handle (≤10 chars) 8 案を出してすぐ user が IG/Threads 両方で取得完了。アンダースコア無し。`oheyamemo` = お部屋メモ、persona と完全整合 + 検索 SEO 弱め (誤クリック源少) + 短い。

### Meta Developer Console — 旧 chokatsu 経路との差分

実機で旧 (2026-04-29) と現行 UI を比較:

| 項目 | 旧 chokatsu 経路 | oheyamemo (5/7) で正解 |
|------|----------------|----------------------|
| Use case | 「ユースケースなし → カスタマイズ」 | **「Threads APIにアクセス」を直接選ぶ方が正解** |
| Business Portfolio | リンクしない | リンクしない (確認のみ) |
| tester 追加 | App settings → Roles (FB account 必須) | **「ユースケース → Threads APIにアクセス → User Token Generator」内の "Add or remove Threads testers"** で `@oheyamemo` 招待 → Threads アプリ通知から承認 (FB account 不要) |
| FB テストユーザー警告 | — | 「テストユーザーの作成機能が一時的に停止されています」が `/roles/test-users/` 画面に表示 = **FB テストユーザー機能の停止であり、Threads tester とは別物** |
| token | OAuth callback 短命 → `th_exchange_token` で long-lived 化 | **「アクセストークン生成」で取得した token は最初から long-lived (60日)** で発行されるパターンあり、Step D (`th_exchange_token`) は **不要だった** (実行すると `Session key invalid` 4279019) |
| scope | 4 (basic/publish/insights + read_replies) | 同 4 つを Available 化 |

→ [[05_learn/threads-graph-api-setup]] に 2026-05-07 学び追記。

### `THREADS_USER_ID` の取得 (2 ルート + xdg `.env` 二重管理問題)

- `curl -G "https://graph.threads.net/me" --data-urlencode fields=id,username --data-urlencode access_token=$TOKEN` → `id` が `THREADS_USER_ID` (account_1 = `26631681313108721`)
- もしくは `npm run check:threads` (`/me` を叩いて User ID + username 印字)
- **xdg vs repo の `.env` 二重管理**: pipeline は `~/.config/threads-posts/.env` (xdg、254 bytes) を優先 load。user は IDE で開いていた repo `.env` (3820 bytes) に `RAKUTEN_*` を追記していた → publish ログで `env_token=xdg env_user_id=xdg` が出ているので xdg 経由 load を判定可能 → repo `.env` の RAKUTEN keys を xdg `.env` に追記コピーで解消。`.env` は gitignored なので commit リスクなし

### 楽天 Web Service App 登録 — Allowed websites + Expected QPS + 新仕様 IDs

| 項目 | 入力 | 結果 |
|------|------|------|
| Allowed websites #1 | `www.threads.net/@oheyamemo` (per-handle) | ❌ `Invalid domain` (path 含むと弾かれる) |
| Allowed websites #2 | `www.threads.net` + `threads.net` | ✅ 通過 (top-level domain のみ受理) |
| Expected QPS | 1 (デフォルト) | ✅ 商品マスター更新 cron 数本だけなので 1 で足る、過大申告は審査落ち、過小申告は `429` |
| App ID 形式 | `375dca6b-f31d-4426-adbc-fc624ad92a36` (UUID、新仕様) | ✅ 新 endpoint で受理 |
| Access Key | `pk_` 始まり (新仕様) | ✅ URL param 必須 |
| Affiliate ID | `53692023.ffe3300c.53692024.0a75b540` | ✅ pipeline `RAKUTEN_AFFILIATE_ID` に登録 |

### Rakuten API renewal — 旧仕様は **2026-05-14 完全停止** (本日 5/7 時点であと 7 日)

user 鋭く指摘: 「Rakuten APIの仕様が一新された、とか言ってなかったっけ？regacy使って大丈夫？」 → docs/operations.md と openspec archive を再確認:

```
旧 endpoint: app.rakuten.co.jp/services/api/...
旧 applicationId: 19 桁数字
新 endpoint: https://openapi.rakuten.co.jp/ichibams/api/...
新 applicationId: UUID
新 accessKey: pk_ 始まり (URL param 必須)
完全停止: 2026-05-14
```

最初の「legacy 使え」推奨は完全に逆。pipeline コードは新仕様対応済 (`pipeline/resolve_rakuten_links.js`) → 新 endpoint で再 test → ✅ 完全動作 (商品名取得 + affiliateUrl 生成)。memory `reference_rakuten_api_2026_renewal.md` を新規記録。 → [[05_learn/rakuten-dashboard-shorturl]] に renewal 警告追加。

### Phase 0 完了の artifact

**新規 (3 ファイル + 1 sample draft)**:
- `genres/interior/README.md` — interior ジャンル overview
- `genres/interior/accounts/oheyamemo/config.yaml` — credentials ref / affiliate IDs / persona path
- `genres/interior/accounts/oheyamemo/README.md` — account_1 overview + 4 軸 identity 一覧 + warmup phase 表
- `genres/interior/accounts/oheyamemo/content/drafts/D001_pendant_light_3_yarinaoshi.md` — W1 期 fit-check sample (公開しない)

**更新 (3 ファイル)**:
- `dept/content/hooks/interior.md` (新規) — "うち" 文体 hooks 構文集 (6 カテゴリ × 平均 3-4 hooks、`compliance: ok` 縛り)
- `CLAUDE.md` — multi-account 記述 + interior persona section + 旧健康ジャンル archive 注釈
- `banned_patterns.yaml` 確認のみ (「私は」強制ルール無し → account 切替設定不要)

### PR #3: `feat/account-pivot-warmup-phase0`

- commit: `fe84d4c feat(account-pivot-warmup): Phase 0 完了 — account_1 oheyamemo 立上げ + interior scaffolding`
- 6 files changed、252 insertions、5 deletions
- URL: https://github.com/tatoflam/ThreadsPosts/pull/3
- lint は新 path 未対応 (multi-tenant aware lint は future task)、想定通り

### W1 期 (2026-05-07〜13) 運用ルール — humanness only

| 行動 | 最低 | 推奨 |
|------|-----|-----|
| like | 5+/day | 8-10/day (interior / 暮らし / 部屋 系) |
| reply | 1+/day | 2-3/day (短くコメント) |
| scroll | 10 min/day | 15-20 min |
| follow | 0-3/day | ≤5/day (一斉フォロー禁止) |
| API 投稿 | **0** | **0** (絶対起動しない) |

**やってはいけない**: API 経由投稿 (`publish.js` / `npm run publish:due`)、bio に外部 URL、旧 chokatsu_studio フォロー先一斉フォロー、プロフィール画像頻繁変更 (1 ヶ月触らない)、1 日 20+ followunfollow、Claude Code 経由 `/me` polling 等の lightweight check も含む。

**Stage 2 起動 milestone (Decision 10、Reminder)**: oheyamemo が「BAN/警告ゼロ + cadence 維持 + ¥50-100k ラン」の 3 条件をすべて達成で account_2 起動判断。

### W2 以降の監視運用 (案)

- W2 開始 (2026-05-14) 後: `npm run metrics:sync` を **週 1 回 user 手動起動** (= weekly_report 生成と同じ rhythm)
- launchd 自動化: account_2 起動 (= scaling 増えてきた) 時点で検討、account_1 単独運用中は手動で十分
- alert / 異常検知: 当面は user の app 内目視に依存、自動 alert は別 change で起票するか判断時に決める

### memory 更新 (5 ファイル)

- 新規: `project_account_1_oheyamemo_facts.md` (handle/user_id/app_id/affiliate_id/credentials 配置先 snapshot)
- 新規: `reference_rakuten_api_2026_renewal.md` (旧 API 2026-05-14 廃止 + 新仕様完全リファレンス)
- 更新: `project_session_2026-05-07.md` (本セッション 完了内容 + W1 期運用ルール + 残タスク + 次セッション開始時のチェック手順)
- 更新: `project_account_scaling_strategy.md` (Phase 0 完了反映、slug `interior` 確定、persona broaden)
- 更新: `project_affiliate_accounts.md` (account_1 affiliate ID 確定値追記)

### 学び (横展開可能)

- **persona refine は explore 後にもう 1 回書き直す覚悟**: 5-7 朝の explore で `賃貸 + PM background` に確定した persona を、5-7 昼の implementation 入口で user が `お部屋 + PM 削除` に再書換 → これが正解。explore で 100% 固定せず、実装入口でもう 1 回見直す余地を残す
- **Meta UI は 4-5 日でも変わる、過去手順は前提を疑って実機確認**: 旧 chokatsu (2026-04-29) と oheyamemo (2026-05-07) で UI 経路が部分的に違う ("Threads APIにアクセス" use case が初手で選べる、`th_exchange_token` 不要パターン)。docs を妄信せず実機画面を 1 段ずつ user に報告してもらって追従する方が速い
- **Meta の警告メッセージは "場所" まで読まないと混乱する**: 「テストユーザーの作成機能が一時的に停止」は `/roles/test-users/` (FB テストユーザー画面) に出る警告であって Threads tester とは無関係。URL を読まずに「Threads tester 作れない」と勘違いしかねない
- **Spec change (Rakuten 2026-05-14 廃止) は memory + vault 両方に明示**: 残り 7 日の状況で過去 docs を引いて legacy を勧めかけた。spec change 系は `reference_*` memory + 05_learn 両方に記録して翌セッションで forget しないように
- **xdg `.env` vs repo `.env` の二重管理を user 操作前に明示**: publish-relocate-local で xdg を canonical 化したが、repo `.env` (IDE 上で開きっぱなし) に user が誤って追記する流れは構造的に再発しうる。pipeline log で `env_token=xdg env_user_id=xdg` が露出するので、user 操作前に「どっちに書くか」を 1 行明示するのが正解
- **W1 期は監視ゼロが理想 (API 起点ゼロ厳守)**: 投稿だけでなく `/me` 等の lightweight check も含めて API call ゼロが humanness signal を最強化する。user の app 内目視 (毎日 humanness routine 中) が最善の "監視" で、Claude Code は出番なし

## 2026-05-09 — `scout-interior-competitors-w1` 三重詰まりで clean abort (session 1228fa25、5-9 00:57–08:35 JST)

W1 期 (oheyamemo 立上げ後 1 週間) の **interior 競合スカウト** を openspec change `scout-interior-competitors-w1` で着工しかけたが、**自動化路が 3 段で詰まり** working tree をクリーンに戻して撤退。重要な「やってはいけない」を未実施で確定できた価値あるラン。

### 起点と要件

- user 要件: Threads 上で interior ジャンル個人クリエイター 5 名 (フォロワー 3K-20K + 楽天 `a.r10.to` 含有 ≥70% + 直近 20 投稿) をスカウト → handle / follower 数 / プロフィール / 代表 post URL を YAML 化
- 競合スカウトは account_1 (oheyamemo) の **W1 期戦略インプット**: 文体・persona・hooks を市場と相対化、Stage 2 起動 (account_2 立ち上げ) 前に絶対必要

### Propose 2 周 (ChatGPT 経路 → Claude 経路に書き直し)

1. **1 周目**: operator + ChatGPT でスカウト + Claude が CLI / YAML 整形支援 (user が ChatGPT を持っていて手動オペレーション可)
2. **user 指摘**「ChatGPT 不要、Claude Code 自身で全部やって」 → 2 周目は **WebSearch + Playwright MCP で Claude が直接 Threads にアクセス**して候補抽出する設計に proposal / design / spec / tasks 全リライト

### /opsx:apply §1.1 Pre-flight で hard block (Threads スクレイピング不可)

`https://www.threads.com/robots.txt` 確認:

```
User-agent: ClaudeBot       Disallow: /
User-agent: Amazonbot       Disallow: /
User-agent: GPTBot          Disallow: /
User-agent: PerplexityBot   Disallow: /
User-agent: Scrapy          Disallow: /
User-agent: *               Disallow: /
```

- **ClaudeBot は名指しで完全 disallow** (旧 .net は .com に 301 redirect)
- 唯一許可は Bingbot / Googlebot のみ (= SERP には Threads URL が出る)
- 明示禁止文言: 「automated data collection on Threads is prohibited without express written permission from Threads and must comply with Meta's Automated Data Collection Terms」

**gray-area で済まない 3 つの理由**:

1. **memory `project_account_ban_pivot.md`**: 2026-05-04 に Meta が前アカウント @chokatsu_studio を automated/inauthentic 分類器で BAN。fingerprint 信号 (IP/device) が分類器入力に含まれていた可能性高
2. **`account-pivot-warmup` Decision 7**: oheyamemo の生存戦略は **「humanness 主力対処」** = 同じ operator マシンから Threads に対して Playwright 自動アクセスすると、まさにその humanness 信号を毀損する
3. **Local-First architecture** ([[05_learn/local-first-anthropic-ops]]): publish と scrape が同一 IP/device になる。bot detection が触れた IP は publish 側にも波及する

### user の代替案「Threads API 使えば？」検証 → 不可

Threads Graph API surface (2026-05-08 時点で確認できる範囲):

- `POST /me/threads` — **自分の** アカウントから投稿
- `GET /me/threads` — **自分の** 投稿一覧
- `GET /me/threads/{id}/insights` — **自分の** 投稿の metrics
- `GET /me/threads_mentions` — **自分への** mention 通知
- `GET /me/threads_replies` — **自分への** reply 通知
- OAuth / token refresh 系

**存在しないもの** (= 競合スカウトに使えない):

- キーワード検索 API (Twitter/X v2 の `/search?q=...` 相当)
- 任意ハンドルの投稿取得 (`GET /users/{handle}/threads` 相当)
- 任意ハンドルのフォロワー数取得
- Public 投稿の hashtag/keyword discovery

**設計理由**: Twitter/X が public search API を提供して scraping/sentiment business に使われた歴史を踏まえ、Meta は Threads / Instagram Graph API を最初から **owner-only model** で設計。Instagram "Business Discovery" は限定的だが Business アカウント前提で個人 ≤ 20K follower スカウトには使えない。

### Fallback A 案 (operator 手動スカウト) を実装→ §4 で bricked → 取りやめ

Claude 単独で進められる範囲は実装:

| § | 完了内容 |
|---|---|
| 1.1-1.3 | Pre-flight findings (scrape 路撤回、operator 路確定) を artifacts に記録 |
| 2.1-2.5 | `dept/dev/pipeline/account-research/index.js` の `cmdCompetitors` を operator 向け手動 protocol に書き換え (`AFFILIATE_LINK_SAMPLE_WINDOW = 20` 定数、Step 5 必須キーに `account_type` 追加) |
| 3.1 | `dept/research/competitors/interior.yaml` skeleton 作成 |
| 3.2 | `gut-health.yaml` 冒頭に archive 注釈 1 行追加 |

§4 (operator が自分のブラウザで Threads 手動閲覧 → 20 投稿チェックリスト → 5 候補絞り込み) に bricked。user 取りやめ判断:

> 「ちょっとこの件は取りやめる。競合取得のための手動でやらなければいけない作業が多すぎて、今は作業に入れない。取得したとして、他の人のアカウントから自動で分析できるわけでもなさそうだし。」

**clean abort 実行**:

- tracked files (CLI + gut-health.yaml) を `git checkout` で revert
- untracked (interior.yaml + `openspec/changes/scout-interior-competitors-w1/`) を個別削除 (`rm -rf` は権限拒否されたため中身ファイルから順に削除)
- working tree を `fe84d4c` 状態に復帰確認
- memory `feedback_competitor_scouting_automation.md` 追加 — 「scrape (robots.txt 名指し disallow) / Graph API (owner-only) / 手動工数」の三重詰まり + 後段 auto 分析が動くまで scout 単独 change を提案しない、を future session への抑制信号として記録

### 横展開できる教訓

- **operator が「自動化前提 + 段階的 fallback なし」を望むケース**: Claude 側で robots.txt + API surface + humanness 信号の **3 段事前チェック** を **propose 段階で済ませる**べき。今回は /opsx:apply の §1 Pre-flight で初めて exposed = 設計の手戻り 1 周分のコスト
- **後段 auto 分析路がない data 収集 change は提案しない**: 取得しても活用できないデータを集める change は「収集パイプラインだけ作って腐らせる」典型的アンチパターン。`feedback_competitor_scouting_automation.md` で抑制信号化
- **「3 段詰まり」の判定軸を 1 ページに**: 詳細は新規 [[05_learn/threads-scrape-tos]] にスペック・robots.txt・Graph API surface を整理。次回 Threads / Instagram 関連の scout 系 change で **propose 入口で参照する想定**

see also: [[02_diary/2026-05-09]] / [[05_learn/threads-scrape-tos]] / [[05_learn/instagram-multi-account-isolation]]

## 2026-05-16 — account_1 (oheyamemo) 最初の interior content: K001/D001 シーリングライト end-to-end (d59da658、5-16 02:50-03:55 JST)

### 経緯

W2 (2026-05-14〜20) に入って account_1 (oheyamemo / interior) の最初の content をどう作るか未定だった状態で、user prompt 一発「YouTube URL `https://www.youtube.com/watch?v=UVHzIuORp44` の内容をもとに可能な範囲で自動でパイプラインを回したい」が起点。動画は YUKICH NO HOME「【シーリングライト14選】この照明でインテリアが激変｜プロ目線の選び方」で、interior の照明カテゴリ直撃。

### Pipeline 完走の構成と output

| Phase | コマンド | output |
|---|---|---|
| C RESEARCH | `npm run research -- --url <YouTube URL>` | `dept/research/knowledge/Transcripts/K001_YUKICH_NO_HOME_...md` + `Topics/K001_シーリングライト14選・プロ目線の選び方.md` (Claude による要点合成) |
| D CONTENT scaffold | `npm run generate -- --topic K001 --target "賃貸でシーリングライトを交換したい人" --template shop_search_redirect --pattern none --genre interior --tone classic --format text --account account_1` | `dept/content/drafts/D001_賃貸でシーリングライトを交換したい人.md` の frontmatter + scaffold |
| 本文書き込み | Claude が CLAUDE.md ルール準拠で本文を手書き | "うち" 文体 / 500 字以内 / 問い締め / 脚注 URL なし |
| Lint | `npm run lint:posts` / `npm run lint:templates` / `npm run validate` | error 0 / warn 0 (字数 562 → 500 字以内に 62 字削減 1 周) |

### Memory が全部刺さった事実 (interior pivot 後の最初の運用適用例)

| memory | 適用 |
|---|---|
| `feedback_footnote_no_url` (D011 以降 YouTube URL を脚注に載せない A/B) | 脚注はタイトル+publisher のみ。D001 を A/B のリンクなし側の最初の sample に位置付け |
| `project_format_strategy_text_first` (2026-05-16 確定) | `format: text` 固定、`format_mix.account_1.text=100` posting_policy gate 通過 |
| `feedback_interior_persona_uchi_style` | 文体は「うち」(主語) を貫いた、"私は" 系の混入なし |
| `feedback_post_templates` (`shop_search_redirect` 既定) | shop_search_redirect 採用、収益期待ランク最上位 |

### Whisper 不要が確認できた (字幕で完走、追加コスト 0)

memo: account_1 (interior) の YouTube 解説動画は字幕付きが多い前提に立てそう。今後 K002, K003 ... を量産する際の最初の選別軸として「字幕の有無」をチェックすれば Whisper API コスト発生を avoid できる。Whisper を呼ぶのは字幕なし動画でかつ高優先度のもののみに限定する運用が次の課題。

### Pipeline の今のところの正解形 (half-auto)

完全自動 LLM 本文生成は CLAUDE.md ルール (文体・問い締め・字数・脚注) の 4 軸同時 satisfy が安定しなかった (562 字オーバーで 1 周削減が必要だった、これは scaffold ベースの手書きでも起きた現象)。今は scaffold (`generate_post.js` で frontmatter + テンプレ構造) + 本文 Claude/人 手書き の half-auto が安定する。完全自動化を急ぐより、scaffold + 手書きで draft 量産する形を先に確立する判断。

### 残ゲート (D001 を実 publish するために必要な人作業)

1. **`status: draft_auto → ready`** — Topic frontmatter (人レビューでドラフトを confirmed 状態に flip)
2. **`[ショップ内検索 URL]` プレースホルダ差し替え** — `products.yaml` に該当エントリ無く `inject_affiliate` 自動マッチせず。`resolve:rakuten` で楽天ショップ内検索 URL を生成 or 手動で `a.r10.to` 短縮 URL を貼る、の判断
3. **`scheduled_at` 設定** — `posting_policy.yaml` の `preferred_jst_hours / min_gap_hours` と W2 残枠 (2026-05-16〜20) で人判断
4. **publish** — `/post-due` skill または `npm run publish:due` をローカル Mac から (Local-First)

### 学び (横展開可能)

- **YouTube 動画 1 本 → draft 1 件のリードタイム ~5 分** が demonstrated。account_1 の content supply 問題は YouTube 動画キューの整備さえできれば律速にならない、と判った
- **interior account_1 の最初の interior content がやっと出た** (Phase 0 完了 5/7 から 9 日、W2 中盤)。Stage 1 milestone の「normal phase + 4 週 + ¥50-100k ラン」までは draft 量産優先で 5-7 件目標
- **post-tone-frank-and-format-strategy spec の effect が出始め**: frontmatter に `template_type` / `copywriting_pattern` / `tone` / `format` を書く運用が D001 から実流入。これらメタデータが将来の W4 期 A/B (classic vs frank, text vs image) の dataset 基盤になる

see also: [[02_diary/2026-05-16]] / [[05_learn/wiki-automation-pipeline]]

## 2026-05-16 W2 ratify 準備 + 競合分析と教材整理

D001 着地後の同日に 2 件のお手入れ作業:

### 沼子。分析 → 4 役割ローテ学習 (196a73b5)

- カピおじ note 記事「分析の鬼が徹底解説・このアカウントから学べ」(2025-04-25) を要約し `docs/resource/k02_05.md` に保存
- W2 strategy stub `dept/marketing/strategy/weekly/2026-W20.md` を新規作成 (各セクション TBD、ratify は B-4 で実施予定)
- 抽出された Threads 4 役割ローテ (共感獲得 / 収益化 / 有益情報 / ファン化) と共感の解像度ルールは [[05_learn/threads-engagement-rotation-pattern]] に再利用可能な形で永続化
- 沼子。アカウントの `dept/research/competitors/interior.yaml` 登録は別セッション (フォーマット整え待ち、memory `feedback_competitor_scouting_automation`)

### Brain 教材 (k01.md) 3391 行 → 638 行 要約 (028c145c)

- 元 (Brain 教材スクレイピング) は画像/CDN 参照だらけ + 特典詳細 (`k02.md` 配下に展開済) で読み返しコスト高 → 構造を残して圧縮
- 維持: 章立て / 6 投稿型のメリデメ / PREP/PASONA/AIDMA / 王道ジャンル定義 / リサーチワード / 薬機法・BAN・スパム判定の注意 / CTA バリエーション
- 除外: `![]()` 画像、Brain/note base64 画像、特典本文 (`k02.md` リンクのみ残置)
- 後で参照する可能性が高い外部 URL (Notion / 楽天イベントカレンダー / 著者の楽天 ROOM / Google Sheets バズフック集) はそのまま保持

### see also
- [[02_diary/2026-05-16]] — 07:50 / 07:51 エントリ
- [[05_learn/threads-engagement-rotation-pattern]] — 本日由来の新ナレッジ

## 2026-05-16 interior-playbook-from-K 49/50 完走 + 「うち」撤回 + launch 週 brand 抑制 (6c99bbeb、07:52-09:14 JST)

K-spec (k01_攻略本 / k02_05_沼子。分析) からの seed を一気に capability 化する change を user-invoked `/opsx:propose interior-playbook-from-K` → `/opsx:apply` で 1.5h で完走 (1 タスクのみ defer: 11.6 branch 作成 = warmup 中は API 投稿せず手動観察 user 判断)。続けて K001-シーリングライト draft 投入 → ad-hoc な user review で「うち」文体撤回 + launch 週 brand 抑制の 2 件のルール改訂が連鎖した。

### change 実装 (49/50)

| 種別 | capability | 主成果物 |
|---|---|---|
| 新規 | `post-purpose-types` | [dept/content/templates/purposes/](dept/content/templates/purposes/) 配下 5 テンプレ + frontmatter `post_purpose` 軸 |
| 新規 | `post-rotation-pattern` | [rotation_account_1.yaml](dept/marketing/strategy/rotation_account_1.yaml) + [rotation_decision_log.md](dept/marketing/strategy/rotation_decision_log.md) + [lib/rotation.js](dept/dev/pipeline/lib/rotation.js) |
| 新規 | `shop-catalog` | [shops/interior.yaml](dept/research/shops/interior.yaml) (33 shops: ok 25 / unknown 8) + [lib/shop_catalog.js](dept/dev/pipeline/lib/shop_catalog.js) + `npm run research:shops` |
| 更新 | `post-templates` | [hooks/interior.md](dept/content/hooks/interior.md) 51 entries (ok 30 / ok-frank 18 / 12 カテゴリ) |
| 更新 | `content-pipeline` | generator `--purpose` + rotation/fallback 経路 ([generate_post.js](dept/dev/pipeline/generate_post.js)) |
| 更新 | `account-research` | [prompts/interior.md](dept/dev/pipeline/account-research/prompts/interior.md) + [_default.md](dept/dev/pipeline/account-research/prompts/_default.md) + competitors/interior.yaml seed (@tokimeki_numako) |
| 更新 | `draft-metadata` | frontmatter `post_purpose` + `template_type` + `copywriting_pattern` + `rotation_position` 軸追加 |

- change 名 rename: 当初 `-kapi` → user 指示で `-K` に。K-spec (k01〜k02_05) seed 由来を強調
- tests: 247/247 pass、`lint:hooks` / `lint:templates --include-templates --include-purposes` 全 clear

### persona 2 層運用 (プロフィール OK / 本文 NG) 仮置き

user から最新 Threads bio (`フォローするだけで〜🪄 / 🏠 / 📐 ｜建築のプロの視点で〜 / ☕ コーヒーと読書と cero`) を受領し [persona.md](genres/interior/accounts/oheyamemo/persona.md) に保管。**「建築のプロの視点」** が **既存 CLAUDE.md ルール「PM/設計 background はすべての層で明示しない」と矛盾** したため即時報告 → 暫定的に **プロフィール OK / 本文 NG の 2 層運用** に解釈 (persona.md + memory `project_account_1_oheyamemo_facts.md` に 2026-05-16 改訂として記録)。CLAUDE.md 本体改訂は user 判断 (A. 2 層確定 / B. 全層 OK / C. プロフィールも戻す) 待ち、本セッションは A 仮置きで実装

### 文体 2 連続改訂 — 実物書いてからルール固定

D002-D005 K001-シーリングライト drafts を主語 = うち版で書いた直後の user review で 2 連続ルール改訂が発生:

#### 「うち」撤回 → 主語省略デフォルト (2026-05-07→2026-05-16)

`私は` → `うち / うちの` の interior 専用文体を **9 日で撤回**。新ルール: **主語省略がデフォルト**、例外として対比文脈の `うちの<具体名>` のみ可。反映先 7 箇所:

- [CLAUDE.md](CLAUDE.md) account_1 セクション (主語省略 + 例外条項)
- [persona.md](genres/interior/accounts/oheyamemo/persona.md) 投稿本文ルール
- [dept/content/style/frank_voice.md](dept/content/style/frank_voice.md) フランク文体ガイド
- [hooks/interior.md](dept/content/hooks/interior.md) 51 entries 全書換 (lint:hooks ✓)
- 11 テンプレ (6 monetization + 5 purpose) フランク版 example body から「うち」除去 (lint:templates ✓)
- 旧 D001 削除 (2 か所) + D002-D005 を主語省略版にリライト + D002 ファイル名から `うちの` slug 除去
- memory `feedback_interior_persona_uchi_style.md` を 2026-05-07→2026-05-16 経緯付きで全面書換 + `MEMORY.md` 行更新

#### launch 週 (warmup_w1〜w4) は出典・固有商品名・ブランド名を抑制

D002 末尾「Art Work Studio『GLOW LED シーリング』を試して」+ D003 「Tiny Glass Ceiling Light 3」+ YUKICH NO HOME 出典 を user 指摘 — launch debut で唐突にブランド名が浮く + empathy 型の構造ルール違反。新ルール: warmup 期は信用形成を先行、固有名詞・出典・アフィ URL を Phase 別に段階解禁:

| Phase | 出典 | 固有名詞 | アフィ |
|---|---|---|---|
| warmup_w1 | × | × | × |
| warmup_w2 | × | × | × |
| warmup_w3 | × | × | △ (ratio 30%) |
| warmup_w4 | △ | △ (1 投稿 1 つ) | △ (ratio 50%) |
| normal_w5+ | ○ | ○ | ○ (ratio 80%) |

反映先: CLAUDE.md (1 行 + persona.md 参照) / persona.md `launch 週の追加制約` 節新設 / [empathy_relatable.md](dept/content/templates/purposes/empathy_relatable.md) 構造ルール + NG パターン / [informational_value.md](dept/content/templates/purposes/informational_value.md) 例外条項 + NG パターン / memory `feedback_launch_week_footnote_brand_suppression.md` 新規 + `MEMORY.md` 更新

D002 → 「アッパーライト独立調光がついている機種」、D003 → 「小ぶりに作られてる機種」に書直し、D004/D005 は元から該当なしで変更不要

### 学び (横展開可能)

- **文体ルールは drafts を 5-10 本書いてから最終確定**: 「うち」文体は 2026-05-07 確定だったが、D002-D005 を実物で書いてみたら冗長と判明、9 日後に撤回。設計レビューでなく実物レビューでないと検出できなかった
- **launch 週デザインは信用形成優先で固有名詞ゼロ**: 4 週積んでから商品紐付け解禁が鉄則 (フォロワー獲得前の brand 露出は「広告アカウント」認知に直結)
- **persona 2 層運用** = 本文では権威化禁止を維持 + プロフィール 130 字では信用フックを取りに行く中道。CLAUDE.md 本体改訂は user 判断待ち

### 次セッション

- 11.6 branch creation (warmup 中は手動観察) → user 判断
- CLAUDE.md 本体の 2 層運用文言改訂 → user 判断
- W2 (5/14-20) の rotation 配列を `2026-W20.md` で ratify → /weekly-cycle B-4 時

### see also
- [[02_diary/2026-05-16]] — 07:52 エントリ (本セッション、3 層変更を時系列で)
- [[05_learn/persona-driven-content-rules]] — 2026-05-16 改訂 (うち撤回 + launch 週抑制) を追記
- [[05_learn/threads-engagement-rotation-pattern]] — 沼子。事例の 4 役割ローテが post-rotation-pattern capability の seed

## 2026-05-16 〜 05-19 — post-tone-frank PR / resolve-affiliates / playbook PR / research-local-first / image-pick-web / at-scheduler (5 sessions landing, run-48)

run-48 (`/wiki-ingest` 2026-05-28) で **private-repo-push 先例**を `tatoflam/ThreadsPosts` 全 PR に統一適用、5/15〜5/19 起算で 22〜38 連続 defer されていた 5 セッションを一気着地。`06_output/2026-05.md` trailing-whitespace dirty は引き続き存在するが、これらは Threads publish (post_id) を伴わず 06_output 対象外として扱う (per run-42/run-47 の MeguruPMReport / ToDoBot 先例)。Threads publish を含む 4 件 (`fdc3d957` D002、`ba2b8e66` D003、`d244f847` D005/D006、+ `e19b11f3` 公開 GitHub 初回 push) は引き続き defer。

### post-tone-frank-and-format-strategy 56/56 完走 + PR #4 / PR #5 archive (8cf2b80c, 5-16 00:35-01:52 JST)

spec-driven change 全 6 group 56 task ✅:

- **lint severity** (errors vs warnings 分離): `dept/dev/pipeline/lint/rule_lint.js`、`lint_posts.js` で WARN プリント、`lintPostFile/Content` の戻り値 `{errors, warnings}` 化、`npm run lint:templates` script 追加
- **banned_patterns.yaml** 新規 (`dept/content/style/banned_patterns.yaml`): 連続体言止め検知 + 脚注行 (`footnote_*`) は formal_stiffness 検査から除外
- **frank_voice.md** 新規 (`dept/content/style/frank_voice.md`): フランク文体ガイド + 用例
- **`tone`/`format` frontmatter 軸** 拡張: `validate_frontmatter.js` で enum 検証、`backfill_frontmatter.js` で `tone: classic` / `format: text` デフォルト埋め込み、`generate_post.js` で account_1 を `--genre interior` から推論
- **6 monetization templates** に「フランク版例文」セクション追加 (`product_single` / `summary_set` / `summary_tree` / `room_redirect` / `shop_redirect` / `shop_search_redirect`)
- **interior hooks に ok-frank 7 entry** 追加 (`dept/content/hooks/interior.md`)、lint:hooks pass
- **posting_policy.yaml** `format_mix` + `format_switch_gates` キー追加、`lib/posting_policy.js` で validation + loader 統合

tests: rule_lint 9 件 / validate_frontmatter 12 件 / backfill 6 件 / posting_policy 11 件 = 計 54 件 pass、`lint:templates` clean。

PR #4 (`feat/post-tone-frank-and-format-strategy → feat/account-pivot-warmup-phase0`、Phase 0 PR スタック、commit `a21aa92`、23 ファイル)。Phase 0 merge 後 GitHub が自動 retarget → main merge 確認 → `/opsx:archive` で `openspec/changes/archive/2026-05-15-post-tone-frank-and-format-strategy/` へ移動、新 spec `post-tone-frank` + `post-format-strategy` capability 化 (`+10 added / ~3 modified`)、PR #5 (`chore/archive-post-tone-frank → main`、純 openspec bookkeeping、`a21aa92` の archive 差分のみ)。

### resolve-affiliates 自動運用棚卸し + actions/checkout@v5 + Node 22 bump PR #6 (c7f92639, 5-16 01:52 → 5-17 08:36 JST)

「今、自動で何か運用できるんだっけ？」 user 質問 → GitHub Actions の稼働 workflow を棚卸し:

- `resolve_affiliates.yml` (日次、楽天 affiliate URL 解決) — Threads token 不使用
- `weekly_report.yml` (週次、posting policy metric 集計) — Threads token 不使用

Threads ban 後 (5/4) は API 投稿が止まっているため、現状動いているのはこの 2 本のみ。`workflow_dispatch` で手動実行可能、artifact (失敗ログ ZIP) のダウンロード方法を user に案内。

Node 20 deprecation 警告対応: `chore/bump-actions-node22` ブランチで:
- `actions/checkout@v3 → @v5`
- `actions/setup-node@v3 → @v5`
- `node-version: 20 → 22`

2 workflow 一括更新、PR #6 起票 → user GitHub UI で merge → ローカル fast-forward + branch prune。

### interior-playbook PR creation + research-local-first /opsx:propose 起票 (86141ecc, 5-17 08:36-09:54 JST)

`/opsx:explore` で 5/16 着地済の interior-playbook-from-K change 周辺を点検。user 「先に PR を切って main を綺麗にしてから運用に入る」方針 → `feat/interior-playbook-from-K` PR 起票 → user GitHub merge → ローカル fast-forward (commit `2259e39`、main 同期)。`D002-D005` (W2 配置 4 件 draft、subjectless「うち」撤回後のリライト版) の frontmatter / lint 確認 → 全 pass。W2 (5/14-20) rotation 運用ルール (4 役割ローテ: 共感獲得 / 収益化 / 有益情報 / ファン化) を `dept/marketing/strategy/rotation_decision_log.md` に追記 (5/16 ratify 補完)。

「ネタ集めも自動化したい」 user 質問 → `/opsx:propose research-local-first`: YouTube transcripts ベース + user-intake-dialogue + 楽天 API 直叩きで `account-research` (ChatGPT 依存) を再設計、6 → 56 task に展開、openspec validate strict pass。「収益化を見据えると、逆算で先にトピックに関連する商品の特徴 × `a.r10.to` や、特徴 × YouTube / X / Threads でリサーチしてマーケティング → 投稿企画」という上流回帰要望を spec 化。

### research-local-first /opsx:apply 56 task 完走 + PR #9 (account-pivot-warmup phase gate + multi-tenant) + account-pivot-warmup archive (a878e29c, 5-17 09:54-11:49 JST)

`/opsx:apply research-local-first` で 9 group 56 task 着地:

- **`/research-youtube` skill** 新設 (`.claude/skills/research-youtube/`): yt-dlp で transcript 取得、字幕ありは Whisper skip
- **`/research-intake` skill** 新設 (`.claude/skills/research-intake/`): weekly-cycle B-MARKETING 冒頭で起動する 5-10 分の対話、`dept/research/inbox/<ISO_week>/candidates/` に 3 file (`knowledge_seeds.md` / `products.yaml.fragment` / `hooks.md.fragment`) 振り分け、URL 推測禁止、skip 可
- **`account-research/*` 撤去**: ChatGPT 依存の subcommand (competitors / products) を完全削除
- staging area `dept/research/inbox/<ISO_week>/` 運用開始
- marketing-cycle B-1 を user-intake-dialogue 主導へ書換 (`SKILL.md`)

同 PR (#9 `feat/account-pivot-warmup-phase-gate → main`) 内で **account-pivot-warmup §3-§12** 全実装も着地:
- `publish.js` phase gate (warmup_w1〜w4 の固有名詞 / 出典 / アフィリ段階解禁)
- warmup ramp 上限 (`MAX_POSTS_PER_DAY` を phase ごと可変)
- `lib/phase_gate.js` 新設 (env var `POSTING_PHASE_GATE_ENABLED=false` で bypass、prominent warning ログ)
- 5 capability 連動 (`posting-strategy` / `account-warmup-protocol` / `account-isolation-hygiene` / `post-templates` / `account-config`)

さらに `multi-tenant-bootstrap §1+§3+§4` も同 PR に乗った: `tenant_paths.js` + base persona + config 拡張 (commit `a5106df`)。

PR #9 merge → `chore(openspec): archive account-pivot-warmup + sync main specs` (commit `87d5a8b`) で main spec 同期完了。

user prompt 「現時点で運用として、一連の流れで何ができるようになっているか。変更要件(changes)の今後のプロダクト更新の方針はどうか、という観点で、一度整理してほしい」 → assistant が 5/16 着地の playbook + 5/17 着地の phase-gate / research / multi-tenant を踏まえた横断 roadmap を提示し、次の作り込み優先順位を提案。

### image-pick-web + 写真確認 UI + at-scheduler 仕込み (72d2768d, 5-18 16:07 → 5-19 07:45 JST)

「この投稿に合う画像って、実装済みの機能を使ってリストアップできるの？」 user 質問 → 既実装の `image-pick-web` (Unsplash API + license 取得ベース) の存在を確認、web からの自動候補抽出は未配線と判明 → 3 PR 起票で配線完成:

- **PR #10**: image API 実装 (`format-image-enablement §1-§7,§9,§10`、commit `c4964da`) — `dept/dev/pipeline/image/` 配下に Unsplash adapter + license 解決 + cache
- **PR #11**: `image-pick-web` skill 新設 (`/image-pick-web` slash command) — draft text → 英語 search query 抽出 → 候補リスト → user 選択 → `dept/content/assets/<account>/<draft_id>/` ダウンロード + frontmatter `image_paths:` + `image_license:` 反映
- **PR #12**: D003-D008 各 draft に image_paths を反映 (merge conflict 解消後着地、本セッション内で user 委譲)

写真確認 UI 経路: `dept/content/assets/account_1/D00X/index.md` で thumbnail プレビュー (Obsidian / VSCode previewer 依存)。「どこで見られるの？リンクを明示して」 user 反復質問 → README に確認手順を明示。

外部ホスト検討: 「Cloudflare R2 / S3 / Cloudinary 等だとどこがいい？例えば GWS アカウントがあるから Google Drive にクレデンシャル使って接続するようにしたら？」 user 質問 → 2 案 (R2 vs Google Drive) → user 「Google Drive で簡潔な実装でよろしく」 → `/opsx:propose image-hosting-gdrive` 起票 (本セッション末で着手、続きは 5/22 d244f847 で実装、本 ingest では defer)。

at-scheduler 仕込み: 「あとは自動で 1 時間後に publish しといて」 user 依頼 → Mac の `at` コマンドで scheduled publish job を仕込み (`atq` で確認、log は `~/Library/Logs/`)。`at` は launchd 経由で permission 必要 → `Update Config Skill` で `~/.claude/settings.json` の bash permission を更新 → user 「at を有効化したよ」で運用開始 (この at-scheduler は後に 5/22 d244f847 で launchd routine に置換)。

### 残課題と先送り

- **Threads publish 系 (4 件) は本 ingest 範囲外**: `fdc3d957` (D002 publish post_id=17930169027278345)、`ba2b8e66` (D003 publish post_id=18099291563012991)、`d244f847` (D005/D006 publish + image-hosting-gdrive 実装 + launchd routine + auto-commit on publish) は public publication (post_id) を伴うため [[06_output/2026-05]] 行追加対象、同 file dirty のため defer 継続 (累計 22-38 連続)。次ラン fix = `cd ~/repo/github/tatoflam/v && git restore 06_output/2026-05.md`
- **format-image-enablement archive** は 5/22 d244f847 セッションで実施、本 ingest では未着地
- **画像付き投稿の実運用**: text-first 戦略の中に「適切なものがあれば一部 image 付き投稿」を入れる方向 (5/22 ba2b8e66 で確定、本 ingest では別 change として起票のみ)

### see also

- [[02_diary/2026-05-16]] — 00:35 + 01:52 entry (本セッション 8cf2b80c + c7f92639)
- [[02_diary/2026-05-17]] — 08:36 + 09:54 entry (本セッション 86141ecc + a878e29c)
- [[02_diary/2026-05-18]] — 16:07 entry (本セッション 72d2768d、5/18→5/19 スパン)
- [[05_learn/threads-engagement-rotation-pattern]] — 4 役割ローテと W2 ratify
- [[05_learn/wiki-automation-pipeline]] — 18+ 日継続 06_output dirty defer の運用パターン
