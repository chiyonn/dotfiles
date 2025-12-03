#!/bin/bash

LID_PATH="/proc/acpi/button/lid/LID/state"
LAST=""

while true; do
    CURRENT=$(awk '{print $2}' "$LID_PATH")
    if [ "$CURRENT" != "$LAST" ]; then
        if [ "$CURRENT" == "closed" ]; then
            swaymsg output eDP-1 disable
        else
            swaymsg output eDP-1 enable
        fi
        LAST="$CURRENT"
    fi
    sleep 1
done
