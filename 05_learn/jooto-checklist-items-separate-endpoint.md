---
title: Jooto API のチェックリスト items は別エンドポイント
category: 05_learn
tags: [topic:jooto-api, tech:python, tech:jooto, project:meguru-pm-report]
sources: [5d8213db-5b81-4f67-a4aa-86c85e83d3af]
updated: 2026-05-30
---

# Jooto API のチェックリスト items は別エンドポイント

## Summary

Jooto REST API の `/v1/tasks/{task_id}/checklists` は **チェックリストの「ヘッダ」(ID + 名前) しか返さない**。実際の items (チェック項目本体) を取るには **別エンドポイント `/v1/checklists/{checklist_id}/items` を叩く必要がある**。さらに、items の表示テキストフィールドは `name` でも `title` でもなく **`content`**。`MeguruPMReport` 上の `/jooto-overdue-scan` は約 4 ヶ月この事実に気付かず、過去 43 件の `data/jooto/.../overdue.json` がすべて `unchecked_checklists` 空のまま週次レポートに供されていた (silent bug)。

## Details

### エンドポイントの構造

```
GET /v1/tasks/{task_id}/checklists
→ [{ "id": 12345, "name": "マイルストーン", "task_id": <task_id>, ... }]
   # ★ items フィールドは付かない

GET /v1/checklists/{checklist_id}/items
→ [{ "id": 67890, "content": "前提整理", "is_checked": true, ... }]
   # ★ 表示テキストは content (name/title ではない、API doc 未明記)
```

つまり「タスク内のチェックリスト 1 つの内容を全部取る」だけで **少なくとも 2 リクエスト** 必要。チェックリストが N 個あれば 1 + N リクエスト。

### なぜ 4 ヶ月気付かなかったか

`/jooto-overdue-scan` の元実装は `/v1/tasks/{id}/checklists` のレスポンスをそのまま `unchecked_checklists` 配列に流し込んでいた。レスポンスにはヘッダしか入ってないので **空配列ではなく `[{id, name}, ...]` のリスト**は返る。テスト fixture も同じ shape を返すモックで作っていたので、structurally は valid。

`is_checked` が無い → 「未チェック扱いで取り出す」フィルタ条件にすると items 自体が無いので **常に空配列**が `unchecked_checklists` に入る。これが「PM が未チェック項目を週次レポートで一度も見ていない」状態を 4 ヶ月続けさせた。

### `add-milestone-sync` での修正 (2026-05-29)

`plugins/jooto-grabber/scripts/application/checklists.py` に共通モジュールを切り出し:

- `fetch_task_checklist_headers(task_id)` — ヘッダのみ
- `fetch_checklist_items(checklist_id)` — items 本体
- `fetch_task_checklists_with_items(task_id)` — 2 API を結合して `[{id, name, items: [...]}]` を返す

`/jooto-overdue-scan` (既存) と `/jooto-backup` の新 `progress_checklist` 取得 (今回追加) の両方を `fetch_task_checklists_with_items` 経由に統一。1 修正で 2 機能のバグが同時解消。

### 教訓 (再発防止)

- **API レスポンスの shape は doc よりも実物を信じる** — Jooto API doc は items の取得方法を明示していない、フィールド名も `content` と書いていない。実物を curl で叩いて目視確認するのが最終的に唯一の確認手段
- **「常に空配列」を valid と見なすテスト fixture は危険** — empty が正常ケースとして混ざる API では、テストで non-empty な実データを 1 件以上は通すべき
- **チェックリスト周りは N+1 API コスト** — Jooto は 1 タスクあたりチェックリスト数 + 1 リクエスト、全タスク × 全チェックリストで爆発する。`MeguruPMReport` 側では「期日超過タスク」+「進捗状況タスク」だけに絞ってコスト抑制 (CLAUDE.md の Jooto 扱い節に明記)

### Jooto API その他のフィールド名特異点

- チェックリスト**ヘッダ**の名前は `name`
- チェックリスト**項目**の表示テキストは `content` (← ここが混乱の元、ヘッダと不揃い)
- `is_checked` (bool) — TRUE / FALSE 状態
- ボード `updated_at` は **チェックリスト項目のチェック変更で更新されない** ので、`jooto-backup` の差分同期 (`board.updated_at` で skip 判定) では新規 progress 取得が漏れる。`progress_checklist` は sync_state と独立して fetch するか、`--force` で全件取得する必要あり (将来課題、現状は force で回避)

## Links

- [[03_work/meguru-pm-report]] — 修正着地先 (`### 2026-05-29 add-milestone-sync 実装着地`)
- [[02_diary/2026-05-30]]
- [[05_learn/google-sheets-multi-row-header]] — 同様に API レスポンス shape を実物で確認した事例
