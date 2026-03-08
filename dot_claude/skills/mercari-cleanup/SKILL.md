---
name: mercari-cleanup
description: |
  メルカリの古い出品を一括削除する。
  「メルカリ掃除」「mercari cleanup」「出品削除」「メルカリ整理」などのキーワードで発動。
---

# メルカリ出品クリーンアップ

更新日が2週間以上前の出品商品を自動削除する。

## 実行手順

### Step 1: ブラウザ起動とログイン

```bash
npx @playwright/cli open https://jp.mercari.com/ --browser firefox --headed
npx @playwright/cli state-load mercari
npx @playwright/cli reload
```

スナップショットを取得し、ログイン済みか確認する（ナビに「chiyonn」が表示されていればOK）。

ログインできていない場合（state期限切れなど）:
1. Firefoxのcookies.sqliteからメルカリのcookieを抽出して注入する
2. 注入後リロードしてログイン確認
3. `npx @playwright/cli state-save mercari` で状態を更新保存

### Step 2: 削除スクリプト実行

```bash
python3 ~/.claude/skills/mercari-cleanup/mercari-cleanup.py
```

スクリプトが以下を自動実行する:
- 出品一覧ページ（/mypage/listings）を開く
- 更新日が14日以上前 or 「か月」表記の商品IDを収集
- 各商品の編集ページで「この商品を削除する」→確認ダイアログ「削除する」を実行

### Step 3: 結果報告

スクリプトの出力をユーザーに報告する。削除件数と失敗件数を伝える。

### Step 4: ブラウザを閉じる

```bash
npx @playwright/cli close
```
