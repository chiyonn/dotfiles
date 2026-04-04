---
name: organize
description: |
  Use when ~/Downloads has files to clean up.
  「整理」「Downloads片付けて」「organize」「ダウンロード整理」などのキーワードで発動。
---

# Downloads Organizer

~/Downloads を常に空に保つためのスキル。

## 実行手順

### Step 1: 定常クリーンアップの実行

まず `auto-clean.sh` を実行して、確認不要な定常処理を一括で片付ける。

```bash
bash ~/.claude/skills/organize/auto-clean.sh
```

このスクリプトは以下を自動実行し、JSON で結果を返す:
- rules.yaml の `action: delete` ルールに該当するファイルを削除
- rules.yaml の `action: move`（画像→~/Pictures）を実行
- 対話が必要なファイル・未マッチファイルを `remaining` リストとして返す

### Step 2: 残りファイルの対話処理

Step 1 の `remaining` にファイルがある場合のみ、以下を行う。

#### mp3 ファイル（move_and_rename）
1. ファイル名からメタデータを推測する
   - `ytmp3free.cc_` や `-youtubemp3free.org` などのゴミを除去
   - ハイフン区切りをスペースに、各単語をタイトルケースに
2. 推測結果をユーザーに AskUserQuestion で確認
   - 例: 「`ytmp3free.cc_waves-youtubemp3free.org.mp3` → `Guthrie Govan - Waves.mp3` でOK？」
   - ユーザーが修正した場合はその名前を使う
3. リネーム+移動を実行
```bash
mkdir -p ~/Documents/"REAPER Media"/reference
mv "元ファイルパス" ~/Documents/"REAPER Media"/reference/"リネーム後ファイル名"
```

#### 動画ファイル（ask）
AskUserQuestion でユーザーに質問する。選択肢:
- **移動**: 移動先パスを指定してもらう
- **削除**: rm する
- **放置**: 何もしない（今回はスキップ）

#### その他の未マッチファイル（ask）
上記と同じく AskUserQuestion で個別に確認する。
似たファイルが複数ある場合はまとめて1つの質問にしてよい。

### Step 3: サマリー表示

処理完了後、結果をまとめて表示する:

```
## 整理結果

| アクション | ファイル | 詳細 |
|-----------|---------|------|
| 削除 | tasmate-prod-xxx.dump | auto-clean.sh |
| 移動 | screenshot.png → ~/Pictures/ | auto-clean.sh |
| リネーム+移動 | ytmp3... → Guthrie Govan - Waves.mp3 | 対話確認 |
| スキップ | something.txt | ユーザー判断: 放置 |

auto-clean: 削除N件, 移動N件 / 対話処理: N件 / 残り: N件
```

### Step 4: ルール学習の提案

Step 2 で ask した結果、パターンが見えた場合（例: .csv は全部削除した等）、
rules.yaml **および** auto-clean.sh への新規ルール追加を提案する。

ユーザーが承認したら、両方を更新する。

## ファイル構成

| ファイル | 役割 |
|---------|------|
| `SKILL.md` | スキル定義（このファイル） |
| `rules.yaml` | ルール定義（信頼できるソース） |
| `auto-clean.sh` | 定常処理スクリプト（rules.yamlの delete/move を実装） |

**重要**: rules.yaml にルールを追加したら auto-clean.sh にも対応する case を追加すること。

## ルール追加方法

ユーザーが新しいルールを追加したい場合:

1. rules.yaml を Edit ツールで編集:
```yaml
- name: ルール名（英数字とアンダースコア）
  match:
    extension: [".拡張子"]    # 拡張子でマッチ
    # または
    pattern: "globパターン"   # ファイル名パターンでマッチ
  action: delete | move | move_and_rename | ask
  destination: ~/移動先パス   # move/move_and_rename時のみ
  include_dirs: true          # ディレクトリも対象にする場合
```

2. action が delete または move の場合、auto-clean.sh にも対応する case を追加する。
