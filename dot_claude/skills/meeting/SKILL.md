---
name: meeting
description: |
  毎朝の朝会（デイリーミーティング）を実施する。
  「朝会」「meeting」「今日何する」「daily」などのキーワードで発動。
---

# Daily Meeting

毎朝の朝会スキル。「やりたくないけどやるべきこと」と「やっちゃダメなこと」の振り返りサイクルを回す。

## マニュアル参照

このスキルの可変データ（アジェンダ、方針等）は外部マニュアルに格納されている。
**まず以下を Read ツールで読み込むこと:**

```
~/Documents/manuals/meeting/agenda.md
```

agenda.md の内容に従って朝会を進行する。

## 情報ソース

### GitHub Projects
```bash
gh project item-list 6 --owner @me --format json
```
ユーザーのタスク一覧を取得する。特に **Today列** のアイテムが朝会の対象。

### 前回の朝会結果（GitHub Projects 固定 Draft item）
固定の Draft item を取得して振り返りに使う。
Draft ID は agenda.md に記載されている。
```bash
gh project item-edit --id "$DRAFT_ID" --format json
```
初回や内容が空の場合はスキップしてOK。

## 進行方式

朝会はインタラクティブな対話形式で進行する。

1. **冒頭でアジェンダを提示する** — 今日話す項目の一覧を最初に見せる
2. **1ステップずつ進行する** — 各フェーズで問いかけ、ユーザーの回答を待ってから次へ進む
3. **深掘りしてから次へ進む** — 「できなかった」で終わらせず「なぜ？」「どうする？」まで掘る
4. **失敗時は具体的なアクションが出るまで次に進まない** — 「代替行動は？」「環境変えられないか？」まで掘る。「そうだよね」で流さない
5. **まとめて出力しない** — 全情報を一度に出すのは禁止。必ずターンを渡す

## その他の進行ルール

- **5分上限**。完璧なプランより「決まってる」が大事
- ユーザーが脱線したらフォーカスアンカーとして機能する
- タスクは **最大3つ** に絞る。全部やろうとしない
- 「やらない」も立派な決定として尊重する
- **Issue作成時は必ず GitHub Projects (ID:6) にも追加する**（`gh project item-add 6 --owner @me --url <issue-url>`）
- **自走している習慣はチェックから外す**（タスク化が楽しさを殺す。Etkin 2016）
- **習慣が定着したらトラッキングを卒業する**（足場は外す。Wood & Neal 2007）

## ジャーナル記録

朝会のサマリを週次ジャーナルの当日セクションに追記する。

### 場所
`~/Documents/notes/journals/journal-YYYY-WXX.md` の当日の日付セクション

### フォーマット
```markdown
### 朝会サマリ
- （3行程度のサマリ）
```

### 手順
1. `zk journal` で今週のジャーナルファイルパスを特定（なければ作成される）
2. 当日の日付セクション（`## YYYY-MM-DD (Day)`）の下に追記
3. ジャーナルのトーンに合わせる（stream-of-consciousness、スタイル編集しない）

## GitHub Projects Draft item 更新

固定の Draft item を毎日上書きする。翌日の振り返りソースになる。
Draft ID は agenda.md に記載。

### 更新方法
```bash
gh project item-edit --id "$DRAFT_ID" --title "Daily: YYYY-MM-DD" --body "$BODY" --project-id PVT_kwHOBrhoMc4BPlDr --format json
```

### Body フォーマット
```markdown
## Tasks
- [ ] タスク1 — ゴールライン
- [ ] タスク2 — ゴールライン
- [ ] タスク3 — ゴールライン

## Yesterday Review
振り返り内容
```

## 自動化移行の条件

7日間連続で手動実行できたら、自動起動（scheduled trigger 等）への移行を検討する。
この条件を満たしたとき、ユーザーに提案すること。
