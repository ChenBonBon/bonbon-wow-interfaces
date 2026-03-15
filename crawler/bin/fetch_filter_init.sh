#!/bin/sh
set -eu

SCRIPT_DIR="$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)"
CRAWLER_DIR="$(dirname -- "$SCRIPT_DIR")"
HTML_OUTPUT_PATH="outputs/filter_pages/filter-page.html"

cd "$CRAWLER_DIR"

if [ "$#" -ne 1 ]; then
  echo "Usage: ./bin/fetch_filter_init.sh <url>" >&2
  exit 1
fi

python3 -m scripts.fetch_filter_page "$1" "$HTML_OUTPUT_PATH"
python3 -m scripts.extract_filter_init "$HTML_OUTPUT_PATH"
