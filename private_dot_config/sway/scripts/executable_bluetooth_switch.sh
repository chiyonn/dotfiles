#!/bin/bash

# ===== Device info: [ID]="MAC|Category|Display Name" =====
declare -A DEVICES=(
  [hp]="88:C9:E8:78:3B:4B|audio|WH-1000XM5"
  [gh]="D8:6C:63:4D:B2:2A|audio|GoogleHome"
  [ep]="F4:9D:8A:01:6D:CE|audio|soundcore Liberty 4 NC"
  [mc]="D7:D2:DE:B5:12:DE|input|MX Master 3S"
  [kb]="C4:C1:63:09:AA:4A|input|HHKB-Hybrid_1"
)

# ===== Select action =====
action=$(printf "connect\ndisconnect" | wofi --dmenu --prompt "Action:")
[[ -z "$action" ]] && exit 0

# ===== Show device options =====
device_options=()
for key in "${!DEVICES[@]}"; do
  IFS='|' read -r _ _ name <<< "${DEVICES[$key]}"
  device_options+=("$key $name")
done

choice=$(printf "%s\n" "${device_options[@]}" | wofi --dmenu --prompt "$action device:")
[[ -z "$choice" ]] && exit 0

device_id="${choice%% *}"
device_info="${DEVICES[$device_id]}"

# ===== Split selected device info =====
IFS='|' read -r TARGET_MAC CATEGORY DEVICE_NAME <<< "$device_info"

# ===== Disconnect other devices in the same category (only for connect) =====
if [[ "$action" == "connect" ]]; then
  for key in "${!DEVICES[@]}"; do
    IFS='|' read -r mac cat _ <<< "${DEVICES[$key]}"
    [[ "$cat" == "$CATEGORY" && "$mac" != "$TARGET_MAC" ]] && bluetoothctl disconnect "$mac" >/dev/null
  done
  bluetoothctl connect "$TARGET_MAC"
else
  bluetoothctl disconnect "$TARGET_MAC"
fi
