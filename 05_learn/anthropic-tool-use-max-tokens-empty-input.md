---
title: Anthropic SDK が空 input の tool_use ブロックを返す = max_tokens 打ち切りシグネチャ
category: 05_learn
tags: [topic:anthropic-tool-use, topic:claude-api, tech:anthropic-claude, tech:python, project:todobot]
sources: [cb878ae5-38c1-4e42-a2dd-56eae9f219f2]
updated: 2026-05-29
---

# Anthropic SDK が空 input の tool_use ブロックを返す = max_tokens 打ち切りシグネチャ

## Summary

Anthropic Messages API (`claude-sonnet-4-6` 含む) で **tools** を渡したリクエストが `max_tokens` で出力途中で切られると、レスポンスは `HTTP 200 OK` のまま `tool_use` ブロックの `input` が空辞書 `{}` で返ってくる。`stop_reason="max_tokens"` は付くが、tool 名は埋まっており呼び出し意図は伝わるため「ツールを正しく呼んだが引数が空」のような誤読を生みやすい。受信側のバリデーションが空 input を `ValueError` で弾くと、上位は「ツール呼び出し成功 → 出力 0 件」として silent fail に近い挙動になる。

トリガは「**system + tools + few-shot** で 3,500 tok 程度を入力し、出力 JSON が `max_tokens` (デフォルト 4096) を超える長さで来るケース」。messages_in が増えるほど出力 ToDo 件数も増え、JSON が肥大化して打ち切られる。

## 発見経路 (2026-05-28 ToDoBot 1課 18:00 初回配信失敗)

[[03_work/todobot#ステータス (2026-05-28) — `1課` プロファイル投入 + extraction max_tokens 4096→16384 修正]] の調査で発覚。

- 1課 (`claude-sonnet-4-6`) 18:00 slot で `messages_in=231`、結果 `todos_extracted=0, status=failed`
- 同じ Sonnet で 2課 は `messages_in=119, todos_extracted=20` で成功
- ログのエラー本文: `ValueError: tool_use block for record_todos has empty input`
- HTTP は `200 OK` で返っており、SDK exception や rate limit ではない

シグネチャの構造:

```
Response: status=200, content_blocks=[
  {"type": "tool_use", "id": "...", "name": "record_todos", "input": {}}
]
stop_reason: "max_tokens"
```

`input={}` は「ツール意図を JSON で出力し始めたが、3000 字を超えた辺りで token 上限に達して中断、確定済みの key/value ペアが 1 つも無いまま JSON が閉じられた」状態。一見「LLM が tool を呼ぼうとして引数を出せなかった」エラーに見えるが、実際は出力長の問題。

## 受信側 (todobot/llm.py) の弾き方が silent fail を強める

ToDoBot の `llm.py:120` 付近 (本リポは v 0.5.0):

```python
if block.type == "tool_use" and block.name == "record_todos":
    if not block.input:
        raise ValueError("tool_use block for record_todos has empty input")
    return block.input
```

この raise を上位 `daily_report.py` の `try / except` が `status=failed` でログに出し、配信スキップで終了する。Cloud Logging に message は出るが、user 視点では「2課 は通知出たが 1課 は何も来なかった」だけ — 通知 0 件と silent fail の区別がつかない。

(本 silent fail は LINE/メール宛先の運用 noise を増やすので、扱いは本ノートの「再発防止策」を参照)

## 再発防止策 (重要度順)

1. **`max_tokens` を明示的に上限近くまで上げる**: ToDoBot は 4096 → **16384** に変更 ([[03_work/todobot#パッチ]])。Anthropic Sonnet は 1 messages call で 64k token まで出力可。`max_tokens` を明示しないと SDK default の 4096 が効くので、構造化出力系では明示が必須
2. **`stop_reason="max_tokens"` を例外条件として扱う**: SDK レスポンスの `stop_reason` を見て、`max_tokens` のときは別 exception (`OutputTruncatedError` 等) を投げる。`ValueError("empty input")` ではなく真因がログに出るのでデバッグ時間が縮む
3. **入力規模からの保護**: messages_in が一定量を超えたら事前に分割呼び出しする (例: 200 msg ごとに `extract_with_tool` を分けて結果をマージ)。Anthropic 課金は max_tokens 設定ではなく**実出力 token** ベースなので、過大な max_tokens を常時設定してもコスト的には問題ない (出力 token 数次第)。SLA 的な response time は `max_tokens` の上限ではなく実出力長に依存
4. **動的 `max_tokens`**: 経験則として `messages_in * 60` 程度を上限値の式にする (`min(64000, max(8192, messages_in * 60))`)。1課 5-28 = 231 msg × 60 ≈ 13860 → 16384 でちょうど良い

## 関連: tool_use の input が **部分埋まり** で返るケース

`max_tokens` 打ち切りでも、`input` が完全に空ではなく一部 key だけ埋まって途中で閉じられるパターンもある (生成プロセスが key/value を順に出していた途中で切れる)。`input` の存在チェックだけでなく、tool schema 上の required key が揃っているかを検証すべき。`record_todos` の場合は `todos: list[Todo]` が空リスト `[]` で返って来るバリアントも理屈上ありうる (LLM が記述開始前で力尽きた場合)。

## モデル別の打ち切り挙動 (実測 / 観測ベース)

| モデル | 既定 max_tokens | 観測した「打ち切り→空 input」 | コメント |
|---|---:|---|---|
| claude-sonnet-4-6 | 4096 (SDK default) | あり (本ノート由来) | tools + 大量 messages_in で再現性高い |
| claude-haiku-4-5 | 4096 (SDK default) | 未観測 | ToDoBot は当初 Haiku、5-21 段階では未遭遇 |
| claude-opus-4-7 | 4096 (SDK default) | 未観測 | Opus は出力 quality 重視のため少ない件数で完結する傾向 |

(Haiku で未観測なのは入力規模が小さかったため。同じ messages_in 量を流せば再現するはず)

## Links

- [[03_work/todobot#ステータス (2026-05-28)]] — 本ノートを生んだ 1課 18:00 初回配信失敗の調査記録
- [[05_learn/todobot-line-mvp]] — ToDoBot 設計全体、Anthropic API 利用方針
- [[02_diary/2026-05-28#07:47  ToDoBot 1課 profile]] — セッション ingest entry
