#!/bin/bash

# docker installer for Fedora
# This script runs once when chezmoi apply is executed

set -euo pipefail

# Check if we're on Fedora
if ! command -v dnf &> /dev/null; then
    echo "dnf not found, skipping docker installation (not Fedora?)"
    exit 0
fi

DOCKER_REPO_URL=https://download.docker.com/linux/fedora/docker-ce.repo
PACKAGES=(
  docker-ce
  docker-ce-cli
  containerd.io
  docker-compose-plugin
)

if [[ ! -f /etc/yum.repos.d/docker-ce.repo ]]; then
    sudo dnf config-manager addrepo --from-repofile $DOCKER_REPO_URL
fi

# Check if all packages are already installed
MISSING_PACKAGES=()
for pkg in "${PACKAGES[@]}"; do
    if ! rpm -q "$pkg" &> /dev/null; then
        MISSING_PACKAGES+=("$pkg")
    fi
done

if [ ${#MISSING_PACKAGES[@]} -eq 0 ]; then
    echo "packages are already installed."
else
    echo "Installing packages..."
    echo "Missing packages: ${MISSING_PACKAGES[*]}"
    sudo dnf install -y "${MISSING_PACKAGES[@]}"
    echo "packages are installed successfully."
fi

sudo systemctl enable --now docker
sudo usermod -aG docker $USER
echo "Docker installed. Re-login required for group changes."

exit 0
