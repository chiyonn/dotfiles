---
name: mercari-manage
description: |
  メルカリの出品管理（出品・削除）を自動化する。
  「メルカリ掃除」「mercari cleanup」「出品削除」「メルカリ整理」「メルカリ出品」などのキーワードで発動。
---

# メルカリ出品管理

## スクリプト構成

| ファイル | 役割 |
|----------|------|
| `base.py` | `PlaywrightClient` — CLI操作の共通基盤 |
| `mercari-listing.py` | `MercariLister` — CSVから商品を自動出品 |
| `mercari-cleanup.py` | `MercariCleaner` — 古い出品を自動削除 |

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

## 重要な技術的注意

- **`eval` コマンドは使わない** — `page.evaluate()` にマッピングされるため Playwright API が動かない。しかも exit code 0 を返すのでエラー検出も困難
- すべて `snapshot` → ref ID → `click`/`fill`/`select`/`upload` コマンドで操作する
- `PlaywrightClient.run()` の成否判定は exit code + 出力の `### Error` チェックの両方で行う

## ブラウザを閉じる

```bash
npx @playwright/cli close
```
