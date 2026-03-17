#!/bin/bash
# Bloomberg日本語ヘッドラインをnotify-sendで通知する
# Source: assets.wor.jp Bloomberg RDF feeds

CACHE_DIR="${XDG_CACHE_HOME:-$HOME/.cache}/bloomberg-notify"
SEEN_FILE="$CACHE_DIR/seen"
mkdir -p "$CACHE_DIR"
touch "$SEEN_FILE"

FEEDS=(
    "markets|マーケット"
    "finance|ファイナンス"
    "international|国際"
    "domestic|国内"
    "overseas|海外"
    "economics|経済"
    "opinion|オピニオン"
    "companies|企業"
)

BASE_URL="https://assets.wor.jp/rss/rdf/bloomberg"
notify_count=0

for entry in "${FEEDS[@]}"; do
    slug="${entry%%|*}"
    label="${entry##*|}"
    url="${BASE_URL}/${slug}.rdf"

    # RDFからtitleを抽出（channel titleを除く）
    titles=$(curl -sf --max-time 10 "$url" \
        | xmllint --xpath '//*[local-name()="item"]/*[local-name()="title"]/text()' - 2>/dev/null)

    [ -z "$titles" ] && continue

    while IFS= read -r title; do
        [ -z "$title" ] && continue
        # 重複チェック（titleのハッシュ）
        hash=$(echo -n "$title" | md5sum | cut -d' ' -f1)
        if ! grep -qF "$hash" "$SEEN_FILE"; then
            echo "$hash" >> "$SEEN_FILE"
            notify-send -a "Bloomberg" -i "stock" "Bloomberg $label" "$title"
            ((notify_count++))
            # 通知が溜まりすぎないよう少し間隔を空ける
            [ "$notify_count" -gt 1 ] && sleep 0.3
        fi
    done <<< "$titles"
done

# 新着があったら1回だけサウンドを鳴らす
if [ "$notify_count" -gt 0 ]; then
    paplay /usr/share/sounds/freedesktop/stereo/window-attention.oga
fi

# seenファイルが肥大化しないよう直近1000件に絞る
if [ "$(wc -l < "$SEEN_FILE")" -gt 1000 ]; then
    tail -500 "$SEEN_FILE" > "$SEEN_FILE.tmp" && mv "$SEEN_FILE.tmp" "$SEEN_FILE"
fi
