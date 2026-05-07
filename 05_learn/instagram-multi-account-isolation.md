---
title: Instagram/Threads マルチアカウント isolation — 4 軸の boundaries と eSIM 副回線推奨
category: 05_learn
tags: [topic:instagram-multi-account-isolation, channel:instagram, channel:threads, tech:esim, tech:povo, anti-pattern:single-phone-multiple-accounts, lesson:device-fingerprint, lesson:composite-fingerprint]
sources: [99902682-b840-494b-b76c-59c90854c892]
updated: 2026-05-07
---

# Instagram/Threads マルチアカウント isolation

## Summary

1 人の運用主体が複数 IG/Threads アカウントを並行運用するとき、Meta 側の同一人物検知 (= 連鎖 BAN リスク) を避けるには **4 軸 (phone / IP / device / payment)** で boundaries を引く必要がある。最弱点は device 軸。電話番号は **eSIM 副回線で 1 デバイス N 番号** を取るのが現実的なベストプラクティス (povo 2.0 等で月額 ¥0-1000)。同じ番号で複数アカ作成は連鎖 BAN 確率最大なので回避必須。

これは [[03_work/threadsposts]] の BAN 後 pivot で 3 アカ並行運用設計の前提として整理した知見。`account-pivot-warmup/design.md` Decision 11 と一致。

## なぜ単純な「同じ電話番号で 3 アカ」が危険か

Meta は「同一人物のサブアカ判定」のために複数信号を AND で見る (= [[03_work/threadsposts]] Decision 7 reframe で言う composite fingerprint hypothesis)。同一電話番号での複数アカ作成は 1 信号で同一人物を直接立証する形になり、1 アカで違反検知された瞬間に連鎖 BAN を引く確率が最も高い構造。

```
1 phone → 3 IG → 3 Threads
   = 同一人物宣言の最強シグナル
   = 1 BAN → 即連鎖 BAN
```

## 4 軸の boundaries

| 軸 | 旧 (BAN 喰らった構成) | 推奨 (3 アカ並行運用) | mitigation の効きやすさ |
|----|---------------------|----------------------|----------------------|
| **Phone** | 1 番号で本アカ | **eSIM 副回線で 1 番号/アカ** (povo 2.0 等) | ◎ 完全分離可 |
| **IP** | datacenter (GH Actions cron + 自宅 VPN) | **自宅 IP / モバイル IP / 公衆 Wi-Fi の混在** で投稿、cron 廃止 | ○ 部分分離 |
| **Device** | 1 iPhone + 1 Mac の同居 | **別ブラウザ profile (Chrome / Firefox / Brave) + Threads web 化** | △ 完全分離は実質不可 |
| **Payment / 楽天 ID** | 1 楽天 ID で全アフィリ | **楽天 ID 3 つ独立** (account_1 = 即取得、_2/_3 = milestone 達成時) | ◎ 完全分離可 |

## 電話番号調達の 6 案比較

```
方法                            安全度  月額        手間   BAN 連鎖
─────────────────────────────  ─────  ─────────   ────   ────────
1. 同じ番号で 3 アカ            ✗     ¥0          最低   最大 (1→3)
2. 物理 SIM #1 + eSIM #2,#3     ◎     ¥0-2k       低     ✓ 独立    ★推奨
3. 物理 SIM 3 枚                ◎     ¥3-9k       中     ✓ 独立
4. IP 電話 (SMARTalk/050plus)   ✗     ¥300        中     -          IG 認証拒否事例多数
5. 家族の番号を 3 つ借りる      △     ¥0          最大   △          家族 identity 紐付けリスク
6. SMS API (Twilio 等)          ✗     ¥1k+        高     -          IG 認証拒否頻発、ロケール検知で弾かれる
```

**推奨は 2 (eSIM 副回線)**: iPhone 1 台で 3 番号運用可能、povo 2.0 は月額 ¥0 で番号維持できる (180 日間無料、6 ヶ月毎に ¥220 の有料トッピング 1 回購入で維持)。物理 SIM 3 枚は isolation は最大だが、コスト・物理管理コストが見合わない。

## Device 軸が最弱点である理由

別 SIM・別楽天 ID にしても、1 デバイス (iPhone or Mac) に複数アカ並行運用すると以下が同居する:

- **Browser cookie / cache** — IG/Threads が device fingerprint に使う JS-level signal
- **VPN history** — 過去に異なるアカで同じ VPN exit node を使うと exit IP の reuse で同一視
- **Font fingerprint / Canvas fingerprint** — Browser API で取れる device 固有情報
- **Push notification token** — Apple/Google の push token が device 単位で発行される

完全分離は **別物理デバイス** が原則だが、コストとオペレーション負荷で非現実的。**実用的 best effort** は:

1. **別ブラウザ profile** で各アカウントを分離 (Chrome profile_1 / profile_2 / profile_3 or Chrome / Firefox / Brave の組合せ)
2. **Threads web 化** でモバイルアプリ依存を切る (アプリは push token で device 同居を強くマーク)
3. **同一 device 内での再ログインを最小化** — 各アカで sign-in/sign-out をループしない、profile を生かしっぱなし

## Engagement の humanness 軸 (隣接トピック)

isolation 4 軸とは別に、**1 アカ内の振る舞いが人間らしいか** が並行で効く:

- 機械的 cadence (毎日同時刻) → 人間らしくない → inauthentic 分類器が反応
- engagement 受動性 (like/reply/scroll ゼロ) → humanness 信号がゼロ → 機械判定
- 100% affiliate 投稿 → 商業 spam 判定

[[03_work/threadsposts]] の `account-pivot-warmup` は warmup 4 週で humanness 信号 (人間らしい cadence + engagement + 非 affiliate 投稿の混在) を立てる設計で、これと isolation 4 軸が組み合わさって BAN 回避の主力対処になる。

## 段階的 scaling との接続

3 アカ並行 isolation の調達は **milestone driven** で段階的にやる (= [[03_work/threadsposts]] Decision 10):

```
Stage 1: account_1 単独運用中
  ─ 物理 SIM (既存メイン回線)、楽天 ID #1 (即取得)
  ─ +8w で BAN ゼロ + ¥50-100k ラン → Stage 2 起動判断
Stage 2: account_2 立上げ
  ─ eSIM #1 (povo 2.0) で番号 #2 取得、楽天 ID #2 取得
  ─ 別ブラウザ profile #2 を新規作成
Stage 3: account_3 立上げ
  ─ eSIM #2 (povo 2.0 2 つ目 or LINEMO) で番号 #3 取得、楽天 ID #3 取得
  ─ 別ブラウザ profile #3 を新規作成
```

milestone driven にすると 4 軸調達の負荷を分散でき、Stage 1 で踏んだ罠 (e.g. eSIM 認証で IG が弾く) を Stage 2/3 で回避できる。

## 学び (横展開可能)

- **isolation は 4 軸 AND で考える、1 軸完全分離では足りない**: 「電話番号は別にした」だけでは device fingerprint で同一視されうる。Composite fingerprint hypothesis ([[03_work/threadsposts]] Decision 7) と同じ発想で、Meta 側も複数信号の AND を見ている前提で設計する
- **device 軸の完全分離はコスト見合わない、best effort で割切る**: 「別物理デバイス + 別ネットワーク」が原則だが、3 アカ運用で 3 デバイス用意は非現実的。別ブラウザ profile + Threads web 化で対処、残るリスクは Stage 1 で実観測する
- **eSIM 副回線は 2026 年現在の現実解**: povo 2.0 / LINEMO 等で eSIM 1 番号 ¥0-220/月、iPhone 1 台で 3 番号運用可能。物理 SIM 3 枚と比べて isolation はほぼ同等で、コスト・物理管理が圧倒的に楽
- **電話番号同一は連鎖 BAN の最強シグナル**: 「1 番号で N アカ作成」だけは絶対に避ける。これは 1 信号だけで同一人物を直接立証する構造
- **milestone driven の調達は新規軸の罠を学習可能にする**: 「Stage 1 完走後に Stage 2 起動」を gate にすると、eSIM 認証 / 別 profile での IG 挙動 / 楽天 ID 取得 fricton 等の運用罠を 1 アカずつ実観測しながら蓄積できる

## Links

- [[03_work/threadsposts]]
- [[05_learn/persona-driven-content-rules]]
- [[02_diary/2026-05-07]]
