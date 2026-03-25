---
name: meeting
description: |
  毎朝の朝会（デイリーミーティング）を実施する。
  「朝会」「meeting」「今日何する」「daily」などのキーワードで発動。
---

# Daily Meeting

毎朝の朝会スキル。「今日何するんだっけ」状態を脱却し、意図のある一日を始める。

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
ユーザーのタスク一覧を取得する。ステータス（Todo / In Progress / Done）を確認。

### 前回の朝会結果（GitHub Projects 固定 Draft item）
固定の Draft item を取得して振り返りに使う。
Draft ID は agenda.md に記載されている。
```bash
gh project item-edit --id "$DRAFT_ID" --format json
```
初回や内容が空の場合はスキップしてOK。

## 進行ルール

- **5分上限**。完璧なプランより「決まってる」が大事
- ユーザーが脱線したらフォーカスアンカーとして機能する
- タスクは **最大3つ** に絞る。全部やろうとしない
- 「やらない」も立派な決定として尊重する

## Discord 投稿

朝会の結果を Discord webhook で投稿する。

### 投稿方法
```bash
curl -H "Content-Type: application/json" \
  -d "$PAYLOAD" \
  "$DISCORD_MEETING_WEBHOOK"
```

環境変数 `DISCORD_MEETING_WEBHOOK` は settings.local.json で設定済み。

### ペイロード構成
```json
{
  "username": "Meeting Minutes",
  "embeds": [{
    "title": "Daily Plan — YYYY-MM-DD",
    "color": 5814783,
    "fields": [
      {
        "name": "Today's Tasks",
        "value": "⬜ タスク1 — ゴールライン\n⬜ タスク2 — ゴールライン\n⬜ タスク3 — ゴールライン"
      },
      {
        "name": "Yesterday Review",
        "value": "振り返り一言"
      }
    ]
  }]
}
```

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
