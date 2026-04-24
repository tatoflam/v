---
title: Google Sheets の IMAGE() セルは Excel に移すと VLOOKUP で引けなくなる
category: 05_learn
tags: [google-sheets, excel, vlookup, image]
sources: [30f065c1-39c5-4b16-b150-7e326773e3b8]
updated: 2026-04-25
---

# Google Sheets の IMAGE() セルは Excel に移すと VLOOKUP で引けなくなる

## Summary

Google Sheets の `=IMAGE("url")` はセルの**値**として画像を保持するが、Excel にダウンロードすると画像はセル上の**浮動オブジェクト**に変換され、セル値は空になる。結果 `VLOOKUP(key, range, col, FALSE)` は **`#N/A` ではなく `0` を返す**（キー一致はしているが、引いた先の値が空）。機器リストなど画像付き資料を Excel でローカル閲覧する運用では、画像欄だけが動かなくなる。

## 症状

- Google Sheets 上では動いていた `=VLOOKUP(B18, 機器リスト!A2:D232, 2, FALSE)` が Excel で `0` を返す
- キー（例: `XAI-3A-4516（FUJIOH）`）は参照表に確かに存在する
- **`#N/A` ではなく `0`** が返るのがヒント: キーは一致しているが、引いた先セル（画像）の値部分が空として扱われている

## 根本原因

|  | Google Sheets | Excel（従来） |
|---|---|---|
| 画像の格納 | `=IMAGE("url")` でセルの**値**として格納 | セルの**上**に浮動オブジェクト配置（セル値ではない） |
| VLOOKUP で引ける | ✅ | ❌（値が空扱い） |

Google Sheets → Excel にダウンロードすると `IMAGE()` 関数は通常の浮動画像に変換される。変換後は VLOOKUP の参照対象から外れる。

## 切り分け（典型パターンとして覚える）

画像検索を含む VLOOKUP が Excel で `0` を返したら:

1. **`#N/A` でなく `0`** が返る → キー一致はしている。型不一致・空白混入・全角半角系は `#N/A` を返すので、この時点で除外できる
2. 参照表の該当セルをクリック
   - 数式バーに `=IMAGE(...)` や URL → IMAGE() がまだ残っている（Excel 365 なら案1で直せる）
   - 数式バーが空で画像だけ見える → 完全に浮動画像化。案1不可

## 対処案

### 案1. Excel 365 の `IMAGE()` 関数を使う（同等機能）

Excel 365（2023年以降）にも `IMAGE()` が追加された。参照表の該当列を `=IMAGE("URL")` に書き換えればセル内値として戻り、VLOOKUP が効く。

### 案2. INDEX/MATCH + 名前定義の画像ルックアップ（旧来テクニック）

1. 検索結果セルに `=INDEX(機器リスト!B:B, MATCH(B18, 機器リスト!A:A, 0))` という**名前定義**を作成（例: 名前 `機器画像`）
2. 画像を1つコピー → 貼り付けて、**数式バーに `=機器画像`** と入力
3. キーを変えると画像が切り替わる

### 案3. そもそも Google Sheets のまま運用する（今回採用）

画像付き資料を Excel に DL して配布すると VLOOKUP が機能しないので、閲覧・編集はブラウザで Google Sheets のまま行う。Excel 提出が必須なら画像抜きテキスト版を別途用意、PDF 配布なら画像は保持される。

## 配布ガイドの雛形

件名: 機器リスト Excel ファイルの運用方法について

- ブラウザ（Chrome 推奨）で Google Drive にアクセス → ダブルクリックで Google Spreadsheet として開く
- Excel でダウンロードすると画像が VLOOKUP で引けなくなる旨を明記
- PDF 配布時は「ファイル → ダウンロード → PDF」で画像保持

相手別の補足:
- 社内 → 共有リンクの閲覧/編集権限を明記
- 社外 → PDF 主、編集版 Sheet はリンクで
- Excel 提出必須 → 画像なしテキスト版を別途用意

## Links

- [[05_learn/google-sheets-multi-row-header]]
- [[02_diary/2026-04-24]]
