#!/bin/bash
set -e  # Exit if any command fails

# 2025 AoPS Crawler Script
# Only runs the crawler, skips cleaning step

START_DATE="2025-01"
ITEMS_RAW_PATH="../out/items_raw_2025.jl"

echo "Running 2025 AoPS Crawler with:"
echo "  START_DATE  = $START_DATE"
echo "  OUTPUT      = $ITEMS_RAW_PATH"

# Navigate to the crawler directory
cd aops_crawler || { echo "Directory 'aops_crawler' not found."; exit 1; }

# Create output directory if it doesn't exist
mkdir -p ../out

# Run Scrapy crawler for 2025 data
AOPS_FEED_URI="${ITEMS_RAW_PATH}" scrapy crawl aops \
    --set="ROBOTSTXT_OBEY=False" \
    -a start_date="$START_DATE" \
    -a test_mode="False"

echo "Crawling done! Output saved to: $ITEMS_RAW_PATH"
