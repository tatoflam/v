---
title: 外部向けリリース計画は observability capability でゴールを言い切る
category: 05_learn
tags: [topic:planning, topic:llm-agent-comms, topic:relationship-os, project:habi-bff, aspect:planning]
sources: [6d328a3b-7b3e-44e1-bfd7-29bc66f889a7]
updated: 2026-07-04
---

# 外部向けリリース計画は observability capability でゴールを言い切る

## 学び

**日付 + 機能数** で外部向けリリース計画を語らない。**「Founder/PM が品質を観測・
判断・調律できる状態」** の到達をゴールとして言い切る。ガードレール型の
Relationship OS (Habi のような) では特に効く。

## 起きたこと

Habi Ver1.0 で「約 3 ヶ月 (〜2026-09 中旬) で Series A デモまで前倒し」と外部
文書に書こうとした際、PM 側の LLM (Habi = ChatGPT) が以下のようにレビューを
返してきた:

> Ver1.0 を 3 ヶ月で前倒しするには、CTO 側は器を先行できる。
> ただし、Policy 確定と Seed 作成は Founder/PM がやらないと、Habi 品質の
> 調律ができない。したがって、返答ではこう補正した方がよい:
> 「2026 年 9 月中旬を目標とする。ただし、ゴールは機能数の完了ではなく、
> Founder/PM が Habi 品質を観測・判断・調律できる状態」

理由:

- Habi の場合、Policy と Seed は Founder 依存で、CTO 側だけで完結できない
- 日付 + 機能数だけ書くと、実装側 (CTO) が Habi の意味 (Attunement 5 段 /
  Output Type / Verdict / Prompt Contract / Narrative Memory boundary) を
  勝手に固めて「完了」判定しがち → Habi 品質のドリフト
- 「観測・判断・調律できる状態」なら、器の完成度と調律の準備が両方揃った
  時点をゴールにできる

## なぜこれが効くのか

**Relationship OS のような "品質は運用側で決まる" プロダクトでは、リリース
定義自体を器側で完結させると必ず品質がブレる**。ゴールを observability
capability で書けば:

1. CTO 側は「調律できる状態を作る」に集中できる (作りすぎず、削りすぎない)
2. Founder/PM は「調律余地を残してもらった器」を受け取れる (自分の判断で
   Habi 品質を決めきれる)
3. 外部 (投資家 / Series A) には「調律可能な器 + 判断者としての Founder」の
   セットで見せられるので、Habi の付加価値がぶれない

## 適用範囲

- Habi Ver1.0 のような **Relationship OS / Guardrail 型** の Roadmap 文書
- 他プロダクトでも、外部向け文書で **意味決定が実装外にある** (契約 / 法規 /
  ドメイン専門家 / 顧客判断) 場合に転用可能
- **CI / CD / エンジニアリング内部**の Roadmap には過剰。機能数ゴールで OK

## 逆パターン (やらない方がいい書き方)

- 「12 月までに 30 機能実装」
- 「Attunement 5 段を全部埋める」
- 「Seed 25 本を全部通す」

これらは CTO 側だけで完了判定できてしまうため、Founder/PM が「Habi じゃ
ないなあ」と感じる余地が消える。

## Links

- [[03_work/habi-bff#2026-06-16 → 2026-07-03 — PM 260613 統合 + 前倒し (2026-09中旬目標) + Founder Master 260618 canonical 化 (session 6d328a3b)]]
- 出典 (Habi 側 GPT レビュー): session `6d328a3b` turn 12 抜粋
