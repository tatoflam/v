---
title: YouTube → Knowledge 自動生成パイプライン — `--asr` opt-in / Claude few-shot Topics / 多言語 EN→JA
category: 05_learn
tags: [topic:research-pipeline, topic:llm-pipeline, topic:asr, tech:nodejs, tech:openai-whisper, tech:claude-sonnet, tech:youtube-transcript, tech:yt-dlp, tech:ffmpeg, project:threadsposts]
sources: [ce4cb7d1-c726-49a8-9b98-b1f7c1856063]
updated: 2026-05-04
---

# YouTube → Knowledge 自動生成パイプライン

## Summary

ThreadsPosts の `dept/research/` で「キーワード or YouTube URL → 文字起こし → Topics 整形 → K### Knowledge 保存」を 1 コマンドで貫通させる pipeline。OpenSpec change `research-pipeline-k006` で起票・実装・archive。capability 名は `research-pipeline`（OpenSpec 上 8 番目）。

特徴:
- **無料パス（timedtext）優先 + 有料パス（Whisper API）は `--asr` opt-in**
- **Topics 生成は Claude Sonnet 4.6 + プロンプトキャッシュ + K005 を few-shot**
- **多言語対応は Topics 生成段階の system prompt で「出力は常に日本語」固定**
- frontmatter は **プログラム側で確実に上書き**（LLM の hallucination 防御）

## Details

### CLI

```bash
npm run research -- --keyword "腸内環境 痩せ菌"      # キーワード検索 → 候補表示 → 番号で選択
npm run research -- --url <youtube-url>              # URL 直指定
npm run research -- --keyword "..." --auto-pick      # 1 位を自動採用
npm run research -- --url <url> --asr                # 字幕なし時に Whisper API 起動（opt-in）
npm run research -- --url <url> --asr=force          # 字幕あっても ASR を強制
npm run research -- --url <url> --asr=local          # ローカル Whisper（予約のみ・非実装）
npm run research -- --keyword "..." --dry-run        # API 叩かず動作確認
npm run research -- --keyword "..." --force          # 既存 K### に対する dedup を無視
```

出力先:
- `dept/research/knowledge/Transcripts/K###_<title>.md` — 生 transcript（frontmatter + `[mm:ss]` タイムスタンプ）
- `dept/research/knowledge/Topics/K###_<title>.md` — Topics 整形済（frontmatter + 観点 + 投稿ネタキーワード）

### モジュール構成（`pipeline/research/`）

| ファイル | 役割 |
|---|---|
| `index.js` | CLI dispatcher、6 フラグ処理、`--auto-pick` / `--force` / `--dry-run` ハンドリング |
| `youtube_search.js` | YouTube Data API v3 直叩き、再生数 × 新しさで top N |
| `transcript_fetch.js` | `youtube-transcript` (npm) で timedtext を取得、言語優先 `ja > en > その他` |
| `audio_download.js` | yt-dlp ラッパ、`/tmp/research-asr-*` に音声 DL、finally で sweep |
| `asr.js` | OpenAI Whisper API (`whisper-1`) を `verbose_json` で叩いて segments → `[mm:ss]` タイムスタンプ付 plaintext に整形 |
| `topic_synthesize.js` | Claude Sonnet 4.6 + cache_control + K005 few-shot で Topics 生成 |
| `write_knowledge.js` | frontmatter + ファイル名サニタイズ + 衝突検出 |
| `k_numbering.js` | Knowledge ディレクトリスキャン → 最大連番 + 1 |
| `dedup.js` | `source_url` 正規化 (v= パラメータのみ) で既存 transcript と衝突検出 |

### 字幕 / ASR の設計（D3 + D11）

**当初案**: `youtube-transcript` 一択、字幕なし動画は skip。
**変更後（user 主導）**: ASR opt-in。

| 手段 | 1h あたり | 月 60 本 | 多言語 | 字幕なし | 精度 |
|---|---|---|---|---|---|
| timedtext（デフォルト） | $0 | $0 | △ 字幕依存 | ❌ | △ 自動字幕雑 |
| Whisper API（`--asr`） | $0.36 | $21.6 | ✅ | ✅ | ◎ |
| Whisper local（`--asr=local`、予約） | $0 | $0 | ✅ | ✅ | ◎ |

「コスト判断を人手に残す」設計。デフォルト無料、`--asr` でユーザが明示的にコスト発生を承認。月額予算超過リスクを運用人手判断で吸収する。「自動でフォールバック」より「明示フォールバック」のほうが大量呼び出しでは安全。

ASR transcript file format:
- frontmatter: `generator: 'whisper-1'` / `lang: <whisper 検出言語>` / `duration_sec: <秒>`
- 本文: `[mm:ss] <text>` の plaintext、Whisper の `verbose_json.segments` から `start` を `mm:ss` 整形

### 多言語対応（D4）

`topic_synthesize.js` の system prompt に固定指示:

- 「**出力は常に日本語**」
- 英語等の他言語の字幕も日本語化して整形する
- **固有名詞は原語表記＋括弧内日本語訳**（例: `Akkermansia muciniphila（アッカーマンシア菌）`）

検証: BBC Global の 1667 chars 英語 transcript → 完全日本語 Topics 出力。4 観点 / 7 キーワード / 固有名詞・数字保持を確認。

### Claude Sonnet 4.6 + few-shot

- model: `claude-sonnet-4-6`（プログラム側で固定上書き、LLM 出力の `model:` フィールドは無視）
- システムプロンプトに **K005 の Topics 全文を few-shot 例**として埋める
- Anthropic SDK の `cache_control: { type: 'ephemeral' }` でシステム＋ few-shot 部分をキャッシュ → 2 回目以降のセッションで再利用される設計

### frontmatter は LLM に任せない

K007 生成時の bug 修正で確立した方針:

| 項目 | LLM に任せると | プログラム側で上書き |
|---|---|---|
| `model` | `claude-opus-4-5` を hallucinate | 実 SDK call で使った model 名を確実に書く |
| `topic_id` | `(unknown)` や `(URL指定)` | `--url` 時は YouTube oEmbed で title/channel 取得 |
| `source_url` | 引用形で歪む | normalize 済 URL（`v=` のみ）を書く |
| `generated_at` | LLM が日付ハルシネ | `new Date().toISOString()` |
| `transcript_path` | LLM 知らない | `write_knowledge.js` が確実に渡す |

LLM の役割は本文（観点 + 投稿ネタキーワード）のみ。frontmatter は `write_knowledge.js` が決定的に書く。

### system prompt の出力例にコードフェンスを使わない

K007 で発見した bug: system prompt が出力フォーマット例を ` ``` ` で囲んでいたら、Claude が ` ``` ` 込みで markdown を返してきた。出力例は plaintext で、プログラム側でフォーマットを固定する。

### dedup（D8）

URL 正規化で既存 transcript と衝突検出:
- `youtu.be/abc` / `youtube.com/watch?v=abc&t=10` → `youtube.com/watch?v=abc` に揃える
- 既存 K### の `source_url` と一致したら exit 1 + 該当 K### 表示
- `--force` で skip 可能（再取得・上書き）

### 採番（D7、K001-K005 legacy 対応）

- K001-K005 は手動で frontmatter なしで作られた legacy
- `k_numbering.js` はディレクトリ内のファイル名 `K\d{3}_` から数字部分のみ抽出 → 最大値 + 1
- frontmatter の有無に依存しない安全な採番

### 開発環境の前提

- Node.js v20+（実機は v25 で検証）
- `yt-dlp` と `ffmpeg` を local install（`brew install yt-dlp ffmpeg`）— `--asr` 時必須
- OpenAI billing 有効（auto-recharge 推奨、quota 切れで 429）
- openai SDK は **v6+ 必須**（v4 + Node v25 + ESM の multipart upload で `ECONNRESET` 発生）

### コスト実績（2026-05-04 セッション）

| Knowledge | source | 経路 | コスト |
|---|---|---|---|
| K006 | PIVOT「痩せ菌」(35分) | `youtube-transcript ja` | ~$0.08 |
| K007 | TED-Ed「How food affects gut」(5分) | `youtube-transcript ja (auto-translated)` | ~$0.05 |
| K008 | くるくるメディカル「大腸菌」(60秒) | **`whisper-1`** ($0.006) + Topics ($0.04) | ~$0.05 |
| **合計 3 本** | | | **~$0.18** |

月 60 本想定（1 日 2 本）でも:
- 全部 timedtext: ~$3
- 全部 ASR: ~$24（Whisper）+ ~$2.4（Topics）= ~$26.4

腸活ジャンルでは多くの動画に JA 字幕があるため timedtext 主体で運用、字幕なし動画に遭遇したら `--asr` で個別承認の予算枠（月 ~$5 想定）。

## 学び（横展開可能）

- **「コスト判断を人手に残す」opt-in 設計**: デフォルト無料、`--asr` で明示承認しないと有料 API は走らせない。月額予算の超過リスクは運用人手判断で吸収する
- **LLM の system prompt は出力例を ` ``` ` で囲むと literal コピーされる**: 出力例は plaintext で書き、プログラム側でフォーマットを固定する
- **frontmatter を LLM に任せない**: model 名 hallucination や `(unknown)` メタデータは frontmatter を Claude に任せる限り発生する。プログラム側で確実に上書きするのが安定運用
- **多言語パスのテストはコミュニティ翻訳字幕で迂回される**: TED-Ed が JA 字幕を持っていたために `youtube-transcript` の `ja > en` 優先順位で真の EN→JA 翻訳パスがスキップされた。BBC など報道系の英語のみ動画でテストするのが確実
- **Whisper の音声誤字は Claude が文脈で吸収する**: ASR の生 transcript には固有名詞誤字が含まれるが（「イイコリ」→ `E. coli`、「肝菌」→ `グラム陰性桿菌`）、Topics 生成段階で Claude が文脈から正しく解釈する。**ASR + LLM 二層構成の堅牢性の根拠**
- **openai SDK v4 → v6 upgrade で `ECONNRESET` 解消**: Node v25 + ESM 環境では openai SDK のメジャーバージョンを最新で揃える運用に
- **OpenSpec の `## ADDED Requirements` wrapper は spec sync 時に削除する**: change-side delta は wrapper 形式だが、main spec に sync する時は wrapper を外して plain spec に変換する。Purpose セクションは change-side からはコピーされないので別途追加

## Links

- [[03_work/threadsposts]]
- [[02_diary/2026-05-04]]
- [[05_learn/persona-driven-content-rules]]
- [[06_output/2026-05]]
