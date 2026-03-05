---
name: organize
description: |
  Use when ~/Downloads has files to clean up.
  「整理」「Downloads片付けて」「organize」「ダウンロード整理」などのキーワードで発動。
---

# Downloads Organizer

~/Downloads を常に空に保つためのスキル。

## 実行手順

### Step 1: ルールの読み込み

このスキルと同じディレクトリにある `rules.yaml` を Read ツールで読み込む。
パス: `~/.claude/skills/organize/rules.yaml`

### Step 2: ファイル一覧の取得

```bash
ls -la ~/Downloads/
```

隠しファイル（.で始まるもの）と `docs/` ディレクトリは除外する。

### Step 3: ルール評価

各ファイル/ディレクトリに対して、rules.yaml のルールを**上から順に**評価する。
最初にマッチしたルールを適用する。

**マッチング条件:**
- `extension`: ファイルの拡張子がリスト内のいずれかに一致
- `pattern`: ファイル名がglobパターンに一致（`*`はワイルドカード、`{a,b}`はOR）
- `include_dirs: true` の場合、ディレクトリもマッチ対象

### Step 4: アクション実行

#### action: delete
```bash
rm "ファイルパス"           # ファイルの場合
rm -rf "ディレクトリパス"    # ディレクトリの場合
```
確認なしで即座に削除する。

#### action: move
```bash
mkdir -p "移動先ディレクトリ"
mv "ファイルパス" "移動先ディレクトリ/"
```
移動先が存在しなければ自動作成。

#### action: move_and_rename
1. ファイル名からメタデータを推測する
   - mp3の場合: ファイル名からアーティスト名と曲名を推測
   - `ytmp3free.cc_` や `-youtubemp3free.org` などのゴミを除去
   - ハイフン区切りをスペースに、各単語をタイトルケースに
2. 推測結果をユーザーに AskUserQuestion で確認
   - 例: 「`ytmp3free.cc_waves-youtubemp3free.org.mp3` → `Guthrie Govan - Waves.mp3` でOK？」
   - ユーザーが修正した場合はその名前を使う
3. リネーム+移動を実行
```bash
mkdir -p "移動先ディレクトリ"
mv "元ファイルパス" "移動先ディレクトリ/リネーム後ファイル名"
```

#### action: ask
AskUserQuestion でユーザーに質問する。選択肢:
- **移動**: 移動先パスを指定してもらう
- **削除**: rm する
- **放置**: 何もしない（今回はスキップ）

### Step 5: 未マッチファイルの処理

`unmatched_policy: ask` の場合、どのルールにもマッチしなかったファイルに対して
Step 4 の `action: ask` と同じ処理を行う。

### Step 6: サマリー表示

処理完了後、結果をまとめて表示する:

```
## 整理結果

| アクション | ファイル | 詳細 |
|-----------|---------|------|
| 削除 | tasmate-prod-xxx.dump | ルール: delete_tasmate_dumps |
| 移動 | screenshot.png → ~/Pictures/ | ルール: images_to_pictures |
| リネーム+移動 | ytmp3... → Guthrie Govan - Waves.mp3 | ルール: mp3_to_reaper_reference |
| スキップ | something.pdf | ユーザー判断: 放置 |

削除: N件 / 移動: N件 / スキップ: N件 / 残り: N件
```

### Step 7: ルール学習の提案

Step 4-5 で ask した結果、パターンが見えた場合（例: .pdf は全部削除した等）、
rules.yaml への新規ルール追加を提案する。

提案例:
> 「.pdfファイルを全部削除したね。今後も .pdf は自動削除するルールを追加する？」

ユーザーが承認したら、rules.yaml に新しいルールを追記する。

## ルール追加方法

ユーザーが新しいルールを追加したい場合、rules.yaml を Edit ツールで編集する。
ルールの書き方:

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
