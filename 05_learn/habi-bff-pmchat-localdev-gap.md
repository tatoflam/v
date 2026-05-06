---
title: habi-bff PM Chat — SAM Local では /auth/login が通らない構造的ギャップ
category: 05_learn
tags: [topic:local-dev, topic:auth, tech:aws-sam, tech:lambda, project:habi-bff, entity:habi-identity]
sources: [c5c0230b-b3e6-43ae-ba7f-ea585ad01a6e]
updated: 2026-05-07
---

# habi-bff PM Chat — SAM Local では /auth/login が通らない構造的ギャップ

## 何が起きるか

`tools/pm-chat.html` をローカルで開いて `npm run sam:local` (`http://localhost:3000`) に
向けてログインしようとしても、`/auth/login` が応答しない / 拒否される。
**SAM Local 起動 + `npm run sam:build` 成功直後でも再現する。**

## なぜ通らないか（2 つの独立した原因）

### 原因 1：SAM Local の `env.json` に AuthProxyFunction エントリが無い

`/auth/{signup,login,refresh,logout}` は habi-bff の `AuthProxyFunction` が
`HABI_IDENTITY_API_BASE` 経由で habi-identity に HTTPS 透過プロキシする設計
（[CLAUDE.md](https://github.com/hlab-it-sys/habi-bff/blob/main/CLAUDE.md) ＆
[openspec/specs/auth/spec.md](https://github.com/hlab-it-sys/habi-bff/blob/main/openspec/specs/auth/spec.md)）。

`env.json` に AuthProxyFunction のエントリが無いと SAM Local のコンテナに
`HABI_IDENTITY_API_BASE` が渡らない → AuthProxy が habi-identity に到達できない。
**「以前ログインできた」という記憶があっても、それは AWS dev URL（`ww6knpkhu4...`）に
ブラウザから直接アクセスしていたとき**で、SAM Local では元から通っていなかった。

### 原因 2：`detectEnvironment()` が localhost で `proxy:development` を自動選択

[tools/pm-chat.html:1330-1332](https://github.com/hlab-it-sys/habi-bff/blob/main/tools/pm-chat.html#L1330-L1332)
の `detectEnvironment()` は localhost で開いたとき `proxy:development` を自動選択する。
ドロップダウンを開けば `same-origin` も含めて 3 択 (`same-origin` / `proxy:development` /
`https://...amazonaws.com/development`) が見えるが、開かない限り選べていない。

「環境セレクタに same-origin が表示されない」という症状は **ドロップダウンを開いていない
だけ** で、コードには定義されている。

## なぜ AWS dev URL でも今ログインできないか（独立した別問題）

habi-identity 側で以下のいずれかが起きている可能性が高い:

- パスワードリセット / DB 再作成
- `JWT_ACCESS_SECRET` のローテート（habi-bff と不一致になると 401）
- ユーザー record の削除

→ habi-identity リポ側で対応する別軸の作業。habi-bff のセッションでは触らない。

## 短期 workaround（PM Chat 検証を進める）

実フロー検証が必要な場合は **mock UI ボタン** で代替する:

1. `tools/pm-chat.html` をブラウザで開く（ローカルファイル直接でも、`http://localhost:3000/pm/chat` でも）
2. 画面下部の **`UI確認` ボタン** を押す → Pattern A / B / C が順次表示
3. Pattern C のメタデータを `▶` で展開して Attunement / Guard セクションを目視

これで UI 描画は確認できる。**実フロー（Lambda + OpenAI）の検証は §4.3 handler test
（4 ケース）+ §5.1 `npm run local:e2e` でロジックレベルでカバー済み**なので、
UI 描画のみ目視確認 + 実フローは §7.1 dev deploy 後に back-fill、で精神は満たせる。

## 中長期：SAM Local を完全動作させたい場合

別 change で以下を整備する:

- `env.json` に `AuthProxyFunction` エントリ追加（`HABI_IDENTITY_API_BASE` を local 値に設定）
- habi-identity をローカルで起動する仕組み（DynamoDB Local / LocalStack 利用版）、もしくは
  staging URL に向ける（その場合は staging データが汚染される懸念）
- `JwtAuthorizerFunction` の bypass 経路 or local テストユーザーの seed

これは PM Chat ローカル開発環境の地ならし作業で、本来の change スコープ
（attunement-policy / bff-guard などの capability 実装）とは別軸。混ぜると
change が膨らんで archive が遠のくので、**専用 change を切り出すのが筋**。

## 教訓

- **ローカル E2E が成立しないタスクは「mock UI 確認」「実フロー検証は dev deploy 後
  back-fill」「別 change で地ならし」の 3 択で user に委ねる**: A 案で進めると本 change を
  早く archive できて、別 change で地ならしを切り出せばスコープが膨らまない
- **「以前は動いていた」は構造分析で疑う**: SAM Local では元から通っていなかったのに
  「以前ログインできた」と言われる場合、参照していた URL（local vs AWS dev）が違う
  可能性を最初に確認する
- **環境セレクタの自動選択ロジックは UI 上で見えにくい**: `detectEnvironment()` のような
  自動選択がドロップダウンに反映されないと「選択肢が無い」と誤読される。デフォルト選択を
  視覚的に示すか、強制的にドロップダウンを展開する UX が要る

## 関連

- [[03_work/habi-bff]]
- 認証分離設計: `openspec/specs/auth/spec.md`（habi-bff repo）
- 関連リポ: `hlab-it-sys/habi-identity`（認証発行側）
