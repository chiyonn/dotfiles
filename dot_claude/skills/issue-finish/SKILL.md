---
name: issue-finish
description: |
  Issue作業完了後のクリーンアップを行う。
  mainへのマージ、worktree削除、ブランチ削除、Issueクローズを一括実行。
  「Issue 19終わった」「#7をマージして片付けて」などで発動。
compatibility: Requires git 2.17+, gh CLI
---

# Issue Finish

Issue作業完了後のクリーンアップを自動化する。`issue-worktree` の逆操作。

## What It Does

1. ブランチをmainにマージ
2. リモート(origin/main)にpush
3. worktree削除
4. ブランチ削除
5. 通信フォルダ削除
6. Issueクローズ

## Naming Convention (issue-worktreeと同じ)

- **Branch**: `feat_{number}-{description}`
- **Worktree**: `../{repo_name}-{number}`
- **通信フォルダ**: `.claude/workers/{number}/`

## Workflow

### Step 1: 状態確認

```bash
# worktree一覧を確認
git worktree list

# ブランチの差分を確認
git log main..feat_{NUMBER}-{DESCRIPTION} --oneline
```

### Step 2: mainにマージ

```bash
# mainブランチにいることを確認
git checkout main

# マージ実行
git merge feat_{NUMBER}-{DESCRIPTION} --no-edit
```

**コンフリクトが発生した場合:**
1. コンフリクト内容を確認 (`git diff --check`)
2. 適切に解決
3. `git add` して `git commit`

### Step 3: リモートにpush

```bash
git push origin main
```

### Step 4: worktree削除

```bash
REPO_NAME=$(basename $(git rev-parse --show-toplevel))
git worktree remove ../{REPO_NAME}-{NUMBER}
```

### Step 5: ブランチ削除

```bash
git branch -d feat_{NUMBER}-{DESCRIPTION}
```

### Step 6: 通信フォルダ削除

```bash
# 通信フォルダが存在すれば削除
rm -rf .claude/workers/{NUMBER}
```

### Step 7: Issueクローズ

```bash
gh issue close {NUMBER} --reason completed
```

## Complete Example

Issue #19「DBマイグレーション自動化」の場合:

```bash
# 1. 状態確認
git worktree list
git log main..feat_19-db-migration-automation --oneline

# 2. マージ
git checkout main
git merge feat_19-db-migration-automation --no-edit

# 3. push
git push origin main

# 4. worktree削除
git worktree remove ../swarmyard-19

# 5. ブランチ削除
git branch -d feat_19-db-migration-automation

# 6. 通信フォルダ削除
rm -rf .claude/workers/19

# 7. Issueクローズ
gh issue close 19 --reason completed
```

## Error Handling

### ブランチが存在しない場合
```bash
# ブランチの存在チェック
BRANCH_NAME="feat_{NUMBER}-{DESCRIPTION}"
if ! git rev-parse --verify "$BRANCH_NAME" 2>/dev/null; then
  echo "Warning: ブランチ $BRANCH_NAME が見つかりません（既に削除済み？）"
  echo "スキップして続行します..."
fi
```

### worktreeが存在しない場合
```bash
# worktreeの存在チェック
WORKTREE_PATH="../{REPO_NAME}-{NUMBER}"
if ! git worktree list | grep -q "$WORKTREE_PATH"; then
  echo "Warning: worktree $WORKTREE_PATH が見つかりません（既に削除済み？）"
  echo "スキップして続行します..."
fi
```

### マージコンフリクトの解決手順

```bash
# コンフリクトが発生した場合
git merge feat_{NUMBER}-{DESCRIPTION} --no-edit
# -> CONFLICT (content): Merge conflict in ...

# 1. コンフリクトファイルの確認
git status

# 2. エディタでコンフリクトマーカーを解決
# <<<<<<< HEAD
# =======
# >>>>>>> feat_{NUMBER}-{DESCRIPTION}

# 3. 解決後、ファイルをステージング
git add <resolved-files>

# 4. マージコミット作成
git commit --no-edit
# または手動メッセージ: git commit -m "Merge feat_{NUMBER}-{DESCRIPTION}"

# 5. マージが成功したことを確認
git log --oneline -1
```

**重要**: コンフリクト解決時は、どちらの変更を採用するか慎重に判断すること。不明な場合はIssueの担当者に確認。

### Issueが既にクローズ済みの場合
```bash
# エラーは無視してOK
gh issue close {NUMBER} --reason completed 2>&1 | grep -v "already closed" || true
```

## Notes

- マージ前にmainブランチにいることを確認する
- worktreeやブランチが存在しない場合は警告を出してスキップ
- 通信フォルダが存在しない場合も自動的にスキップされる
- 部分的な実行も可能（例: pushだけ、Issueクローズだけ）
