# Common environment variables for both macOS and Linux

# Editor
export EDITOR=nvim

# Language
export LANG=en_US.UTF-8

# Path additions
export PATH="$HOME/.local/bin:$PATH"
export PATH="$HOME/Private/callot/bin:$PATH"

# ZK notebook directory
# TODO: Migrate to /mnt/nas/notes with NFS (see TODO.md)
export ZK_NOTEBOOK_DIR="/Volumes/notes"

# Homelab server addresses (private network)
export NOMAD_ADDR=http://192.168.40.104:4646
export VAULT_ADDR=http://192.168.40.104:8200
