#!/bin/bash
# Claude Code statusline - reads theme from ~/.config/nvim/theme to match current desktop theme

INPUT=$(cat)

MODEL=$(echo "$INPUT" | jq -r '.model.display_name // "?"')
CTX=$(echo "$INPUT" | jq -r '.context_window.used_percentage // 0' | cut -d. -f1)
COST=$(echo "$INPUT" | jq -r '.cost.total_cost_usd // 0')

# detect theme
THEME_FILE="$HOME/.config/themes/.current"
CURRENT_THEME=$(cat "$THEME_FILE" 2>/dev/null || echo "default")

# rose gold palette (neogal)
if [[ "$CURRENT_THEME" == "neogal" ]]; then
    C_ACCENT='\033[38;2;232;164;184m'  # rose pink
    C_GOLD='\033[38;2;212;165;116m'    # warm gold
    C_DIM='\033[38;2;92;26;48m'        # wine
    C_TEXT='\033[38;2;200;100;140m'     # medium rose
    C_WARN='\033[38;2;234;157;52m'     # amber
    C_CRIT='\033[38;2;180;99;122m'     # deep rose
    SEP='♡'
else
    # fallback: minimal
    C_ACCENT='\033[36m'
    C_GOLD='\033[33m'
    C_DIM='\033[90m'
    C_TEXT='\033[37m'
    C_WARN='\033[33m'
    C_CRIT='\033[31m'
    SEP='│'
fi
RST='\033[0m'

# context color based on usage
if (( CTX > 85 )); then
    C_CTX="$C_CRIT"
elif (( CTX > 60 )); then
    C_CTX="$C_WARN"
else
    C_CTX="$C_GOLD"
fi

# context bar (10 chars)
FILLED=$(( CTX / 10 ))
EMPTY=$(( 10 - FILLED ))
BAR=""
for ((i=0; i<FILLED; i++)); do BAR+="▓"; done
for ((i=0; i<EMPTY; i++)); do BAR+="░"; done

printf '%b' \
    "${C_ACCENT}${SEP}${RST} " \
    "${C_TEXT}${MODEL}${RST} " \
    "${C_DIM}${SEP}${RST} " \
    "${C_CTX}${BAR} ${CTX}%%${RST} " \
    "${C_DIM}${SEP}${RST} " \
    "${C_GOLD}\$${COST}${RST}" \
    " ${C_ACCENT}${SEP}${RST}"
