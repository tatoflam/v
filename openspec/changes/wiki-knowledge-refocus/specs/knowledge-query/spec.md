# knowledge-query

問い合わせ応答。`/wiki-query` を Vault の一次インターフェースとし、curated 知識層と分身モデルを根拠に citation 付きで応答する。

## ADDED Requirements

### Requirement: curated 層優先の応答
`/wiki-query` は curated 層（00_self / 03_work / 04_life / 05_learn / 06_output / home.md）を一次参照として回答を構成しなければならない（SHALL）。回答には根拠ページへの citation（wiki-link）を含めなければならない（MUST）。「現在の状態」「決定事項」「手順・Runbook」の標準セクションを質問の型（今どうなってる／なぜ決めた／どうやる）に対応付けて参照しなければならない（SHALL）。

#### Scenario: 状態質問
- **WHEN** 「MeguruPMReport は今どうなってる？」と問い合わせた
- **THEN** 03_work/meguru-pm-report の `現在の状態` を根拠に、citation 付きで最新スナップショットが回答される

#### Scenario: 決定理由の質問
- **WHEN** 「なぜオペレーティングリースはエミルでやることにした？」と問い合わせた
- **THEN** 該当ページの `決定事項` を根拠に、決定日と理由が citation 付きで回答される

### Requirement: 鮮度の開示とフォールバック
curated 層に回答がない、または staging / queue に未反映の関連情報がある場合、`/wiki-query` はその旨を明示しなければならない（SHALL）。staging・02_diary から補完して回答する場合は「未整理情報からの回答」であることをラベル付けしなければならない（MUST）。

#### Scenario: 未 distill 情報がある
- **WHEN** 質問に関連するダイジェストが staging に未処理で存在する
- **THEN** curated 層からの回答に加え、未整理の staging 情報からの補足が区別されて提示され、`/wiki-distill` の実行が提案される

#### Scenario: 知識層に情報がない
- **WHEN** vault のどこにも回答根拠が見つからない
- **THEN** 「vault に情報がない」と明示し、推測で回答しない

### Requirement: 分身としての応答
人格・嗜好・判断基準・目標に関する質問に対し、`/wiki-query` は 00_self を一次根拠として回答しなければならない（SHALL）。

#### Scenario: 嗜好の質問
- **WHEN** 「メール文面はどういうスタイルが好みだっけ？」と問い合わせた
- **THEN** 00_self/preferences.md（および関連 feedback 記録）を根拠に citation 付きで回答される

### Requirement: 読み取り専用の維持
`/wiki-query` は vault の内容を変更してはならない（MUST NOT）。例外は log.md への実行記録 1 行の追記のみとする（現行踏襲）。

#### Scenario: 問い合わせ後の vault 状態
- **WHEN** `/wiki-query` が実行された
- **THEN** log.md の 1 行追記以外に git diff が発生しない
