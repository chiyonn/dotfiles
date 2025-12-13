#!/bin/bash

# Hack Nerd Font installer
# This script runs once when chezmoi apply is executed

set -euo pipefail

FONT_DIR="$HOME/.local/share/fonts"
FONT_NAME="Hack"

# Check if already installed
if fc-list | grep -qi "Hack.*Nerd"; then
    echo "Hack Nerd Font is already installed."
    exit 0
fi

echo "Installing Hack Nerd Font..."

# Create fonts directory if it doesn't exist
mkdir -p "$FONT_DIR"

# Get latest release version from GitHub
LATEST_VERSION=$(curl -s https://api.github.com/repos/ryanoasis/nerd-fonts/releases/latest | grep '"tag_name"' | sed -E 's/.*"([^"]+)".*/\1/')

if [ -z "$LATEST_VERSION" ]; then
    echo "Failed to get latest version, using v3.3.0"
    LATEST_VERSION="v3.3.0"
fi

echo "Downloading Hack Nerd Font $LATEST_VERSION..."

DOWNLOAD_URL="https://github.com/ryanoasis/nerd-fonts/releases/download/${LATEST_VERSION}/Hack.zip"
TEMP_DIR=$(mktemp -d)

curl -fsSL "$DOWNLOAD_URL" -o "$TEMP_DIR/Hack.zip"
unzip -o -q "$TEMP_DIR/Hack.zip" -d "$FONT_DIR"

# Clean up
rm -rf "$TEMP_DIR"

# Refresh font cache
fc-cache -fv

echo "Hack Nerd Font installed successfully."
