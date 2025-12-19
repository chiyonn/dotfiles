#!/bin/bash

# Get paired devices: "MAC Name"
mapfile -t devices < <(bluetoothctl devices Paired | sed 's/^Device //')

if [[ ${#devices[@]} -eq 0 ]]; then
    notify-send "Bluetooth" "No paired devices found" 2>/dev/null
    exit 0
fi

# Select action
action=$(printf "connect\ndisconnect" | wofi --dmenu --prompt "Action")
[[ -z "$action" ]] && exit 0

# Build wofi options: "Name (MAC)"
options=""
for device in "${devices[@]}"; do
    mac="${device%% *}"
    name="${device#* }"
    options+="$name ($mac)"$'\n'
done

# Show wofi
selected=$(echo -n "$options" | wofi --dmenu --prompt "$action")
[[ -z "$selected" ]] && exit 0

# Extract MAC from selection
mac=$(echo "$selected" | grep -oE '[0-9A-F:]{17}')

if [[ "$action" == "connect" ]]; then
    bluetoothctl connect "$mac"

    # Wait for bluez card to appear, then set A2DP profile
    card_name="bluez_card.${mac//:/_}"
    for i in {1..10}; do
        if pactl list cards short | grep -q "$card_name"; then
            pactl set-card-profile "$card_name" a2dp-sink 2>/dev/null
            break
        fi
        sleep 0.5
    done
else
    bluetoothctl disconnect "$mac"
fi

notify-send "Bluetooth" "$action: $selected" 2>/dev/null
