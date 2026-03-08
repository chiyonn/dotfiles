---
name: mercari-manage
description: |
  メルカリの出品管理（出品・削除）を自動化する。
  「メルカリ掃除」「mercari cleanup」「出品削除」「メルカリ整理」「メルカリ出品」などのキーワードで発動。
---

# メルカリ出品管理

## スクリプト一覧

| スクリプト | 用途 |
|-----------|------|
| `mercari-listing.py` | CSVから商品を自動出品 |
| `mercari-cleanup.py` | 古い出品を自動削除 |
| `fetch-images.py` | 既存出品から商品画像を収集 |

## 共通の前提条件

### ブラウザ起動とログイン

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

## 出品 (mercari-listing.py)

```bash
python3 -u ~/.claude/skills/mercari-manage/mercari-listing.py
```

- Google SheetsのCSVから在庫情報を取得
- 在庫 > 0 かつ必須フィールドが揃った商品を自動出品
- 画像は `~/.claude/skills/mercari-manage/assets/{ASIN}/` から取得

## 削除 (mercari-cleanup.py)

```bash
python3 -u ~/.claude/skills/mercari-manage/mercari-cleanup.py
```

- 出品一覧ページで「もっと見る」を繰り返しクリックして全件読み込み
- 更新日が14日以上前 or 「か月」表記の商品を自動削除

## 画像収集 (fetch-images.py)

```bash
python3 -u ~/.claude/skills/mercari-manage/fetch-images.py
```

- 既存出品の商品画像をダウンロードして `assets/{ASIN}/` に保存

## 重要な技術的注意

- **`eval` コマンドは使わない** — `page.evaluate()` にマッピングされるため Playwright API が動かない。しかも exit code 0 を返すのでエラー検出も困難
- すべて `snapshot` → ref ID → `click`/`fill`/`select`/`upload` コマンドで操作する
- `run_cli` の成否判定は exit code + 出力の `### Error` チェックの両方で行う

## ブラウザを閉じる

```bash
npx @playwright/cli close
```
