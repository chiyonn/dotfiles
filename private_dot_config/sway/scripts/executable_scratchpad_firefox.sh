#!/bin/bash

MARK="sp"

# 既にspマークを持つウィンドウがあれば何もしない
if swaymsg -t get_tree | jq -e ".. | select(.marks? and (.marks | contains([\"$MARK\"])))" > /dev/null 2>&1; then
  notify-send "scratchpad init" "既にscratchpadが存在します"
  exit 0
fi

# 既にFirefoxが起動していたら通知して終了
if pgrep -x firefox > /dev/null; then
  notify-send "scratchpad init" "Firefoxが既に起動しています。先にFirefoxを閉じてください。"
  exit 1
fi

# firefoxをバックグラウンドで起動
firefox --new-window &

# 新しいfirefoxウィンドウが開くのを待ってmark付けてscratchpadへ
swaymsg -t subscribe '["window"]' | while read -r event; do
  if echo "$event" | jq -e '.change == "new" and .container.app_id == "org.mozilla.firefox"' > /dev/null 2>&1; then
    con_id=$(echo "$event" | jq -r '.container.id')
    swaymsg "[con_id=$con_id] mark $MARK, floating enable, resize set 2160 2000, move position 0 920, move scratchpad"
    exit 0
  fi
done
