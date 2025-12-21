#!/bin/bash

# fcitx5 + mozc installer for Fedora
# This script runs once when chezmoi apply is executed

set -euo pipefail

# Check if we're on Fedora
if ! command -v dnf &> /dev/null; then
    echo "dnf not found, skipping fcitx5-mozc installation (not Fedora?)"
    exit 0
fi

PACKAGES=(
    fcitx5
    fcitx5-mozc
    fcitx5-configtool
    fcitx5-gtk3
    fcitx5-gtk4
    fcitx5-qt
)

# Check if all packages are already installed
MISSING_PACKAGES=()
for pkg in "${PACKAGES[@]}"; do
    if ! rpm -q "$pkg" &> /dev/null; then
        MISSING_PACKAGES+=("$pkg")
    fi
done

if [ ${#MISSING_PACKAGES[@]} -eq 0 ]; then
    echo "fcitx5 and mozc are already installed."
else
    echo "Installing fcitx5 and mozc..."
    echo "Missing packages: ${MISSING_PACKAGES[*]}"

    sudo dnf install -y "${MISSING_PACKAGES[@]}"

    echo "fcitx5 and mozc installed successfully."
    echo "Remember to set environment variables in your shell config:"
    echo "  export GTK_IM_MODULE=fcitx"
    echo "  export QT_IM_MODULE=fcitx"
    echo "  export XMODIFIERS=@im=fcitx"
fi

echo ""
echo "To add custom words, run:"
echo "  /usr/libexec/fcitx5-mozc/mozc_tool --mode=dictionary_tool"
