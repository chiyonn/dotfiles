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

# Calculate next index with wrap-around
if [ $current_index -eq -1 ]; then
    # Current workspace is empty or not found, go to first non-empty
    next_workspace="${workspaces[0]}"
else
    next_index=$(( (current_index + 1) % ${#workspaces[@]} ))
    next_workspace="${workspaces[$next_index]}"
fi

# Switch to next workspace
aerospace workspace "$next_workspace"