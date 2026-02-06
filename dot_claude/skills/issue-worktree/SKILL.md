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

# プロジェクトルート
PROJECT_ROOT=$(git rev-parse --show-toplevel)

# tmuxセッション名（カレントセッション）
SESSION=$(tmux display-message -p '#S')

# Orchestratorのウィンドウ名（現在のウィンドウ）
ORCH_WINDOW=$(tmux display-message -p '#W')
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

### Step 5: 通信フォルダ初期化

```bash
# プロジェクトルートに .claude/workers/{NUMBER}/ を作成
mkdir -p "$PROJECT_ROOT/.claude/workers/{NUMBER}"

# status.md初期化
cat > "$PROJECT_ROOT/.claude/workers/{NUMBER}/status.md" << 'EOF'
# Worker Status: Issue #{NUMBER}

status: initializing
started_at: {TIMESTAMP}
updated_at: {TIMESTAMP}
summary: 起動中

## Progress
- [ ] Issue内容の確認
- [ ] 実装

## Blockers
なし

## Notes
EOF
```

### Step 5.5: workerから通信フォルダ・設定へのシンボリックリンク作成

```bash
# workerは相対パス .claude/workers/ を使うので、メインリポジトリへリンク
mkdir -p "$WORKTREE_PATH/.claude"
ln -s "$PROJECT_ROOT/.claude/workers" "$WORKTREE_PATH/.claude/workers"

# settings.local.json をシンボリックリンク（許可設定を継承）
# 既存ファイルがあれば削除してからリンク
rm -f "$WORKTREE_PATH/.claude/settings.local.json"
ln -s "$PROJECT_ROOT/.claude/settings.local.json" "$WORKTREE_PATH/.claude/settings.local.json"
```

### Step 6: tmuxウィンドウ作成

```bash
# 新しいウィンドウをworktreeディレクトリで開く
tmux new-window -t "$SESSION" -n "{NUMBER}" -c "$(realpath $WORKTREE_PATH)"
```

### Step 7: mise trust実行

```bash
# 新しいウィンドウでmise trustを実行
# IMPORTANT: 文章とEnterは必ず2回に分けて送信する
tmux send-keys -t "$SESSION:{NUMBER}" 'mise trust'
tmux send-keys -t "$SESSION:{NUMBER}" Enter
```

### Step 8: Claude起動とIssue内容 + Worker Protocol送信

```bash
# claudeを起動（--allowedToolsで開発系コマンドを許可）
ALLOWED_TOOLS='Edit Write "Bash(git:*)" "Bash(make:*)" "Bash(go:*)" "Bash(golangci-lint:*)" "Bash(yarn:*)" "Bash(docker:*)" "Bash(docker-compose:*)" "Bash(gh:*)"'
tmux send-keys -t "$SESSION:{NUMBER}" "claude --allowedTools $ALLOWED_TOOLS"
tmux send-keys -t "$SESSION:{NUMBER}" Enter

# 少し待ってからセキュリティガイド同意を処理（初回起動時のみ表示されるが、空振りしても問題ない）
sleep 2
tmux send-keys -t "$SESSION:{NUMBER}" Enter

# さらに少し待ってからIssue内容を送信
sleep 1

# Issue内容 + Worker Protocolを送信
# Worker Protocolは外部ファイルから読み込む
SKILL_DIR="$HOME/.claude/skills/issue-worktree"
WORKER_PROTOCOL=$(cat "$SKILL_DIR/worker-protocol.md")

ISSUE_WITH_PROTOCOL="# Issue #${NUMBER}: ${TITLE}

${ISSUE_BODY}

---

${WORKER_PROTOCOL}"

tmux send-keys -t "$SESSION:{NUMBER}" "$ISSUE_WITH_PROTOCOL"
tmux send-keys -t "$SESSION:{NUMBER}" Enter
```

**Worker Protocol:** `worker-protocol.md` を参照（再利用可能）

## Complete Example

Issue #4「ポジション復旧機能の実装」の場合:

```bash
# 1. Issue確認
gh issue view 4 --json number,title

# 2. ブランチ・worktree作成
git branch feat_4-position-recovery main
git worktree add ../swarmyard-4 feat_4-position-recovery

# 3. 通信フォルダ初期化
mkdir -p .claude/workers/4
echo "# Worker Status: Issue #4" > .claude/workers/4/status.md

# 4. tmuxウィンドウ作成
tmux new-window -t swarmyard -n 4 -c /path/to/swarmyard-4

# 5. mise trust（文章とEnterは分けて送信）
tmux send-keys -t swarmyard:4 'mise trust'
tmux send-keys -t swarmyard:4 Enter

# 6. claude起動してIssue内容 + Worker Protocolを渡す（--allowedToolsで開発系コマンド許可）
ALLOWED_TOOLS='Edit Write "Bash(git:*)" "Bash(make:*)" "Bash(go:*)" "Bash(golangci-lint:*)" "Bash(yarn:*)" "Bash(docker:*)" "Bash(docker-compose:*)" "Bash(gh:*)"'
tmux send-keys -t swarmyard:4 "claude --allowedTools $ALLOWED_TOOLS"
tmux send-keys -t swarmyard:4 Enter
sleep 2
tmux send-keys -t swarmyard:4 Enter  # セキュリティガイド同意（空振りOK）
sleep 1
tmux send-keys -t swarmyard:4 "$ISSUE_WITH_PROTOCOL"
tmux send-keys -t swarmyard:4 Enter
```

## Error Handling

### Issue番号が存在しない場合
```bash
# gh issue viewが失敗した場合
if ! gh issue view {NUMBER} --json number,title 2>/dev/null; then
  echo "Error: Issue #{NUMBER} が見つかりません"
  exit 1
fi
```

### ブランチが既に存在する場合
```bash
# ブランチの存在チェック
if git rev-parse --verify "feat_{NUMBER}-{DESCRIPTION}" 2>/dev/null; then
  echo "Error: ブランチ feat_{NUMBER}-{DESCRIPTION} は既に存在します"
  echo "削除するには: git branch -D feat_{NUMBER}-{DESCRIPTION}"
  exit 1
fi
```

### worktreeが既に存在する場合
```bash
# worktreeの存在チェック
WORKTREE_PATH="../{REPO_NAME}-{NUMBER}"
if [ -d "$WORKTREE_PATH" ]; then
  echo "Error: worktree $WORKTREE_PATH は既に存在します"
  echo "削除するには: git worktree remove $WORKTREE_PATH"
  exit 1
fi
```

**推奨**: 上記エラーが発生した場合は、`/issue-finish {NUMBER}` または `/git-branch-cleanup` で既存リソースをクリーンアップしてから再実行。

## Notes

- **IMPORTANT**: `tmux send-keys`でclaudeに送信する際は、文章とEnterを必ず2回に分けて送信すること（1回で送ると正しく動作しない）
- 通信フォルダは `.claude/workers/{NUMBER}/` に作成される（.gitignore推奨）
- worktree一覧は `git worktree list` で確認
- Worker Protocolは `worker-protocol.md` に外部ファイル化されており、再利用可能
