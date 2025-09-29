# Quick Edit function
edit() {
  typeset -A EDIT_CONFIGS
  EDIT_CONFIGS=(
    [zshrc]="$HOME/.config/zsh/.zshrc"
    [aliases]="$HOME/.config/zsh/aliases.zsh"
  )
  
  local SOURCE_TAGS=(zshrc aliases)
  
  local tag="$1"
  
  if [[ -z "$tag" ]]; then
    echo "Error: No tag specified" >&2
    echo "Available tags: ${(k)EDIT_CONFIGS[@]}" >&2
    return 1
  fi
  
  if [[ "$tag" == "--help" || "$tag" == "-h" ]]; then
    echo "Quick Edit Tool"
    echo "Usage: edit <tag>"
    echo "Available tags: ${(k)EDIT_CONFIGS[@]}"
    return 0
  fi
  
  local filepath="${EDIT_CONFIGS[$tag]}"
  if [[ -z "$filepath" ]]; then
    echo "Error: Unknown tag: $tag" >&2
    echo "Available tags: ${(k)EDIT_CONFIGS[@]}" >&2
    return 1
  fi
  
  if [[ ! -f "$filepath" ]]; then
    echo "File $filepath does not exist."
    echo -n "Create it? (y/N): "
    read -r response
    if [[ "$response" =~ ^[Yy]$ ]]; then
      local dir=$(dirname "$filepath")
      if [[ ! -d "$dir" ]]; then
        mkdir -p "$dir"
        echo "Created directory: $dir"
      fi
      touch "$filepath"
      echo "Created file: $filepath"
    else
      echo "Cancelled."
      return 1
    fi
  fi
  
  local editor="${EDITOR:-nvim}"
  "$editor" "$filepath"
  
  local exit_code=$?
  if [[ $exit_code -ne 0 ]]; then
    return $exit_code
  fi
  
  # source needed?
  if [[ " ${SOURCE_TAGS[@]} " =~ " ${tag} " ]]; then
    echo "Sourcing $filepath..."
    source "$filepath"
    if [[ $? -eq 0 ]]; then
      echo "✓ Successfully sourced $filepath"
    else
      echo "✗ Failed to source $filepath"
      return 1
    fi
  else
    echo "✓ Successfully saved $filepath"
  fi
}

# zk wrapper function to cd to notebook dir before opening editor
zk() {
  # Check if any of the subcommands will open an editor
  local will_open_editor=false
  local args=("$@")
  
  for arg in "${args[@]}"; do
    case "$arg" in
      edit|new)
        will_open_editor=true
        break
        ;;
    esac
  done
  
  # If interactive flag is present, editor will be opened
  if [[ " ${args[@]} " =~ " -i " ]] || [[ " ${args[@]} " =~ " --interactive " ]]; then
    will_open_editor=true
  fi
  
  if [[ "$will_open_editor" == true ]] && [[ -n "$ZK_NOTEBOOK_DIR" ]]; then
    # Save current directory
    local current_dir=$(pwd)
    
    # Change to notebook directory
    cd "$ZK_NOTEBOOK_DIR"
    
    # Run the actual zk command
    command zk "$@"
    local exit_code=$?
    
    # Return to original directory
    cd "$current_dir"
    
    return $exit_code
  else
    # Run zk command normally if not opening editor or ZK_NOTEBOOK_DIR not set
    command zk "$@"
  fi
}

# todo command - runs task with current directory name as project
todo() {
  local project_name="${PWD##*/}"
  task project:"$project_name" "$@"
}

# task wrapper with auto-sync
task() {
  # Run the actual task command
  command task "$@"
  local result=$?

  # List of read-only commands that don't need sync
  local readonly_cmds=(list ls next ready waiting blocked export stats summary info show reports burndown history ghistory calendar)

  # Check if this is a read-only command
  local should_sync=true
  for cmd in "${readonly_cmds[@]}"; do
    if [[ "$1" == "$cmd" ]]; then
      should_sync=false
      break
    fi
  done

  # Auto sync if not a read-only command
  if [[ "$should_sync" == true && "$1" != "sync" ]]; then
    # Run sync in background to avoid delay
    (command task sync >/dev/null 2>&1 &)
  fi

  return $result
}
