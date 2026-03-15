#!/bin/bash
# URL抽出スクリプト
# 使い方:
#   extract_url.sh "text with URL"      # 引数から抽出
#   echo "text" | extract_url.sh        # stdinから抽出
#   extract_url.sh --join "text"        # 改行除去してから抽出（PDF等のコピペ用）
#   extract_url.sh --clip               # クリップボードから読み取り→URL抽出→クリップボードに書き戻し（.desktop用）

URL_PATTERN='https?://[A-Za-z0-9._~:/?#\[\]@!$&'"'"'()*+,;=%\-]+'

extract_url() {
  grep -oP "$URL_PATTERN" | head -1
}

extract_url_join() {
  tr -d '\n\r' | extract_url
}

notify() {
  notify-send -a "extract-url" "$1" "$2"
}

if [[ "$1" == "--clip" ]]; then
  input=$(wl-paste 2>/dev/null)
  if [[ -z "$input" ]]; then
    notify "Extract URL" "Clipboard is empty"
    exit 1
  fi
  url=$(echo "$input" | extract_url_join)
  if [[ -n "$url" ]]; then
    echo -n "$url" | wl-copy
    notify "URL extracted" "$url"
  else
    notify "Extract URL" "No URL found"
    exit 1
  fi
elif [[ "$1" == "--join" ]]; then
  shift
  if [[ $# -gt 0 ]]; then
    echo "$*" | extract_url_join
  else
    extract_url_join
  fi
elif [[ $# -gt 0 ]]; then
  echo "$*" | extract_url
else
  extract_url
fi
