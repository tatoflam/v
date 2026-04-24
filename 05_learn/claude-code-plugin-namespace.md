---
title: Claude Code プラグインの名前空間と短縮コマンド
category: 05_learn
tags: [claude-code, plugins, commands]
sources: [bab023ec-53ee-4301-869d-306222b4a3f8]
updated: 2026-04-24
---

# Claude Code プラグインの名前空間と短縮コマンド

## Summary

Claude Code プラグイン内のスラッシュコマンドは、プラグイン名（`.claude-plugin/marketplace.json` の `name` フィールド）に応じて **名前空間付きでロードされる**。短縮形（名前空間なし）で呼べるかどうかは Claude Code 側の解決ルール次第で、**プラグイン名を変えると既存の短縮呼び出しが無効化** されることがある。

## Details

### 踏んだケース

MeguruPMReport で:

- 2026-04-23 以前: plugin name が `jooto-grabber` → `/jooto-backup` で動いていた
- 2026-04-24: commit `2157bb7 Rename plugin to JootoGrabber` で PascalCase にリネーム → `/jooto-backup` が `Unknown command: /jooto-backup` で叩けなくなった
- 同時期に追加した `PMMasterGrabber` の `/pm-master-backup` も同様に名前空間付きでのみロード

**正しい呼び出し形**:

```
/JootoGrabber:jooto-backup --all-active
/PMMasterGrabber:pm-master-backup
```

### プラグイン命名の実務ガイド

- 短縮形で呼べるかは **確約されない**。常に `/{PluginName}:{command}` 形で書ける前提で設計する
- リネームするときは **既存の短縮呼び出しがすべて無効化される** 点を change 起票時に明記（CLAUDE.md や README、ドキュメント中の参照をすべて namespaced に変える）
- VS Code の Claude Code 拡張 / ターミナル CLI で挙動差は**無い**（両方とも namespace 必須、ハーネスではなくプラグイン解決ロジックの問題）

### 新規プラグインの hot-reload

`.claude-plugin/marketplace.json` と `.claude/settings.json` に追加しても、**Claude Code が既に起動中のセッションでは reload されない**。対処:

1. `/plugin` で有効プラグイン一覧を確認
2. 出ていなければ marketplace refresh、それでもダメなら **VS Code / ターミナルを再起動**
3. `enabledPlugins` のキー形式が `"PluginName@marketplace-name"` で正しいか再確認

## Links

- [[03_work/meguru-pm-report]]
- [[05_learn/wiki-automation-pipeline]]
