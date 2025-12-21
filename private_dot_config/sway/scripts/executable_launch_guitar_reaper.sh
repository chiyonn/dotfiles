#!/bin/bash

REAPER_MEDIA_DIR="/home/chiyonn/Documents/REAPER Media/"

medias=$(ls "$REAPER_MEDIA_DIR")
song=$(printf "$medias" | wofi --dmenu --prompt "Songs")

[[ -z "$song" ]] && exit 0

reaper "$REAPER_MEDIA_DIR$song" &

notify-send "Guitar Practice" "Starting: $song"
