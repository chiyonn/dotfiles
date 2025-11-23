#!/bin/bash

SESSION_NAME="${1:-home}"

if tmux has-session -t "$SESSION_NAME" 2>/dev/null; then
  tmux attach -t "$SESSION_NAME"
  exit 0
fi

# セッションをデタッチ状態で新規作成
tmux new-session -d -s "$SESSION_NAME"

# 左右分割（初期ペインは0）
tmux split-window -h -t "$SESSION_NAME:0.0"

# 右ペイン（1）を選択
tmux select-pane -t "$SESSION_NAME:0.1"

# nvim 実行
tmux send-keys -t "$SESSION_NAME:0.1" 'nvim' C-m

# 右ペインを上下に分割（nvimの下にhtop用のペインを作る）
tmux split-window -v -t "$SESSION_NAME:0.1"

# htop 実行（新しくできたペインは自動的にアクティブ＝ペイン2）
tmux send-keys -t "$SESSION_NAME:0.2" 'htop' C-m

# 左ペイン（0）を選択
tmux select-pane -t "$SESSION_NAME:0.0"

# ウィンドウ名を変更（任意）
tmux rename-window -t "$SESSION_NAME:0" "dashboard"

# アタッチ
tmux attach -t "$SESSION_NAME"
