# Common aliases for both macOS and Linux

# ls aliases (cross-platform)
if [[ "$(uname)" == "Darwin" ]]; then
  alias ls='ls -G'
  alias ll='ls -lG'
  alias la='ls -laG'
else
  alias ls='ls --color=auto'
  alias ll='ls -l --color=auto'
  alias la='ls -la --color=auto'
fi

# Git aliases
alias gb='git branch'
alias gl='git log'
alias gll='git log --oneline'
alias gs='git status'
alias ga='git add'
alias gc='git commit -m'
alias gp='git push'
alias gd='git diff'

# Rails aliases
alias precom='bin/rails assets:precompile'

# App aliases
alias v=nvim
alias cz=chezmoi
alias gocz='cd ~/.local/share/chezmoi'
alias edit='chezmoi managed | peco | xargs -I {} chezmoi edit --apply "{}"'


# Tmux aliases
alias t=tmux
alias tnew='tmux new-session -s'
alias attach='tmux attach -t'

# Python environment
alias activate='source ./.venv/bin/activate'

alias tile='aerospace layout tiles'

alias qbuild='NOMAD_TOKEN="$(vault kv get -field=admin-token secret/nomad/tokens)" && curl -X POST $NOMAD_ADDR/v1/job/quartz-builder/dispatch -H "X-Nomad-Token: $NOMAD_TOKEN" -d "{}"'

# System aliases
alias reboot='systemctl soft-reboot'
