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

### Step 5.5: workerから通信フォルダへのシンボリックリンク作成

```bash
# workerは相対パス .claude/workers/ を使うので、メインリポジトリへリンク
mkdir -p "$WORKTREE_PATH/.claude"
ln -s "$PROJECT_ROOT/.claude/workers" "$WORKTREE_PATH/.claude/workers"
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
# claudeを起動
tmux send-keys -t "$SESSION:{NUMBER}" 'claude'
tmux send-keys -t "$SESSION:{NUMBER}" Enter

# 少し待ってからIssue内容を送信（claudeの起動を待つ）
sleep 2

# Issue内容 + Worker Protocolを送信
tmux send-keys -t "$SESSION:{NUMBER}" "$ISSUE_WITH_PROTOCOL"
tmux send-keys -t "$SESSION:{NUMBER}" Enter
```

**送信する内容 ($ISSUE_WITH_PROTOCOL):**

```markdown
# Issue #{NUMBER}: {TITLE}

{ISSUE_BODY}

---

## Worker Protocol

あなたは自律的に動作するWorkerです。実装からレビュー、修正まで自己完結してください。

### 進捗報告
作業の節目で `.claude/workers/{NUMBER}/status.md` を更新してください:

- status: `in_progress` | `in_review` | `completed`
- summary: 現在何をしているか1行で
- Progress: チェックリスト形式で進捗を記録
- Blockers: 自力で解決できない問題があれば記載

### 実装フロー

1. Issue内容を確認し、status を `in_progress` に更新
2. 実装を進める（テストも書く）
3. 実装完了したらコミット
4. レビューフローへ

### レビューフロー

実装が完了したら、**Taskツール**を使ってレビューエージェントを起動し、フィードバックを受けてください。

1. status を `in_review` に更新
2. Taskツールでレビューエージェントを起動:

```
Task tool parameters:
- subagent_type: "general-purpose"
- description: "Review Issue #{NUMBER} changes"
- prompt: 以下の内容を渡す
```

**レビューエージェントへのプロンプト:**

~~~
# Code Review Request

Issue #{NUMBER}: {TITLE}

## Issue要件
{ISSUE_BODYの要約}

## レビュー対象
`git diff main..HEAD` の内容をレビューしてください。

## レビュー観点

### Must Check
- [ ] Issue要件がすべて実装されているか
- [ ] スコープクリープ（要求されていない機能の追加）がないか
- [ ] エラーハンドリングは適切か
- [ ] テストは追加されているか

### Code Quality
- [ ] 命名は意図を正確に表しているか
- [ ] 関数の責務は単一か
- [ ] マジックナンバー/ストリングがないか
- [ ] 不要なコードが残っていないか

### Security
- [ ] ユーザー入力のバリデーション
- [ ] 機密情報がログに出力されていないか

### Architecture
- [ ] プロジェクトの既存パターンに従っているか
- [ ] YAGNI/KISS原則に反していないか

## 出力形式

```markdown
## Summary
[1-2文で全体評価]

## Must Fix
- [ ] [修正必須の問題]

## Should Fix
- [ ] [推奨される修正]

## Verdict
[ ] Approved - マージ可能
[ ] Request Changes - 修正が必要
```
~~~

3. レビュー結果を受け取る
4. **Request Changes** の場合:
   - 指摘事項を修正
   - 再コミット
   - 再度レビューエージェントを起動（ループ）
5. **Approved** の場合:
   - status を `completed` に更新
   - 作業完了

### ブロック時

自力で解決できない問題が発生したら:
1. status.md の Blockers セクションに詳細を記載
2. 可能な範囲で調査を続ける
3. どうしても無理なら作業を中断（Orchestratorが後で確認する）
```

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

# 6. claude起動してIssue内容 + Worker Protocolを渡す
tmux send-keys -t swarmyard:4 'claude'
tmux send-keys -t swarmyard:4 Enter
sleep 2
tmux send-keys -t swarmyard:4 "$ISSUE_WITH_PROTOCOL"
tmux send-keys -t swarmyard:4 Enter
```

## Notes

- 既にブランチやworktreeが存在する場合はエラーになる
- 削除は `git-branch-cleanup` skillを使用
- worktree一覧は `git worktree list` で確認
- **IMPORTANT**: `tmux send-keys`でclaudeに送信する際は、文章とEnterを必ず2回に分けて送信すること（1回で送ると正しく動作しない）
- 通信フォルダは `.claude/workers/{NUMBER}/` に作成される（.gitignore推奨）
