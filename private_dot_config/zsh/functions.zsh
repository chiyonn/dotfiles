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

timer() {
  [[ -z $1 ]] && { echo "Invalid arguments: timer [int]"; return 1;}
  local sound="/usr/share/sounds/freedesktop/stereo/alarm-clock-elapsed.oga"
  [[ -f $sound ]] || { echo "No such file: $sound"; return 1; }
  (sleep $1m && notify-send "timer" && paplay $sound) & disown
}

again() {
  eval "$(history | tac | peco | sed -E 's/^\s+[0-9]+\s+//')"
}

edit() {
  cd $(chezmoi source-path)
  chezmoi managed | peco | xargs -I {} chezmoi edit --apply '~/{}'
  cd - > /dev/null
}
