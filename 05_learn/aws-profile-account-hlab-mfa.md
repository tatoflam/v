---
title: AWS プロファイル取り違いによる本番系 MFA-Deny (hlab default / bff-lambda-dev)
category: 05_learn
tags: [topic:aws-profile-account-mismatch, tech:aws-cli, tech:aws-iam, tech:sam, tech:cloudformation, project:habi-bff, client:hlab, stage:active]
sources: [6d328a3b-7b3e-44e1-bfd7-29bc66f889a7]
updated: 2026-07-04
---

# AWS プロファイル取り違いによる本番系 MFA-Deny (hlab default / bff-lambda-dev)

## Summary

hlab 側のローカル AWS 設定に **別アカウントの長期キー 2 本**が同居している状態で、`AWS_PROFILE` を指定せずに `sam deploy` を叩くと **本番系アカウント (MFA 必須ポリシー) に向かって Deny** される。表面症状は「MFA 忘れ」だが本質は「アカウント取り違い」。dev デプロイの正解は非 default プロファイル (`bff-lambda-dev`)。

## Details

### 誤ったモデル (最初の推測)

- default プロファイルの `CREW-USER` は組織共通の hlab 開発者 IAM
- `hlab-prod-MFA-required-policy` で MFA なし操作を Deny
- → `aws sts get-session-token` で MFA 一時クレデンシャルを発行すれば dev へデプロイできる

これで **一時クレデンシャル発行 → export → `npm run deploy:dev`** を 1 コマンドで走らせようとしたが、TOTP コード転送のレイテンシで `invalid MFA one time pass code` を繰り返した。ここで user 直感 「`crew-user_hlab_device` が指定されているのが違う気がする」で `~/.aws/config` を再精査。

### 実際の構造 (判明後)

| プロファイル | AWS Account | User | MFA | 用途 |
|---|---|---|---|---|
| **`default` = CREW-USER** | `864310138286` | crew-user | **必須** (`hlab-prod-MFA-required-policy`) | **本番系**。dev 用ではない |
| **`bff-lambda-dev`** | `062759670692` | `tatoflam` | 不要 | **dev**。`s3://habi-bff-deploy-dev` バケット・stack `habi-bff-dev` はこちらに存在 |

- dev リソース (`habi-bff-deploy-dev` バケット、`habi-bff-dev` スタック) は **062759670692 側にのみ存在**。default (CREW-USER) で叩くとバケット作成が本番系に向かって MFA Deny を食らう構造
- `~/.aws/config` の `bff-lambda-dev` ブロックには `role_arn` / `mfa_serial` は無く、**単純な別アカウント長期キー**が保存されているだけ

### 対処

- `AWS_PROFILE=bff-lambda-dev npm run deploy:dev` で **MFA 不要でそのまま dev デプロイ成功**
- CloudFormation `UPDATE_COMPLETE`、`NarrativeMemoryTable` (DynamoDB) 新規作成、全 Lambda 更新
- API endpoint: `https://ww6knpkhu4.execute-api.ap-northeast-1.amazonaws.com/development/`

## 再発防止の観点

1. **deploy スクリプト冒頭で `aws sts get-caller-identity` の Account/User を期待値と比較**。不一致で即 `exit 1` する assertion を入れる (samconfig の `profile` 明示だけでは呼び出し側 export で覆るので不十分)
2. **samconfig の `[dev.deploy.parameters]` に `profile = "bff-lambda-dev"` を明示** — CLI が `AWS_PROFILE` 未指定でも samconfig を読む
3. **開発者マシンの `~/.aws/config` に `[profile bff-lambda-dev]` を role で切る** のが本筋 (dev 側で assume-role 用の IAM を作り、default から `sts assume-role` する形にする)。今回は暫定的に別ユーザーの長期キーが並置されている状態で、キーローテーション事故のリスクがある
4. **README / CLAUDE.md に「dev は `AWS_PROFILE=bff-lambda-dev` を使う。default は本番系 (MFA 必須) で dev 用ではない」を明記** — 特に AI エージェント経由でデプロイする場合、default の Deny を「MFA 忘れ」と誤診しやすい

## 教訓 (一般化)

**同じ組織名の下に「開発」と「本番」の別 AWS アカウントがある構成**では、default プロファイルがどちらを指しているかが最重要。名前 (`CREW-USER`、`bff-lambda-dev`) や MFA の要否を見ても、実体は Account ID でしか判別できない。**`sts get-caller-identity` を assertion にして「意図した Account/User でデプロイしているか」を明示的にチェック**するのが唯一の再発防止策。

MFA Deny のエラーメッセージは強力に「MFA を追加すれば通る」というシグナルに見えるが、**explicit Deny policy が本番系にしか適用されていない場合、Deny 自体が「別アカウントに向かっている」証拠**。エラーの一次原因を疑う前に、まず Account ID を確認する。

## Links

- [[03_work/habi-bff]] — 2026-07-03 dev デプロイ H2 に運用文脈
- [[02_diary/2026-07-03]] — run-118 ingest の該当セッション
- [[06_output/2026-07]] — dev deploy URL の外部公開分
