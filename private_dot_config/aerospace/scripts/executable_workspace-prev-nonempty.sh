#!/bin/bash

# Get current workspace
current=$(aerospace list-workspaces --focused)

# Get all non-empty workspaces sorted
workspaces=($(aerospace list-workspaces --monitor focused --empty no | sort -n))

# If no non-empty workspaces, exit
if [ ${#workspaces[@]} -eq 0 ]; then
    exit 0
fi

# Find current workspace index
current_index=-1
for i in "${!workspaces[@]}"; do
    if [ "${workspaces[$i]}" = "$current" ]; then
        current_index=$i
        break
    fi
done

# Calculate previous index with wrap-around
if [ $current_index -eq -1 ]; then
    # Current workspace is empty or not found, go to last non-empty
    prev_workspace="${workspaces[-1]}"
else
    prev_index=$(( (current_index - 1 + ${#workspaces[@]}) % ${#workspaces[@]} ))
    prev_workspace="${workspaces[$prev_index]}"
fi

# Switch to previous workspace
aerospace workspace "$prev_workspace"