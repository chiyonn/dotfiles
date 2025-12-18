#!/bin/bash

# Check for connected Bluetooth audio devices without a2dp-sink
check_bluetooth_sink() {
    local cards
    cards=$(pactl list cards 2>/dev/null)
    [[ -z "$cards" ]] && return

    # Extract bluez card names (only audio devices appear here)
    local bluez_cards
    bluez_cards=$(echo "$cards" | grep -oE 'bluez_card\.[0-9A-F_]+')
    [[ -z "$bluez_cards" ]] && return

    while read -r card_name; do
        [[ -z "$card_name" ]] && continue

        # Check if device has a2dp-sink profile available
        if ! echo "$cards" | grep -A 30 "$card_name" | grep -q "a2dp-sink\|a2dp_sink"; then
            local device_name
            device_name=$(echo "$cards" | grep -A 15 "$card_name" | grep "device.description" | sed 's/.*= "\(.*\)"/\1/')
            [[ -z "$device_name" ]] && device_name="$card_name"
            notify-send -u critical "Bluetooth Audio" "$device_name: No A2DP profile\nTry restarting bluetooth.service" 2>/dev/null
        fi
    done <<< "$bluez_cards"
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
