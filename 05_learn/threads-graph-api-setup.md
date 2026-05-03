---
title: Threads Graph API セットアップ — Meta Developer Console の落とし穴
category: 05_learn
tags: [topic:threads-graph-api, tech:nodejs, channel:threads, entity:meta-developer-console]
sources: [088ab1c0-c2f2-4677-8201-1c6f9767bcfa, ea7dfd5b-e2ac-4067-82b3-a2efde32bb29]
updated: 2026-05-03
---

# Threads Graph API セットアップ — Meta Developer Console の落とし穴

## Summary

Threads Graph API を新規アプリで有効化するときに、世に出回っている記事や旧 docs
（左メニュー「Threads」→「利用開始」みたいな手順）は **2026 年 4 月時点の現行 UI
と乖離**している。本実装中に同じ罠で 2 時間以上溶かしたので、**動いた経路だけ**
を記録しておく。詳細プロジェクトは [[03_work/threadsposts]]。

## Details

### 1. 動いた発行ルート（2026-04-29 確認）

Meta Developer Console（`developers.facebook.com/apps/<APP_ID>`）の左メニューには
**「Threads」「利用開始」「設定」**といった旧 docs に出てくるエントリは存在しない。
代わりに次のメニューだけがある：

```
- ダッシュボード
- 必要なアクション
- ユースケース
- テスト
- 公開
```

正解は **「ユースケース → カスタマイズ → アクセストークンを作成」** のルート。
ここから直接ユーザートークンが発行できる（権限選択 UI もこの中に統合されている）。

### 2. 詰まったポイントと回避策

| 詰まり | 旧 docs の指示 | 実際 | 回避策 |
|--------|----------------|------|--------|
| Redirect URI を保存できない | 「`https://localhost:8443/callback` を登録」 | 「フォームを保存できません」エラー | **`https://www.threads.net/`** を登録すると通過。GitHub Pages（`https://tatoflam.github.io/ThreadsPosts/callback`）も `https://tatoflam.github.io/oauth-cb/` も同エラーで NG |
| 認証 URL が「リクエストと一緒にアプリ ID が送信されませんでした」エラー（`error_code: 4476002`） | 認証 URL を組み立てて手動 OAuth | リダイレクト URI ホワイトリストに登録できないので OAuth 自体に進めない | OAuth フローを諦め、Console の **アクセストークン作成 UI** で直接発行する |
| 「権限」メニューが見つからない | 旧 docs の「Threads → 権限」 | そのメニュー自体存在せず | スコープは **ユースケース → カスタマイズ** の中で選ぶ |
| `scopes` 設定が見当たらない | 旧 docs ナレッジ依存 | カスタマイズ画面の「設定」セクションに統合済 | 同画面で `threads_basic` などを ON |

### 3. Threads プロフィール保護のロックアウト

OAuth 設定を試行錯誤している最中に「**あなたの Threads プロフィールで異常な
アクティビティが検出されたため、プロフィール保護のためアクセスが制限されました**」
というメッセージが表示され、Instagram に通知が来ず復旧導線がなくなる事象が発生。

- Instagram にも Threads にも復旧通知が出ない（「別のデバイスでのお知らせ」が来ない）
- Threads アプリ側からは何もできない
- **Meta Developer Console 側で「ユースケース → カスタマイズ → アクセストークン作成」
  を完了させると、その操作自体が認証として機能してロックが解除された**

OAuth リダイレクトを諦めて Console 内発行に切り替えたのが結果的に正解だった。

### 4. ローカル疎通確認（`npm run check:threads`）

`/me?fields=id,username` を叩く軽量スクリプト。発行直後にこれで OK / FAILED
を即判定できる。

```bash
$ npm run check:threads
[check] OK
  user id:  36075427142056546
  username: @chokatsu_studio
[check] set THREADS_USER_ID=36075427142056546 in your .env
```

`username` は表示名（`chokatsu_studio`）、API 呼出には **数字の User ID** を使う点に注意。

実装上の地雷 2 件：
1. **`.env` 自動 load なし** — 初版は `process.env` を直接読んでいて `THREADS_ACCESS_TOKEN env var is required` で落ちる。`node --env-file=.env` を `package.json` の script に追加して解決（commit `3bc9317`）
2. **YAML パーサが `scheduled_at` を Date 型に変換** — `validate_frontmatter.js` と `publish.js` の両方で文字列前提の `isDuePost` チェックが落ちる。Date インスタンスも受けるよう修正（commit `2beb918`）

### 5. トークン運用

- **アクセストークン有効期限：60 日**（`exchange_token` で都度延長可）
- 失効する前に再発行する運用が必要。今回の発行が 2026-04-29 なので **2026-06 下旬までに再発行** をリマインダ済
- `.env` 4 変数が揃っていれば `check:threads` がワンコマンドで疎通＋ User ID 印字するので、再発行の手順は token 上書き → `npm run check:threads` のみ

### 6. 当面参照しなくていい記事 / 手順

旧 docs の以下の文言は 2026-04 時点では **無視してよい**：

- 「左メニューの Threads → 利用開始」
- 「Threads → 設定 → Client OAuth の設定」
- 「権限メニューでスコープを選択」
- 「Redirect URI に `https://localhost:...` を登録」

代わりに `developers.facebook.com/apps/<APP_ID>/use_cases/` 配下を直接見る。

## Links

- [[03_work/threadsposts]]
- [[02_diary/2026-04-29]]
- [[06_output/2026-04]]

## 7. ID/トークン対応表 — User ID と App ID は別物（2026-05-03 追加）

`THREADS_USER_ID` と `THREADS_APP_ID` の取り違えで詰まりがち。`docs/meta_developer_setup.md` 冒頭に対応表を置いて取り違え予防（commit `f6691db docs(setup): ID/トークン対応表を追加し User ID 取得手順を強調`）。

| 変数 | 例 | 取得元 | いつ作られる |
|---|---|---|---|
| `THREADS_APP_ID` | `2128135774707190` | Meta Developer Console → Apps → 該当アプリの「App ID」 | アプリ作成時に自動採番 |
| `THREADS_APP_SECRET` | `xxxxx...` | 同 → 「App Secret」 | アプリ作成時に自動採番（再生成可） |
| `THREADS_USER_ID` | `36075427142056546` | OAuth flow（手順 5）または `npm run check:threads` の出力 | 初回アクセストークン発行時に判明 |
| `THREADS_ACCESS_TOKEN` | `THAA...`（60 日有効） | 「ユースケース → カスタマイズ → アクセストークンを作成」 | 手順 3〜4 で発行 |

**重要**: User ID は手順 5（OAuth flow）でしか自然に取れない → 取り忘れた場合は `npm run check:threads` の出力をコピペすればリカバリ可能。スクリプトは `/me?fields=id,username` を叩いて User ID と username の両方を返す。

```bash
$ npm run check:threads
[check] OK
  user id:  36075427142056546   ← これが THREADS_USER_ID
  username: @chokatsu_studio    ← これは表示用、API には使わない
[check] set THREADS_USER_ID=36075427142056546 in your .env
```
