#!/bin/bash

URL="${1:-https://open.spotify.com}"
MARK="sp"

# firefoxをバックグラウンドで起動
firefox --new-window "$URL" &

# 新しいfirefoxウィンドウが開くのを待ってmark付けてscratchpadへ
swaymsg -t subscribe '["window"]' | while read -r event; do
  if echo "$event" | jq -e '.change == "new" and .container.app_id == "org.mozilla.firefox"' > /dev/null 2>&1; then
    con_id=$(echo "$event" | jq -r '.container.id')
    swaymsg "[con_id=$con_id] mark $MARK, floating enable, resize set 2160 2000, move position 0 920, move scratchpad"
    exit 0
  fi
done
