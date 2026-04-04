#!/usr/bin/env bash
# auto-clean.sh — Downloads定常クリーンアップ
# rules.yamlの自動削除・自動移動ルールをシェルで実行する。
# 対話が必要なもの（mp3リネーム、未マッチファイル）はスキップしてリストだけ返す。
set -euo pipefail

DL=~/Downloads
deleted=0
moved=0
remaining=()

for f in "$DL"/*; do
  [ -e "$f" ] || continue
  name="$(basename "$f")"

  # 隠しファイル・docsディレクトリはスキップ
  [[ "$name" == .* ]] && continue
  [[ "$name" == "docs" && -d "$f" ]] && continue

  handled=false

  # === 自動削除ルール ===
  case "$name" in
    tasmate-*.dump)                          rm -rf "$f"; ((++deleted)); handled=true ;;
    reaper*_linux_x86_64*)                   rm -rf "$f"; ((++deleted)); handled=true ;;
    *Songsterr*)                             rm -rf "$f"; ((++deleted)); handled=true ;;
    *diatonic_chords*|*seventh_chords*|*fretboard_notes*)
                                             rm -f  "$f"; ((++deleted)); handled=true ;;
    *baibai*|*デビットカード*)                rm -f  "$f"; ((++deleted)); handled=true ;;
    202*-DICH-*.pdf|202*-DNP-*.pdf)          rm -f  "$f"; ((++deleted)); handled=true ;;
    *license\ cert*.pdf)                     rm -f  "$f"; ((++deleted)); handled=true ;;
    *御見積書*.pdf)                           rm -f  "$f"; ((++deleted)); handled=true ;;
  esac
  $handled && continue

  # === 自動移動ルール ===
  ext="${name##*.}"
  ext_lower="$(echo "$ext" | tr '[:upper:]' '[:lower:]')"
  case "$ext_lower" in
    png|jpg|jpeg|gif|webp)
      mkdir -p ~/Pictures
      mv "$f" ~/Pictures/
      ((++moved))
      handled=true
      ;;
  esac
  $handled && continue

  # === 対話が必要 or 未マッチ → 残りリストに追加 ===
  remaining+=("$name")
done

# === レポート出力（JSON） ===
echo "{"
echo "  \"deleted\": $deleted,"
echo "  \"moved\": $moved,"
echo -n "  \"remaining\": ["
first=true
for r in "${remaining[@]+"${remaining[@]}"}"; do
  $first && first=false || echo -n ","
  echo -n "\"$(echo "$r" | sed 's/"/\\"/g')\""
done
echo "]"
echo "}"
