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
else
    bluetoothctl disconnect "$mac"
fi

notify-send "Bluetooth" "$action: $selected" 2>/dev/null
