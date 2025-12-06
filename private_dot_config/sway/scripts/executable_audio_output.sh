#!/bin/bash

# Get sinks: "sink_name\tDescription"
mapfile -t sinks < <(pactl list sinks | awk '
    /Name:/ { name=$2 }
    /Description:/ { sub(/.*Description: /, ""); print name "\t" $0 }
')

# Build wofi options: "Description"
options=""
for sink in "${sinks[@]}"; do
    desc="${sink#*$'\t'}"
    options+="$desc"$'\n'
done

# Show wofi
selected=$(echo -n "$options" | wofi --dmenu --prompt "Audio Output")
[[ -z "$selected" ]] && exit 0

# Find matching sink name
for sink in "${sinks[@]}"; do
    name="${sink%%$'\t'*}"
    desc="${sink#*$'\t'}"
    if [[ "$desc" == "$selected" ]]; then
        pactl set-default-sink "$name"
        notify-send "Audio Output" "Switched to: $desc" 2>/dev/null
        exit 0
    fi
done
