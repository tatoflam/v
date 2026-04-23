---
title: MeguruPMReport
category: 03_work
tags: [meguruit, jooto, weekly-report, python]
sources: [3e07de94-4eea-46b3-892a-e815cd133f4e]
updated: 2026-04-24
---

# MeguruPMReport

## Summary

Meguru 案件の **週次アップデート** を Gmail と Jooto から Claude Code 上で生成するワークスペース。仕様の SoT は `openspec/specs/`、スラッシュコマンドは `/weekly-report` と vendored plugin `jooto-grabber/`。

## Details

### リポジトリ
- ローカル: `/Users/tato/repo/github/meguruit/MeguruPMReport`
- リモート: `git@github.com:meguruit/MeguruPMReport.git`（2026-04-24 に初push、main 直 push は初回のみ承認で通した）

### 典型ワークフロー
```
/jooto-backup --all-active       # 差分同期
/jooto-overdue-scan              # 期日超過の深掘り源泉
/weekly-report                   # 週次レポート生成
```

### Python 環境（plugins/jooto-grabber）
- **Python 3.10.11**（`.python-version` で pyenv に指示、`.gitignore` 対象なのでコミットされない）
- **venv**: `plugins/jooto-grabber/.venv`（editable install + dev extras）
- 旧ワークスペース（`tatoflam/...`）から vendor-in した際に venv パスが破損するので、`python -m venv --clear .venv` で作り直す
- pytest 54 件（2026-04-24 時点）

### 運用ルール（CLAUDE.md 抜粋）
- Gmail は **厳格 read-only**：`search_threads` / `get_thread` のみ、送信・下書き・ラベル操作禁止
- Jooto も read-only、コメント/チェックリスト取得は期日超過タスクに限定（コスト抑制）
- 変更は **OpenSpec change 起票が先**（`/opsx:propose`）、コード先行禁止
- 元リポジトリ（Plugins-Bizuayeu/JootoGrabber）と元ワークスペース（ClaudeWork/MeguruPM）は編集禁止

### Git push の前提
- `eval \`ssh-agent\`; ssh-add -k ~/.ssh/id_rsa7; ssh-add -k ~/.ssh/github_rsa` を **同一 Bash 呼び出し**で実行してから push
- 詳細: [[05_learn/ssh-agent-shortcuts]]

## Links

- [[02_diary/2026-04-24]]
- [[05_learn/ssh-agent-shortcuts]]
- [[06_output/2026-04]]
