---
name: issue-worktree
description: |
  GitHub IssueからGit worktreeとtmuxウィンドウを発行する。
  Issue番号を指定すると、ブランチ作成・worktree発行・tmuxウィンドウ作成・mise trustまで一括で行う。
  「Issue 4のworktree作って」「#7で作業開始」などで発動。
compatibility: Requires git 2.17+, gh CLI, tmux, mise
---

# Issue Worktree

GitHub IssueベースでGit worktreeとtmuxウィンドウを発行する。

## Naming Convention

- **Branch**: `feat_{number}-{description}` (main派生)
- **Worktree**: `../{repo_name}-{number}`
- **tmux window**: `{number}`

## Workflow

### Step 1: Issue情報の取得

```bash
# Issue番号から情報取得
gh issue view {NUMBER} --json number,title,labels
```

### Step 2: description生成

Issueタイトルからdescriptionを生成:
- 日本語の場合は英語に意訳（短く）
- スペースはハイフンに変換
- 小文字化
- 特殊文字は除去

例:
- 「ポジション復旧機能の実装」→ `position-recovery`
- 「Bot詳細ページの追加」→ `bot-detail-page`
- 「リスク管理モジュールの実装」→ `risk-management`

### Step 3: リポジトリ情報の取得

```bash
# リポジトリ名を取得
REPO_NAME=$(basename $(git rev-parse --show-toplevel))

# tmuxセッション名（カレントセッション）
SESSION=$(tmux display-message -p '#S')
```

### Step 4: ブランチとworktree作成

```bash
BRANCH_NAME="feat_{NUMBER}-{DESCRIPTION}"
WORKTREE_PATH="../{REPO_NAME}-{NUMBER}"

# main派生でブランチ作成
git branch "$BRANCH_NAME" main

# worktree発行
git worktree add "$WORKTREE_PATH" "$BRANCH_NAME"
```

### Step 5: tmuxウィンドウ作成

```bash
# 新しいウィンドウをworktreeディレクトリで開く
tmux new-window -t "$SESSION" -n "{NUMBER}" -c "$(realpath $WORKTREE_PATH)"
```

### Step 6: mise trust実行

```bash
# 新しいウィンドウでmise trustを実行
# IMPORTANT: 文章とEnterは必ず2回に分けて送信する
tmux send-keys -t "$SESSION:{NUMBER}" 'mise trust'
tmux send-keys -t "$SESSION:{NUMBER}" Enter
```

### Step 7: Claude起動とIssue内容の引き渡し

```bash
# Issue内容を取得
ISSUE_BODY=$(gh issue view {NUMBER} --json title,body --jq '"# Issue #{NUMBER}: " + .title + "\n\n" + .body')

# claudeを起動
tmux send-keys -t "$SESSION:{NUMBER}" 'claude'
tmux send-keys -t "$SESSION:{NUMBER}" Enter

# 少し待ってからIssue内容を送信（claudeの起動を待つ）
sleep 2
tmux send-keys -t "$SESSION:{NUMBER}" "$ISSUE_BODY"
tmux send-keys -t "$SESSION:{NUMBER}" Enter
```

## Complete Example

Issue #4「ポジション復旧機能の実装」の場合:

```bash
# 1. Issue確認
gh issue view 4 --json number,title

# 2. ブランチ・worktree作成
git branch feat_4-position-recovery main
git worktree add ../swarmyard-4 feat_4-position-recovery

# 3. tmuxウィンドウ作成
tmux new-window -t swarmyard -n 4 -c /path/to/swarmyard-4

# 4. mise trust（文章とEnterは分けて送信）
tmux send-keys -t swarmyard:4 'mise trust'
tmux send-keys -t swarmyard:4 Enter

# 5. claude起動してIssue内容を渡す
tmux send-keys -t swarmyard:4 'claude'
tmux send-keys -t swarmyard:4 Enter
sleep 2
ISSUE_BODY=$(gh issue view 4 --json title,body --jq '"# Issue #4: " + .title + "\n\n" + .body')
tmux send-keys -t swarmyard:4 "$ISSUE_BODY"
tmux send-keys -t swarmyard:4 Enter
```

## Notes

- 既にブランチやworktreeが存在する場合はエラーになる
- 削除は `git-branch-cleanup` skillを使用
- worktree一覧は `git worktree list` で確認
- **IMPORTANT**: `tmux send-keys`でclaudeに送信する際は、文章とEnterを必ず2回に分けて送信すること（1回で送ると正しく動作しない）
