# Common aliases for both macOS and Linux

# macOS-specific ls aliases
alias ls='ls -G'
alias ll='ls -lG'
alias la='ls -laG'

# Git aliases
alias gb='git branch'
alias gl='git log'
alias gll='git log --oneline'
alias gs='git status'
alias ga='git add'
alias gc='git commit -m'
alias gp='git push'
alias gd='git diff'

# Editor aliases
alias v=nvim

# Tmux aliases
alias t=tmux
alias tnew='tmux new-session -s'
alias attach='tmux attach -t'

# Python environment
alias activate='source ./.venv/bin/activate'
