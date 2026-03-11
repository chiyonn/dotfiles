#!/bin/bash
set -e

THEME_DIR="$HOME/.config/themes"
THEME="${1:-}"

if [ -z "$THEME" ]; then
    echo "usage: theme-switch.sh <theme>"
    echo "available:"
    ls -1 "$THEME_DIR" 2>/dev/null
    exit 1
fi

if [ ! -d "$THEME_DIR/$THEME" ]; then
    echo "theme '$THEME' not found"
    echo "available:"
    ls -1 "$THEME_DIR" 2>/dev/null
    exit 1
fi

SRC="$THEME_DIR/$THEME"

# waybar
cp "$SRC/waybar-config" "$HOME/.config/waybar/config"
cp "$SRC/waybar-style.css" "$HOME/.config/waybar/style.css"

# swaync
cp "$SRC/swaync-config.json" "$HOME/.config/swaync/config.json"
cp "$SRC/swaync-style.css" "$HOME/.config/swaync/style.css"

# wofi
cp "$SRC/wofi-style.css" "$HOME/.config/wofi/style.css"

# swaylock
cp "$SRC/swaylock" "$HOME/.config/swaylock/config"

# sway colors
cp "$SRC/sway-theme" "$HOME/.config/sway/config.d/theme"

# foot colors
{
    echo "[colors]"
    cat "$SRC/foot-colors"
} > /tmp/foot-colors-new
# replace [colors] section in foot.ini
sed -i '/^\[colors\]/,$d' "$HOME/.config/foot/foot.ini"
cat /tmp/foot-colors-new >> "$HOME/.config/foot/foot.ini"
rm -f /tmp/foot-colors-new

# reload
pkill waybar 2>/dev/null; sleep 0.2; waybar &disown
pkill swaync 2>/dev/null; sleep 0.2; swaync &disown
swaymsg reload 2>/dev/null

echo "switched to: $THEME"
