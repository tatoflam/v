---
title: milestone_mapping.yaml の process コメントアウト時の各サブシステム整合性
category: 05_learn
tags: [topic:milestone-mapping, project:meguru-pm-report, tech:python, tech:google-sheets, tech:yaml]
sources: [00db3a35-a07a-43bf-913e-97f2d41c1041]
updated: 2026-06-05
---

# milestone_mapping.yaml の process コメントアウト時の各サブシステム整合性

## Summary

`config/milestone_mapping.yaml` の `milestones[]` を **コメントアウトしてスプシ側の列は残す** 運用にしたとき、5 つのサブシステム (backup / writeback / alert / weekly-report / メール) がどう振る舞うか。**起点は `detect_layout()` の「ヘッダ行 完全一致」スキャン**。yaml に無いヘッダはレイアウトに含まれないため、ほぼ全ての処理が「該当列を素通りする」整合の取れた挙動になる。**ただし 1 つだけ手動クリーンアップが必須**: コメントアウト時点で背景色が朱/橙のセルは `milestone-alert` が触らなくなり、永久に塗り替わらない。

## Details

### 各処理の挙動

| 処理 | コメントアウト列の扱い |
|---|---|
| **backup** (`fetch_milestone`) | `detect_layout()` がレイアウト未検出 → `milestone.json.cells` から消える。**エラーにはならない** (threshold=3 を残存 process でクリアできれば) |
| **writeback** (`pm-master-writer`) | `bucket_to_entry` / `task_prefix` インデックスから除外 → `_current_achieved` が None → スキップ。書き込まれない (=書き戻しが止まるだけで誤書き込みは無い) |
| **期日近い/超過チェック+色塗り** (`milestone-alert`) | scan 対象は `layout.process_columns` のみ。コメントアウト列は **走査されない = 赤/橙色が更新されない**。**前回までの色が残置されたまま固定される** |
| **工程軸 進捗グリッド** (`weekly-report`) | グリッド行は `phase_buckets` (15 行 = Jooto checklist) で決まる。今回コメントアウトしたのは全て `phase_bucket: null` のものなので、**グリッドには元から出ていない** → 影響なし |
| **メールレポート 案件別セクション** | snapshot に無い列は出ない → 該当 process の「遅延/直近予定」は出ない |

### 残すメリット vs 削除のトレードオフ

**残すメリット**
- 過去の期日・実績チェック・申し送りメモが保全される
- yaml をアンコメントすれば元に戻る
- 手動運用列 (PM 目視管理用) として残せる

**残す場合の必須クリーンアップ**
1. **背景色の手動リセット** — `milestone-alert` が触らなくなるので、現在赤/橙のセルは**永久に塗り替わらない**。一度白に戻さないと「いつまで経っても期日超過」のような誤情報が固定表示される
2. ヘッダに `(運用停止)` 等のラベル追記は無効。`detect_layout()` は完全一致のため、yaml と一致しなくなった時点で素通りする — むしろ揃えて削除する方が安全側

**削除した方がよいケース**
- 該当列を**もう誰も見ない**のが確定している
- 列が右端寄りで、削除によるレイアウト崩れが小さい
- 背景色リセットを面倒に感じる

### ヘッダリネームは別問題

`仮受（意匠・構造）` → `仮受（意匠）` のような **ヘッダ文字列変更**は yaml と完全一致しなくなった瞬間に layout から落ちる。`detect_layout()` の起点となる完全一致仕様のため、**スプシ側のヘッダ文字列もリネーム後の表記に合わせる**作業が必須。コメントアウトとは別の操作。

### 色リセット手順

`/milestone-alert --dry-run` 後に `state/milestone_alert_*.json` を grep して、commented-out 列のセル一覧 (status = `overdue` / `upcoming`) を抽出 → スプシ画面で手動クリアで対応可。`milestone-alert` 本実行に投入する前に dry-run 結果を確認するのが安全。

### 2026-06-05 実測 (cleanup 後フルセット 1 周)

7 列コメントアウト + `仮受（意匠）` リネーム後の整合性検証 (`/jooto-backup --all-active --force` → `/pm-master-backup` → writeback dry-run → alert dry-run → 本実行 `--skip-email`):

- **layout detection** — 15 process columns 検出 (yaml active entry 数と一致)、`仮受（意匠）` も検出
- **commented-out リーク** — writeback / alert snapshot ともに混入ゼロ
- **writeback PATH 1** — `cells_planned: 0` (prev==curr で transition 無し、Jooto checked label と Milestone TRUE が完全同期している正常 no-op)
- **writeback PATH 2** (task_prefix-only) — コメントアウトで該当エントリ消滅 → 元から work 無し
- **milestone-alert color** — 360 セル走査 / 360 更新 / `hash_drift: []` (他シート不可触) / 20 overdue + 9 upcoming 検出
- **メール** — `--skip-email` で `skipped_reason: skip_email_flag` (送信なし)
- 色分布: done 195 / future 72 / not_applicable 64 / overdue 20 / upcoming 9

## Links

- [[03_work/meguru-pm-report]]
- [[05_learn/jooto-checklist-items-separate-endpoint]]
- [[02_diary/2026-06-05]]
