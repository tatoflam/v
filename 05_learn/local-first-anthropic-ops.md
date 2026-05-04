---
title: Local-First Anthropic Ops — Max plan を活かす二重課金回避と週次バッチ運用
category: 05_learn
tags: [topic:claude-code, topic:openspec, topic:anthropic-api, topic:cost-optimization, topic:weekly-cycle, topic:ooda, topic:human-jitter, topic:permissions, tech:nodejs, tech:github-actions, tech:launchd, principle:local-first-anthropic, project:threadsposts]
sources: [d40649e2-fb8b-4e0a-8c18-14bc3a972ea8, 57a002bd-6c29-47d4-ae0b-f42b43b5b03d, a73c0aa2-c9a4-46e3-ab60-72b6b426901a]
updated: 2026-05-04
---

# Local-First Anthropic Ops

## Summary

**Max plan x20 を払っているなら Anthropic API はローカル Claude Code から呼ぶのが正解**。GH Actions 等の CI に持ち込むと別建ての従量課金が発生し、二重課金になる。Max plan ($200/月固定) 内で消費できる枠を最大限使い、CI には **Anthropic を呼ばない workflow（外部 API のみ叩くもの）** だけを残す。

この原則を ThreadsPosts の会社運営パイプラインに適用すると **週次バッチ運用** + **3 段重ね reminder** の組合せに自然に収束する。1 セッション 30-90 分の集中タイムで「今週分終わり」の状態に到達するバッチ式 + OS / hook / 直接実行の冗長 trigger。`marketing-cycle-bootstrap` change で spec 化済（[[03_work/threadsposts]]）。

## Details

### 1. Local-First の根拠 — コスト構造

| 環境 | Anthropic API 呼出経路 | コスト |
|---|---|---|
| ローカル Claude Code | **Max plan x20 (OAuth)** | $200/月固定（既に支払い済） |
| GH Actions | API key (PAT 相当) | **追加課金 ($/token、月 $5-30 推定)** |

Max plan x20 は Anthropic アカウント単位の OAuth ベース課金で、GH Actions のような非対話的環境では使えない（OAuth flow が走らない）。CI から Anthropic API を呼ぶには別途 API key を作って従量課金されるルートに乗る必要があり、これは **Max plan を払い続ける限り二重課金**になる。

→ Max plan 解約時は GH Actions 移管も視野に入るが、**Max plan 継続中は Local-First 一択**

### 2. workflow の分離原則

**GH Actions に置く workflow の判定基準**: その workflow が Anthropic API を呼ぶか?

| 種類 | GH Actions 自動化 | ローカル実行 |
|---|---|---|
| `publish.yml`（Threads API のみ） | ✅ cron で自動 | — |
| `sync_metrics.yml`（Threads insights API のみ） | ✅ cron で自動 | — |
| `weekly_report.yml`（CSV 集計のみ、LLM 不使用） | ✅ cron で自動 | — |
| `resolve_affiliates.yml`（楽天市場 API のみ） | ✅ 手動 dispatch | — |
| **research（YouTube + Whisper + Claude Topics 合成）** | ❌ Anthropic 必須 | ✅ Local Claude Code |
| **generate（Claude による Drafts 本文生成）** | ❌ Anthropic 必須 | ✅ Local Claude Code |
| **B-MARKETING フェーズ（Claude による戦略合成）** | ❌ Anthropic 必須 | ✅ Local Claude Code |

**例外的に GH Actions で Anthropic を走らせたい場合の安全弁**: `workflow_dispatch` の inputs に `confirm_anthropic_cost: true` を必須にする。事故的な cron 自動課金を防ぐ

### 3. 週次バッチ = OODA ループの実装形

Local-First を前提にすると、Anthropic 課金を発生させる作業は **集中タイムにまとめる** のが自然になる。1 投稿ずつ毎日触ると認知負荷が分散して続かないので、**週 1 で 14 投稿分まとめて準備** するバッチ式が user の運用継続性にフィット。

7 フェーズ（OODA 構造）:

```
A REVIEW (Observe)        ← 先週の数字を見る
  ↓
B MARKETING (Orient)      ← 来週の戦略を立てる ← user 指摘で追加された
  ↓
C RESEARCH (Act 1)        ← Knowledge を仕入れる
  ↓
D CONTENT (Act 2)         ← Drafts を起こす
  ↓
E AFFILIATE (Act 3)       ← アフィリ紐付け
  ↓
F SCHEDULE (Act 4)        ← scheduled_at 配分
  ↓
G PUSH (Act 5)            ← commit + push
```

**B フェーズが抜けると OODA が短絡する**: Observe → Act 直結だと「先週の数字を見ても次の打ち手が決まらない」状態になる。B-1 仮説出し / B-2 affiliate モデル / B-3 persona 見直し（月初週は強制実行）/ B-4 戦略 ratify (status: draft → ratified → superseded) を入れる

戦略アウトプット格納: `dept/marketing/strategy/weekly/<ISO_week>.md`（Section 1-7 構造、`status` で世代管理）

### 4. 3 段重ね reminder（運用継続性の冗長化）

単一 trigger だと:
- オフライン時の通知見逃し
- Mac 開かない期間（旅行等）の取りこぼし
- skill を user が忘れる

→ **3 層冗長化**:

| Layer | 仕組み | 動作 |
|---|---|---|
| 1 | launchd plist（日曜 14:00 JST） | macOS 通知 + iMessage to self |
| 2 | Claude Code sessionStart hook | `check_weekly_due.js` が exit 1 なら system-reminder inject |
| 3 | user 直接実行 | `/weekly-cycle` を任意の時に叩く |

通知メディアは **macOS 純正 + iMessage to self のみ**（Apple ロックインだが user 環境最適）。Slack や Discord を入れない理由は「自分用 reminder に外部 SaaS の生死をのせたくない」

### 5. skill 名は kebab-case で統一

VS Code プラグイン / CLI / Web は全部共通の skill registry を見る。`PascalCase` で登録すると user が叩くべきは `/PascalCase` になり、user の指打ち感覚と合わない。**kebab-case で統一**:

- ディレクトリ: `.claude/skills/<kebab-name>/`
- frontmatter `name`: `<kebab-name>`
- SKILL.md / docs / tasks 内の言及: `/<kebab-name>`

`/weekly-cycle` で 3 環境すべて動作確認

### 6. dev 部署は account 軸を超える例外

`pipeline/` のコードは multi-tenant 化しても `dept/dev/pipeline/` に据え置く（`genres/<g>/shared/dev/` には入れない）。理由は **コード fork の発生を防ぐ**ため。

→ multi-tenant-bootstrap の `dept-organization` delta で明文化、`tenant-path-resolver` capability も `dept='dev'` を reject する設計

### 7. artifact mismatch は smoke で即停止

`/opsx:apply` 開始直後に artifact（tasks/specs/design）と実装環境（リポジトリの実態）がズレていることを発見したら、**即 stop して user に再 plan の選択を投げる**:

- 選択肢 A: artifact を実態に合わせて全更新して進める（scope 縮小も含む）
- 選択肢 B: 実態を artifact に合わせて作り直す（範囲外なら却下）
- 選択肢 C: 中止

タスクを進めながら型を変えると差分管理が破綻する。companify-bc-hybrid の Python → Node.js mismatch で確立したパターン

### 8. W19 サイクル実体検証で確認できた追加原則（2026-05-04）

`/weekly-cycle` 初実運用（1.5h で W19 完走、[[02_diary/2026-05-04]] §6 / [[03_work/threadsposts]]）で見えた運用上のディテール:

- **A REVIEW の Step 0 に `git fetch` 必須**: GH Actions が自動 cron で push してくる workflow（publish.yml / sync_metrics.yml / weekly_report.yml）の成果物を A フェーズで読むためには、ローカルセッション開始時に `git fetch origin` を回す必要がある。Local-First で「Anthropic 推論はローカル / 外部 API は GH」で分離していると、リモート側が独立に commit を積み上げる構造になる → 取り逃すと A REVIEW で先週レポートを見逃す。SKILL.md / orchestrator spec の Step 0 に明記すべき
- **GH Actions 自動 cron の独立性が並走で実証された**: ローカルセッション中に GH Actions が `D005 auto-publish` + `metrics.csv sync` を独立に push。ローカルの commit と衝突せず rebase 可能なファイル分離になっており、Local-First 分離設計の正しさが実体で証明された
- **default branch 保護を緩める settings 編集は literal 列挙承認が必須**: G PUSH で `git push origin main` が拒否され、`.claude/settings.local.json` の編集も harness が「user の `C` 一文字回答では self-permission 編集として不十分」と拒否。「`Bash(git push origin main)` を追加することを承認した」のように **対象ルールを literal に列挙** した user 承認が必要。今後の自動化は settings.local.json で許可ルールを明示しておく
- **決定論的 humanJitter は draft path ハッシュベース**: スケジュール時刻に「人間らしさ」を足す jitter は乱数だと再スケジュールで時刻変動が起きる。**FNV ハッシュ + 60〜599 sec オフセット**（同じ draft path に対して常に同じ jitter）で再現性を担保。下限 0 だと「24 秒」のような薄いオフセットが出るので下限 60 sec に設定

## Links

- [[03_work/threadsposts]]
- [[05_learn/youtube-knowledge-pipeline]]
- [[05_learn/openspec-retroactive-flow]]
- [[02_diary/2026-05-04]]
- [[06_output/2026-05]]
