#!/bin/bash
# Auto-monitor and restart crawler until done
# Target: 3600001 -> 3750000, appending to out/items_raw_2025.jl

END_ID=3750000
OUTPUT="out/items_raw_2025.jl"
DELAY=0.2

while true; do
    # Check if crawler is running
    if ! ps aux | grep -q "[c]rawl_2025_simple"; then
        # Get last topic ID from output
        LAST_ID=$(tail -1 "$OUTPUT" | python3 -c "import json,sys; print(json.load(sys.stdin)['topic_id'])" 2>/dev/null)

        if [ -z "$LAST_ID" ]; then
            echo "$(date '+%H:%M:%S') ERROR: Cannot read last topic ID"
            break
        fi

        NEXT_ID=$((LAST_ID + 1))

        if [ "$NEXT_ID" -ge "$END_ID" ]; then
            echo "$(date '+%H:%M:%S') DONE: Reached end ID $END_ID"
            break
        fi

        echo "$(date '+%H:%M:%S') RESTART: Resuming from $NEXT_ID"
        python3 crawl_2025_simple.py --start "$NEXT_ID" --end "$END_ID" --delay "$DELAY" --output "$OUTPUT" &
        sleep 10
    fi

    # Print progress
    TOTAL=$(wc -l < "$OUTPUT")
    NEW=$((TOTAL - 130001))
    TARGET=150000
    PCT=$((NEW * 100 / TARGET))
    echo "$(date '+%H:%M:%S') 進度: ${PCT}% (${NEW}/${TARGET}) | 總行數: ${TOTAL}"

    sleep 60
done

echo "=== 最終統計 ==="
TOTAL=$(wc -l < "$OUTPUT")
ERRORS=$(grep -c '"error_code"' "$OUTPUT" || echo 0)
SUCCESS=$((TOTAL - ERRORS))
echo "總記錄: ${TOTAL} | 成功: ${SUCCESS} | 錯誤: ${ERRORS}"
