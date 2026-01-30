---
name: firefly-transaction
description: |
  Firefly IIIに取引を登録する。Nomad variablesからAPIトークンを取得し、
  ユーザーに登録内容（金額、日付、カテゴリ、出金元、支払先、説明）を確認してAPIを叩く。
  「家計簿」「支出登録」「Fireflyに登録」などのキーワードで発動。
compatibility: Requires nomad CLI and curl. Firefly III instance at firefly.voxon.monster.
---

# Firefly III 取引登録

Firefly IIIに取引（主にwithdrawal/支出）を登録する。

## Workflow

### Step 1: トークン取得

Nomad variablesからFirefly APIトークンを取得：

```bash
FIREFLY_TOKEN=$(nomad var get -out=json nomad/jobs/callot | jq -r '.Items.firefly_token')
```

### Step 2: ユーザーに登録内容を確認

以下の情報を聞く（AskUserQuestionツールを使用）：

| 項目 | 必須 | デフォルト | 例 |
|------|------|------------|-----|
| 金額 | Yes | - | 1075 |
| 日付 | No | 今日 | 2026-01-20 |
| 説明 | Yes | - | 昼飯 |
| 出金元 | No | SMBC | SMBC |
| 支払先 | Yes | - | セブンイレブン |
| カテゴリ | No | (なし) | 食費 |
| タイプ | No | withdrawal | withdrawal/deposit/transfer |

**ユーザーが一文で全部言ってくれた場合**（例：「1075円で食費としてセブンイレブンで昼飯、SMBCから」）は、パースして確認だけ取る。

### Step 3: 既存データの参照（オプション）

カテゴリや口座名が曖昧な場合、既存データを確認：

```bash
# カテゴリ一覧
curl -s -X GET 'https://firefly.voxon.monster/api/v1/categories' \
  -H "Authorization: Bearer $FIREFLY_TOKEN" \
  -H 'Accept: application/json' | jq '.data[] | {id: .id, name: .attributes.name}'

# 口座一覧
curl -s -X GET 'https://firefly.voxon.monster/api/v1/accounts?type=asset' \
  -H "Authorization: Bearer $FIREFLY_TOKEN" \
  -H 'Accept: application/json' | jq '.data[] | {id: .id, name: .attributes.name}'
```

### Step 4: API実行

```bash
curl -s -X POST 'https://firefly.voxon.monster/api/v1/transactions' \
  -H "Authorization: Bearer $FIREFLY_TOKEN" \
  -H 'Content-Type: application/json' \
  -H 'Accept: application/vnd.api+json' \
  -d '{
    "transactions": [{
      "type": "withdrawal",
      "date": "YYYY-MM-DD",
      "amount": "AMOUNT",
      "description": "DESCRIPTION",
      "source_name": "SOURCE_ACCOUNT",
      "destination_name": "DESTINATION",
      "category_name": "CATEGORY"
    }]
  }'
```

**注意**: category_nameが空の場合はフィールドごと省略する。

### Step 5: 結果確認

成功時のレスポンスから以下を抽出して報告：

```bash
| jq '{
  id: .data.id,
  amount: .data.attributes.transactions[0].amount,
  description: .data.attributes.transactions[0].description,
  source: .data.attributes.transactions[0].source_name,
  destination: .data.attributes.transactions[0].destination_name,
  category: .data.attributes.transactions[0].category_name,
  balance_after: .data.attributes.transactions[0].source_balance_after
}'
```

## よくあるパターン

### 支出（withdrawal）
```
「1075円、セブンイレブン、昼飯、食費」
→ type: withdrawal, amount: 1075, destination: セブンイレブン, description: 昼飯, category: 食費, source: SMBC
```

### 収入（deposit）
```
「給料25万、会社から」
→ type: deposit, amount: 250000, source_name: 会社, destination_name: SMBC, category: 給与
```

### 振替（transfer）
```
「SMBCから楽天に5万移動」
→ type: transfer, amount: 50000, source: SMBC, destination: 楽天
```

## エラーハンドリング

| エラー | 原因 | 対処 |
|--------|------|------|
| Unauthenticated | トークン無効/期限切れ | Firefly UIで新しいPAT作成、Nomad var更新 |
| source_name not found | 口座名が違う | 口座一覧を確認して正確な名前を使用 |
| Validation error | 必須フィールド不足 | amount, description, source/destinationを確認 |

## 補足

- カテゴリは存在しなければ自動作成される
- 支払先（expense account）も存在しなければ自動作成される
- 日本円（JPY）がデフォルト通貨として設定されている前提
