---
title: ハニーポット誤爆 (autofill が bot 判定を引く)
category: 05_learn
tags: [topic:bot-defense, topic:honeypot, topic:form-ux, tech:html, tech:css, tech:javascript, tech:apps-script]
sources: [dd13e6ac-719c-47ef-9063-6077e615ab5f]
updated: 2026-07-02
---

# ハニーポット誤爆 (autofill が bot 判定を引く)

## 症状

フォーム submit → 「申込を受け付けました」風の **完了画面が出る** のに、実際は
バックエンドで bot と判定されて **drop されている** サイレント失敗。ユーザー本人は
成功したと思っているため苦情も来ない → 発覚が遅れる。

## 原因

ハニーポット (=人間には見えず bot だけ埋める隠し input) が **正規ユーザーの自動入力
ツールに拾われる** のが典型。以下の 2 条件で高確率で誤爆する:

1. **欄名が汎用**: `company` / `address` / `phone` / `website` などは Autofill /
   1Password / Chrome の保存パスワード / パスワードマネージャに **辞書 hit しやすい**。
2. **CSS が画面外配置 (`left:-9999px` / `top:-9999px` / `visibility:hidden`)**:
   これらは **DOM には残る** ため、自動入力エンジンから見て「見えている input」と
   判定される。DOM ツリーからは除外されない。

## 3 原則 (誤爆させないハニーポット)

1. **欄名を汎用にしない**
   - `nickname2` / `middle_name` / `secondary_email` など、
     autofill ヒューリスティックに hit しにくい名前を選ぶ
   - ランダム suffix (`hp_a3f2`) を付けるのも defensive
   - `id`/`name` の両方を変更する (autofill は両方見る)

2. **CSS は `display:none` にする (DOM 除外)**
   - `display:none` は **DOM ツリーから実質除外**、autofill 走査対象外
   - `position:absolute; left:-9999px` は **NG** — 見えないだけで DOM 上は残る
   - `visibility:hidden` も同様に NG
   - `aria-hidden="true"` + `tabindex="-1"` + `autocomplete="off"` を併記して
     bot にはハニーポットのまま見えつつ、人間の tab フォーカスから逃がす

3. **誤爆時のレスポンスを「エラー表示 + 救済導線」にする**
   - **「完了風のサイレント成功」は禁じ手** — debug 不能で最悪の UX
   - 「送信できませんでした。パスワード管理ツール / ブラウザ自動入力を一度無効に
     してから再送信してください。または `<連絡先>` まで直接ご連絡ください。」
     のような明示エラー + fallback 導線を返す
   - サーバ側で bot 判定した場合も同様。silent drop は運用者の可視化 (logs) を
     除いて **ユーザー側からは事故と区別できない**

## 補助的な防御

ハニーポット単体では上記の誤爆リスクがあるため、以下と併用するのが安全:

- **サーバ側での多重チェック**: 空フィールド以外にも「送信間隔が異常に短い」
  「User-Agent が bot」等の二次判定
- **Cloudflare Turnstile / hCaptcha** の invisible mode: 人間のインタラクション
  シグナルで判定、autofill と誤爆しない
- **rate limit / IP throttle**: バックエンド側で

## 出典

- session `dd13e6ac` (`tatoflam/minami-gakudo-tshirt`, 2026-06-27, commit
  `167d4de`): 本番公開後の T シャツ申込フォームで **`company` 欄 + `left:-9999px`
  CSS** の組み合わせが Chrome 自動入力に拾われて誤作動、正規ユーザー数件が
  「完了画面出るのに登録されない」サイレント失敗を報告。3 原則すべて適用して修正
  (`company` → `nickname2` / `display:none` / エラー明示化)
- [[04_life/minami-gakudo-tshirt-site]]
