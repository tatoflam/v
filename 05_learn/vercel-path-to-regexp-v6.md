---
title: Vercel デプロイの落とし穴（path-to-regexp v6 / LFS / Team scope namespace / branch-stable URL）
category: 05_learn
tags: [topic:vercel, tech:vercel, tech:nextjs, tech:git-lfs, tech:path-to-regexp, stage:done]
sources: [3c5be9c0-ca09-48a9-a034-8f8e46003dc3]
updated: 2026-05-03
---

# Vercel デプロイの落とし穴

SpecDrawing を Vercel に乗せた `add-vercel-deployment`（[[05_learn/specdrawing-material-presenter]]）で踏んだ落とし穴を再利用可能な形でまとめる。

## 1. `vercel.json` の `headers.source` は path-to-regexp v6 互換が必須

- 症状: Vercel CI が `Deployment failed: invalid-route-source-pattern` を返す。リンク先は <https://vercel.com/docs/errors/error-list#invalid-route-source-pattern>
- 原因: path-to-regexp v6 で **unnamed group**（`(mask_|shading_|base_)` のような `(...)` だけの非キャプチャ風記法）が削除されている
- 修正: グループを使わず、各パターンを別エントリに分割する
  ```json
  // ❌ NG（v6 で reject）
  { "source": "/assets/(mask_|shading_|base_).*", "headers": [...] }

  // ✅ OK
  { "source": "/assets/mask_:rest*", "headers": [...] },
  { "source": "/assets/shading_:rest*", "headers": [...] },
  { "source": "/assets/base_:rest*", "headers": [...] }
  ```
- 注意: Vercel は **`installCommand` は実行するが `headers` 設定は reject** という半分動作になる。LFS pull は走って画像は出るが Cache-Control が付かない、というハーフ状態を生む
- 関連 commit: [`5cbda54 Fix vercel.json headers patterns for path-to-regexp v6`](https://github.com/meguruit/SpecDrawing/commit/5cbda54)

## 2. `installCommand` で `git lfs pull` を明示する

- 症状: 画像（PNG / JPG）が全部リンク切れに見える。実際にレスポンスを覗くと **134 bytes の LFS pointer file テキスト** が返ってくる
- 原因: Vercel のデフォルト clone は LFS pointer のみ pull する（Hobby / Pro 共通）
- 修正: `vercel.json` で installCommand を上書き
  ```json
  {
    "installCommand": "git lfs pull && npm install"
  }
  ```
- 検証: build log で `Filtering content` / `Downloading LFS objects` の行が出るか確認。Build log は **Vercel ダッシュボード → Deployments → 該当 deploy → Build Logs**

## 3. Vercel Team scope は GitHub namespace 単位で見える / 見えないが決まる

- 症状: GitHub 個人アカウント `tatoflam` で `Only select repositories: SpecDrawing` を許可しても、Vercel Team の Import 画面に repo が出ない
- 原因: Vercel は **scope（Personal / Team）ごとに Git integration が独立**。Team が連携している GitHub identity がチームメイトの個人アカウントだと、`tatoflam` namespace は別人扱いで Team scope に出てこない
- Pro Team の解決策: Team scope の Import 画面の Git Namespace dropdown 一番下の **"+ Add GitHub Account"** または **"Switch git provider"** から `tatoflam` を追加 install
  - `https://github.com/settings/installations` の Vercel App で repo access を確認
  - Pro 以上で個人 namespace 追加可
- Hobby Team の場合: 個人 namespace 追加 UI が出ないので **GitHub repo を Team が連携している org に transfer** するしか手がない
- 確認用 URL（UI ナビが見つからないとき）:
  - Login Connections（自分の Vercel ログイン identity）: <https://vercel.com/account/login-connections>
  - Team の Settings → Git Integrations: `https://vercel.com/<team-slug>/~/settings`

## 4. Deploy 固有 URL ≠ Branch-stable URL ≠ Production URL

Vercel が発行する URL は 3 系統あり、何を見せられているかで状況解釈が変わる:

| 種類 | 形式 | 何に pin される | 用途 |
|---|---|---|---|
| **Deploy 固有 URL** | `<project>-<commit-hash-suffix>-<team>.vercel.app`（例: `spec-drawing-6aqqijf2r-meguru-construction.vercel.app`） | **commit に固定** | 過去の deploy をスナップショットで再現 |
| **Branch-stable URL** | `<project>-git-<branch-slug>-<team>.vercel.app`（例: `spec-drawing-git-proposal-memos-fideli-d382e7-meguru-construction.vercel.app`） | **ブランチの最新 deploy** | preview の共有 / レビュー |
| **Production URL** | `<project>.vercel.app` ＋ custom domain | **production branch（main 等）の最新** | 本番 |

- 「画像が出ない」と言われたら、**どの URL を見ているか** を最初に確認する。Deploy 固有 URL は古い commit の deploy を見ている可能性がある
- preview deploy は GitHub PR にコメント化されるが、PR がまだ無い branch でも push すれば自動で走る（preview branches の制限がない場合）
- Branch deploy が走らない場合: **Vercel ダッシュボード → Settings → Git → Deploy Branches** の設定を確認

## 5. GitHub redirect で動作しても remote URL は更新する

- repo を `tatoflam/SpecDrawing` → `meguruit/SpecDrawing` に transfer すると、GitHub が redirect で旧 URL を受け流すので **`git push` は動き続ける**が、`git remote -v` は古いままになる
- そのままだと「どこに push しているか」が読み取りにくい。新リモートに更新:
  ```bash
  git remote set-url origin git@github.com:meguruit/SpecDrawing.git
  ```

## 6. Vercel UI で「Build complete」と GitHub の「Deployment failed」が両立しうる

- Vercel: build は通ったが、`vercel.json` の `headers` config 適用時に reject → status は failed
- GitHub PR には Vercel の status check として "Deployment failed" が表示される
- build log を見ても compile error は出ていないので、`invalid-route-source-pattern` のような config 系エラーを **error log（build log とは別）** で探す必要がある

## Links

- [[05_learn/specdrawing-material-presenter]] — 適用先プロジェクト
- [[06_output/2026-05]] — 5cbda54 / 15fae13 の deploy 系 commit
- [[02_diary/2026-05-01]]
