---
name: make-pr-from-template
description: PRテンプレートから Issue 用の PR 説明文を作成
---
# PR 作成コマンド

PRテンプレートをコピーして、指定されたIssue用のPR説明文を作成します。

## 指示

1. `.github/pull_request_template.md` を `tmp/pr_{issue_number}.md` にコピー
2. 以下を編集:
   - 関連Issue: `Closes #{issue_number}`
   - 修正内容と理由を具体的に記載
   - テスト内容を実際の操作で記載
   - チェックボックスの適切な項目にチェック

## 使用例
```bash
# Issue #42 用のPR説明文を作成
cp .github/pull_request_template.md tmp/pr_42.md
# 編集後、内容を確認
cat tmp/pr_42.md
```
