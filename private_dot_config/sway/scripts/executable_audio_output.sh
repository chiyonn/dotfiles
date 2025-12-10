#!/bin/bash

# Check for connected Bluetooth devices without audio sink
check_bluetooth_sink() {
    local bt_devices
    bt_devices=$(bluetoothctl devices Connected 2>/dev/null)
    [[ -z "$bt_devices" ]] && return

    while read -r _ mac name; do
        [[ -z "$mac" ]] && continue
        local card_name="bluez_card.${mac//:/_}"

        # Check if device has a2dp-sink profile available
        if ! pactl list cards 2>/dev/null | grep -A 30 "$card_name" | grep -q "a2dp-sink\|a2dp_sink"; then
            notify-send -u critical "Bluetooth Audio" "$name: A2DPプロファイルなし\nbluetooth.service再起動で直るかも" 2>/dev/null
        fi
    done <<< "$bt_devices"
}

check_bluetooth_sink

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
