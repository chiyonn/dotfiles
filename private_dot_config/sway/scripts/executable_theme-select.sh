#!/bin/bash

THEME_DIR="$HOME/.config/themes"
CURRENT=$(cat "$THEME_DIR/.current" 2>/dev/null)

# List themes, mark current
options=""
for dir in "$THEME_DIR"/*/; do
    name=$(basename "$dir")
    if [[ "$name" == "$CURRENT" ]]; then
        options+="$name ●"$'\n'
    else
        options+="$name"$'\n'
    fi
done

selected=$(echo -n "$options" | wofi --dmenu --prompt "Theme")
[[ -z "$selected" ]] && exit 0

# Strip marker
theme="${selected%% *}"

if [[ "$theme" == "$CURRENT" ]]; then
    notify-send "Theme" "Already active: $theme"
    exit 0
fi

if "$HOME/.config/sway/scripts/theme-switch.sh" "$theme"; then
    notify-send "Theme" "Switched to: $theme"
else
    notify-send -u critical "Theme" "Failed to switch: $theme"
fi
